from ocatari import OCAtari


class RLLMEnv(OCAtari):
    def __init__(self, env_name, mode="revised", new_reward_func=None, *args, **kwargs):
        super(RLLMEnv, self).__init__(env_name, mode, *args, **kwargs)
        if new_reward_func is None:
            raise ValueError("new_reward_func must be defined")
        self.new_reward_func = new_reward_func
        self._oca_step = self.step
        self.step = self._step_with_lm_reward
        self.org_reward = 0 # only for tracking
    
    def new_reward_func(self):
        raise NotImplementedError

    def _step_with_lm_reward(self, action):
        obs, game_reward, truncated, terminated, info = self._oca_step(action)
        self.org_reward = self.org_reward+game_reward
        info["org_reward"] = self.org_reward

        try:
            reward = self.new_reward_func(self.objects)
        except Exception as e:
            print("Error in new_reward_func: ", e)
            reward = 0
        return obs, reward, truncated, terminated, info

    def reset(self, **kwargs):
        state = super(RLLMEnv, self).reset()
        self.org_reward = 0
        return state
    
def get_reward_function(game: str):
    reward_functions = {}
    module_name = f"context.{game}.reward_function"
    print(module_name)
    return __import__(module_name, fromlist=[''])

    return reward_functions[game]
