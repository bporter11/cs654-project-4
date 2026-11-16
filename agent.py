"""Base agent interface used by the project agents."""


class Agent:
    def __init__(self, env):
        self.env = env

    def make_action(self, observation, test=True):
        """Return an action for an observation."""
        raise NotImplementedError

    def init_game_setting(self):
        """Reset any agent state needed before a new evaluation episode."""
        raise NotImplementedError
