from ocatari import OCAtari  # type: ignore
import numpy as np


class ReSLLMEnv(OCAtari):
    """
    OCAtari environment wrapper to use LLM-generated reward functions.
    The reward function must take (objects) as input.
    """

    def __init__(self, env_name, reward_func, mode="revised", *args, **kwargs):
        super().__init__(env_name, mode=mode, *args, **kwargs)
        if not callable(reward_func):
            raise ValueError("reward_func must be a callable accepting objects")
        self.reward_func = reward_func
        self.org_return = 0
        self._oca_step = self.step
        self.step = self._step_with_custom_reward

    def _step_with_custom_reward(self, action):
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

    def reset(self, **kwargs):
        obs, info = super().reset(**kwargs)
        self.org_return = 0
        return obs, info


def run_episodes(env, num_episodes=5, max_steps=5000, render=False, verbose=False):
    """
    Runs num_episodes using the provided RLLMEnv.
    Returns:
    - rewards: list of total rewards per episode
    - errors: list of errors encountered (None if no error for that episode)
    """
    rewards, errors = [], []

    for ep in range(num_episodes):
        total_reward, error = 0, None
        obs, info = env.reset()
        for _ in range(max_steps):
            action = env.env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            if "reward_error" in info:
                error = info["reward_error"]
                break
            if terminated or truncated:
                break
            if render:
                env.render()
        rewards.append(total_reward)
        errors.append(error)
        if verbose:
            print(f"Episode {ep+1}: Reward={total_reward} | Error={error}")

    return rewards, errors
