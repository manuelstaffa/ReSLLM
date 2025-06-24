from ocatari import OCAtari
from hackatari import HackAtari
import numpy as np
import subprocess
import os


class ReSLLMEnv(HackAtari):
    """
    OCAtari environment wrapper to use LLM-generated reward functions.
    The reward function must take (objects) as input.
    """

    def __init__(
        self, env_name: str, reward_func: str, mode: str = "revised", *args, **kwargs
    ) -> None:
        super().__init__(
            env_name=f"ALE/{env_name.capitalize()}-v5",
            mode=mode,
            *args,
            **kwargs,
        )
        if not callable(reward_func):
            raise ValueError("reward_func must be a callable accepting objects")
        self.reward_func = reward_func
        self.org_return = 0
        self._oca_step = self.step
        self.step = self._step_with_custom_reward

    def _step_with_custom_reward(
        self, action: int | np.integer
    ) -> tuple[np.ndarray, float, bool, bool, dict]:
        obs, game_reward, terminated, truncated, info = self._oca_step(action)

        if isinstance(game_reward, (int, float, np.integer, np.floating)):
            self.org_return += float(game_reward)

        info["org_return"] = self.org_return
        try:
            reward = self.reward_func(self.objects)
        except Exception as e:
            reward = 0
            info["reward_error"] = str(e)
        return obs, reward, terminated, truncated, info

    def reset(self, **kwargs) -> tuple[np.ndarray, dict]:
        obs, info = super().reset(**kwargs)
        self.org_return = 0
        return obs, info


def run_episodes(
    env: OCAtari,
    num_episodes: int = 5,
    max_steps: int = 5000,
    render: bool = False,
    verbose: bool = False,
) -> tuple[bool, list[float], str]:
    """
    Runs num_episodes using the provided RLLMEnv.
    Returns:
    - rewards: list of total rewards per episode
    - errors: list of errors encountered (None if no error for that episode)
    """
    rewards, errors = [], []
    success = True

    for ep in range(num_episodes):
        total_reward, error = 0, None
        obs, info = env.reset()
        for _ in range(max_steps):
            action = env.env.action_space.sample()  # type: ignore
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward  # type: ignore
            if "reward_error" in info:
                error = info["reward_error"]
                success = False
                break
            if terminated or truncated:
                break
            if render:
                env.render()
        rewards.append(total_reward)
        errors.append(error)
        if verbose:
            print(f"Episode {ep+1}: Reward={total_reward} | Error={error}")

    errors = "\n".join(errors) if errors else ""

    return success, rewards, errors


def import_roms(rom_dir: str) -> None:
    """
    Imports ROMs from the specified directory using ale-import-roms.

    Parameters:
        rom_dir (str): Path to the directory containing ROM files.

    Raises:
        FileNotFoundError: If the ROM directory does not exist.
        ValueError: If the ROM directory is not a directory.
        RuntimeError: If importing ROMs fails.
    """
    if not os.path.exists(rom_dir):
        raise FileNotFoundError(f"ROM directory '{rom_dir}' does not exist.")

    if not os.path.isdir(rom_dir):
        raise ValueError(f"ROM directory '{rom_dir}' is not a directory.")

    try:
        subprocess.run(["ale-import-roms", rom_dir], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "Failed to import ROMs. Ensure 'ale-import-roms' is installed and the ROMs directory is correct."
        ) from e
