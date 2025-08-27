import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

from hackatari import HackAtari  # noqa: E402
import importlib.util  # noqa: E402
import traceback  # noqa: E402
from typing import Tuple, List, Optional  # noqa: E402
import argparse  # noqa: E402
import pygame  # noqa: E402


def _load_reward_function(rewardfunc_path: str):
    spec = importlib.util.spec_from_file_location("reward_function", rewardfunc_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec or loader for {rewardfunc_path}")
    reward_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reward_module)
    return reward_module.reward_function


def run_episodes(
    game: str,
    rewardfunc_path: str,
    num_episodes: int = 10,
    obs_mode: str = "dqn",
) -> Tuple[bool, List[float], Optional[str]]:
    rewards = []
    obss = []
    error = None

    try:
        # reward_fn = _load_reward_function(rewardfunc_path)
        print("Creating HackAtari environment...")
        env = HackAtari(
            env_name=game,
            obs_mode=obs_mode,
            rewardfunc_path=rewardfunc_path,
            render_mode="rgb_array",
            hud=False,
            render_oc_overlay=True,
        )

        pygame.init()

        for ep in range(num_episodes):
            print(f"Running episode {ep + 1}/{num_episodes}...")
            obs, info = env.reset()
            done = False
            episode_reward = 0.0

            while not done:
                action = env.action_space.sample()
                obs, reward, terminated, truncated, info = env.step(action)
                # ram = env.get_ram()
                # obs = env.objects
                # episode_reward += reward_fn(env)
                # env.render(env._state_buffer_rgb[-1])
                obss.append(obs)
                # env.render(env._state_buffer_rgb[-1])  # type: ignore

                episode_reward += reward
                done = terminated or truncated

            print(f"Episode {ep + 1} finished with reward: {episode_reward}")
            rewards.append(episode_reward)

        env.close()
        success = True

    except Exception as e:
        success = False
        error = traceback.format_exc()
        rewards = []
        print(f"An error occurred while running the episodes: {e}")

    return success, rewards, error


def main():
    parser = argparse.ArgumentParser(
        description="Run a HackAtari reward function on a given game."
    )
    parser.add_argument(
        "--game", "-g", type=str, help="Name of the Atari game, e.g., 'seaquest'"
    )
    parser.add_argument(
        "--rewardfunc_path", "-rf", type=str, help="Path to the reward_function.py file"
    )
    parser.add_argument(
        "--num_episodes", "-ne", type=int, default=10, help="Number of episodes to run"
    )
    parser.add_argument(
        "--obs_mode",
        "-obs",
        type=str,
        default="obj",
        choices=["ori", "dqn", "obj"],
        help="Observation mode",
    )

    args = parser.parse_args()

    success, rewards, error = run_episodes(
        game=args.game,
        rewardfunc_path=args.rewardfunc_path,
        num_episodes=args.num_episodes,
        obs_mode=args.obs_mode,
    )

    if success:
        print(f"Success! Rewards over {args.num_episodes} episodes:")
        print(rewards)
    else:
        print(f"An error occurred:\n{error}")


if __name__ == "__main__":
    main()
