"""The simplified Flappy Bird Gymnasium environment.

This module contains only the game mechanics: physics, pipes, collisions,
observations, rewards, and optional Pygame rendering.  Learning code lives in
``agent_q_learning.py`` and experiment code lives in ``experiments.py``.
"""

import os

import numpy as np
import gymnasium as gym
from gymnasium import spaces


WIDTH, HEIGHT = 288, 400
BIRD_X, BIRD_R = 60, 12
GRAVITY, FLAP_VEL, MAX_VEL = 1.0, -9.0, 10.0
PIPE_W, GAP, PIPE_SPEED, PIPE_SPACING = 52, 100, 3, 150
GAP_MIN, GAP_MAX = 100, 300


class FlappyBirdEnv(gym.Env):
    """A small numerical-observation Flappy Bird environment.

    Observation format::

        [bird_y, bird_velocity, distance_to_next_pipe,
         next_gap_y, following_gap_y]

    Actions are ``0`` for no flap and ``1`` for flap.  The environment supports
    sparse rewards and a shaped reward variant for the experiments.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, reward_mode="sparse", max_steps=3000, render_mode=None):
        if reward_mode not in {"sparse", "shaped"}:
            raise ValueError("reward_mode must be 'sparse' or 'shaped'")
        if render_mode not in {None, "human", "rgb_array"}:
            raise ValueError("render_mode must be None, 'human', or 'rgb_array'")

        self.reward_mode = reward_mode
        self.max_steps = int(max_steps)
        self.render_mode = render_mode
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(
            low=np.array([0, -MAX_VEL, 0, GAP_MIN, GAP_MIN], dtype=np.float32),
            high=np.array(
                [HEIGHT, MAX_VEL, WIDTH + PIPE_SPACING, GAP_MAX, GAP_MAX],
                dtype=np.float32,
            ),
        )
        self.screen = None
        self.clock = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.bird_y = HEIGHT / 2
        self.bird_vel = 0.0
        self.pipes = [
            [WIDTH + i * PIPE_SPACING, self._new_gap()] for i in range(3)
        ]
        self.score = 0
        self.steps = 0
        return self._obs(), {"score": 0}

    def step(self, action):
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action: {action}")

        self.bird_vel = (
            FLAP_VEL
            if int(action) == 1
            else min(self.bird_vel + GRAVITY, MAX_VEL)
        )
        self.bird_y += self.bird_vel
        self.steps += 1

        reward = 0.0
        for pipe in self.pipes:
            previous_right = pipe[0] + PIPE_W
            pipe[0] -= PIPE_SPEED
            if previous_right >= BIRD_X - BIRD_R > pipe[0] + PIPE_W:
                self.score += 1
                reward += 1.0

        if self.pipes[0][0] + PIPE_W < 0:
            self.pipes.pop(0)
            self.pipes.append(
                [self.pipes[-1][0] + PIPE_SPACING, self._new_gap()]
            )

        terminated = self._crashed()
        if terminated:
            reward = -1.0
        elif self.reward_mode == "shaped":
            next_gap_y = self._next_pipes()[0][1]
            reward += 0.1 * max(
                0.0, 1 - abs(self.bird_y - next_gap_y) / GAP
            )

        truncated = self.steps >= self.max_steps
        if self.render_mode in {"human", "rgb_array"}:
            self.render()

        return self._obs(), reward, terminated, truncated, {"score": self.score}

    def _new_gap(self):
        return float(self.np_random.uniform(GAP_MIN, GAP_MAX))

    def _next_pipes(self):
        ahead = [
            pipe
            for pipe in self.pipes
            if pipe[0] + PIPE_W >= BIRD_X - BIRD_R
        ]
        return ahead[0], ahead[1]

    def _obs(self):
        next_pipe, following_pipe = self._next_pipes()
        return np.array(
            [
                self.bird_y,
                self.bird_vel,
                next_pipe[0] + PIPE_W - BIRD_X,
                next_pipe[1],
                following_pipe[1],
            ],
            dtype=np.float32,
        )

    def _crashed(self):
        if (
            self.bird_y + BIRD_R >= HEIGHT
            or self.bird_y - BIRD_R <= 0
        ):
            return True

        return any(
            x - BIRD_R < BIRD_X < x + PIPE_W + BIRD_R
            and abs(self.bird_y - gap_y) > GAP / 2 - BIRD_R
            for x, gap_y in self.pipes
        )

    def render(self):
        """Render one frame for a window or for a video recorder."""
        if self.render_mode == "rgb_array" and os.environ.get("DISPLAY") is None:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

        import pygame

        if self.screen is None:
            pygame.init()
            self.screen, self.clock = pygame.display.set_mode(
                (WIDTH, HEIGHT + 40)
            ), pygame.time.Clock()

        screen = self.screen
        screen.fill((135, 206, 235))
        pygame.draw.rect(screen, (222, 184, 135), (0, HEIGHT, WIDTH, 40))
        for x, gap_y in self.pipes:
            pygame.draw.rect(
                screen, (34, 139, 34), (x, 0, PIPE_W, gap_y - GAP / 2)
            )
            pygame.draw.rect(
                screen,
                (34, 139, 34),
                (x, gap_y + GAP / 2, PIPE_W, HEIGHT - gap_y - GAP / 2),
            )
        pygame.draw.circle(
            screen, (255, 215, 0), (BIRD_X, int(self.bird_y)), BIRD_R
        )
        pygame.event.pump()
        pygame.display.flip()

        if self.render_mode == "human":
            self.clock.tick(self.metadata["render_fps"])
            return None

        # Pygame returns (width, height, channels); Gymnasium expects
        # (height, width, channels) in RGB order.
        return np.transpose(pygame.surfarray.array3d(screen), (1, 0, 2))

    def close(self):
        if self.screen is not None:
            import pygame

            pygame.display.quit()
            pygame.quit()
            self.screen = None
            self.clock = None
