"""Project-level environment wrapper.

This gives the rest of the project a small interface similar to the course
Atari project while keeping the actual Flappy Bird mechanics in
``flappy_bird_env.py``.
"""

import numpy as np

from flappy_bird_env import FlappyBirdEnv


class Environment:
    """Wrapper exposing the action and observation spaces used by the agent."""

    def __init__(self, reward_mode="sparse", max_steps=3000, render_mode=None):
        self.env = FlappyBirdEnv(
            reward_mode=reward_mode,
            max_steps=max_steps,
            render_mode=render_mode,
        )
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space

    def reset(self, seed=None):
        observation, info = self.env.reset(seed=seed)
        return np.asarray(observation, dtype=np.float32), info

    def step(self, action):
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action: {action}")
        observation, reward, terminated, truncated, info = self.env.step(action)
        return (
            np.asarray(observation, dtype=np.float32),
            reward,
            terminated,
            truncated,
            info,
        )

    def get_action_space(self):
        return self.action_space

    def get_observation_space(self):
        return self.observation_space

    def get_random_action(self):
        return self.action_space.sample()

    def close(self):
        self.env.close()
