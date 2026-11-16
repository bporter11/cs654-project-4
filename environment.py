"""Project-level environment wrapper.

This gives the rest of the project a small interface similar to the course
Atari project while keeping the actual Flappy Bird mechanics in
``flappy_bird_env.py``.
"""

import numpy as np
import gymnasium as gym

from flappy_bird_env import FlappyBirdEnv


class Environment:
    """Wrapper exposing the action and observation spaces used by the agent."""

    def __init__(
        self,
        reward_mode="sparse",
        max_steps=3000,
        render_mode=None,
        video_folder=None,
        video_prefix="flappy_bird",
        video_episodes=0,
    ):
        base_render_mode = "rgb_array" if video_folder else render_mode
        self.env = FlappyBirdEnv(
            reward_mode=reward_mode,
            max_steps=max_steps,
            render_mode=base_render_mode,
        )
        if video_folder:
            self.env = gym.wrappers.RecordVideo(
                self.env,
                video_folder=video_folder,
                name_prefix=video_prefix,
                episode_trigger=lambda episode_id: episode_id < int(video_episodes),
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
