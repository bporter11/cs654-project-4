"""Tabular Q-learning for a simplified Flappy Bird.

Run:  python flappy_rl.py
Trains 3 configurations x 3 seeds (5,000 episodes each), evaluates each greedy policy
on 20 unseen levels, and writes results/pilot.json and figures/learning_curve.pdf.
"""
import json, os
from collections import defaultdict
from multiprocessing import Pool
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils.env_checker import check_env
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- Game ----------------
WIDTH, HEIGHT = 288, 400          # play area in pixels (ground at y = HEIGHT)
BIRD_X, BIRD_R = 60, 12
GRAVITY, FLAP_VEL, MAX_VEL = 1.0, -9.0, 10.0
PIPE_W, GAP, PIPE_SPEED, PIPE_SPACING = 52, 100, 3, 150
GAP_MIN, GAP_MAX = 100, 300       # range of gap centers


class FlappyBirdEnv(gym.Env):
    """Observation: [bird_y, bird_vel, dx_next, gap_y_next, gap_y_after]. Actions: 0 = nothing, 1 = flap.
    Sparse reward: +1 per pipe, -1 on crash. Shaped: plus up to 0.1 per frame for staying near the gap center."""
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, reward_mode="sparse", max_steps=3000, render_mode=None):
        self.reward_mode, self.max_steps, self.render_mode = reward_mode, max_steps, render_mode
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(
            low=np.array([0, -MAX_VEL, 0, GAP_MIN, GAP_MIN], dtype=np.float32),
            high=np.array([HEIGHT, MAX_VEL, WIDTH + PIPE_SPACING, GAP_MAX, GAP_MAX], dtype=np.float32))
        self.screen = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.bird_y, self.bird_vel = HEIGHT / 2, 0.0
        self.pipes = [[WIDTH + i * PIPE_SPACING, self._new_gap()] for i in range(3)]
        self.score, self.steps = 0, 0
        return self._obs(), {"score": 0}

    def step(self, action):
        self.bird_vel = FLAP_VEL if action == 1 else min(self.bird_vel + GRAVITY, MAX_VEL)
        self.bird_y += self.bird_vel
        self.steps += 1

        reward = 0.0
        for p in self.pipes:
            prev_right = p[0] + PIPE_W
            p[0] -= PIPE_SPEED
            if prev_right >= BIRD_X - BIRD_R > p[0] + PIPE_W:
                self.score += 1
                reward += 1.0
        if self.pipes[0][0] + PIPE_W < 0:
            self.pipes.pop(0)
            self.pipes.append([self.pipes[-1][0] + PIPE_SPACING, self._new_gap()])

        terminated = self._crashed()
        if terminated:
            reward = -1.0
        elif self.reward_mode == "shaped":
            reward += 0.1 * max(0.0, 1 - abs(self.bird_y - self._next_pipes()[0][1]) / GAP)
        if self.render_mode == "human":
            self.render()
        return self._obs(), reward, terminated, self.steps >= self.max_steps, {"score": self.score}

    def _new_gap(self):
        return float(self.np_random.uniform(GAP_MIN, GAP_MAX))

    def _next_pipes(self):
        ahead = [p for p in self.pipes if p[0] + PIPE_W >= BIRD_X - BIRD_R]
        return ahead[0], ahead[1]

    def _obs(self):
        nxt, after = self._next_pipes()
        return np.array([self.bird_y, self.bird_vel, nxt[0] + PIPE_W - BIRD_X, nxt[1], after[1]],
                        dtype=np.float32)

    def _crashed(self):
        if self.bird_y + BIRD_R >= HEIGHT or self.bird_y - BIRD_R <= 0:
            return True
        return any(x - BIRD_R < BIRD_X < x + PIPE_W + BIRD_R and abs(self.bird_y - gap_y) > GAP / 2 - BIRD_R
                   for x, gap_y in self.pipes)

    def render(self):
        import pygame
        if self.screen is None:
            pygame.init()
            self.screen, self.clock = pygame.display.set_mode((WIDTH, HEIGHT + 40)), pygame.time.Clock()
        s = self.screen
        s.fill((135, 206, 235))
        pygame.draw.rect(s, (222, 184, 135), (0, HEIGHT, WIDTH, 40))
        for x, gap_y in self.pipes:
            pygame.draw.rect(s, (34, 139, 34), (x, 0, PIPE_W, gap_y - GAP / 2))
            pygame.draw.rect(s, (34, 139, 34), (x, gap_y + GAP / 2, PIPE_W, HEIGHT - gap_y - GAP / 2))
        pygame.draw.circle(s, (255, 215, 0), (BIRD_X, int(self.bird_y)), BIRD_R)
        pygame.event.pump()
        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])


# ---------------- Q-learning ----------------
def discretize(obs, state_rep="basic"):
    """Basic: (dx, dy, vel) bins. Expanded adds the height change to the following gap."""
    bird_y, vel, dx, gap_y, gap_after = obs
    s = (int(dx // 10), int(np.clip(bird_y - gap_y, -150, 150) // 10), int(vel))
    if state_rep == "expanded":
        s += (int(np.clip(gap_after - gap_y, -200, 200) // 25),)
    return s


def train(reward_mode, state_rep, episodes, seed, alpha=0.1, gamma=0.99, eps_start=0.1):
    rng = np.random.default_rng(seed)
    env = FlappyBirdEnv(reward_mode=reward_mode)
    Q = defaultdict(lambda: np.zeros(2))
    scores = []
    for ep in range(episodes):
        eps = eps_start * max(0.0, 1 - ep / (episodes / 2))
        obs, _ = env.reset(seed=seed * 100_000 + ep)
        s = discretize(obs, state_rep)
        while True:
            a = int(rng.integers(2)) if rng.random() < eps else int(np.argmax(Q[s]))
            obs, r, term, trunc, info = env.step(a)
            s2 = discretize(obs, state_rep)
            Q[s][a] += alpha * ((r if term else r + gamma * Q[s2].max()) - Q[s][a])
            s = s2
            if term or trunc:
                break
        scores.append(info["score"])
    return Q, np.array(scores)


def evaluate(policy, episodes=20, seed=10_000):
    """Mean pipes passed for a policy (obs -> action) on unseen levels."""
    env, scores = FlappyBirdEnv(), []
    for ep in range(episodes):
        obs, _ = env.reset(seed=seed + ep)
        while True:
            obs, _, term, trunc, info = env.step(policy(obs))
            if term or trunc:
                break
        scores.append(info["score"])
    return float(np.mean(scores))


# ---------------- Pilot experiments ----------------
EPISODES, SEEDS = 5000, [0, 1, 2]
CONFIGS = {"Sparse reward, basic state": ("sparse", "basic"),
           "Sparse reward, expanded state": ("sparse", "expanded"),
           "Shaped reward, basic state": ("shaped", "basic")}


def heuristic(obs):
    return int(obs[0] > obs[3] + 15)   # flap when 15 px below the gap center


def run(args):
    label, seed = args
    reward_mode, state_rep = CONFIGS[label]
    Q, scores = train(reward_mode, state_rep, EPISODES, seed)
    return label, scores, evaluate(lambda obs: int(np.argmax(Q[discretize(obs, state_rep)]))), len(Q)


if __name__ == "__main__":
    check_env(FlappyBirdEnv(), skip_render_check=True)
    print("Environment check passed. Hand-coded controller score:", evaluate(heuristic))

    with Pool(len(CONFIGS) * len(SEEDS)) as pool:
        runs = pool.map(run, [(l, s) for l in CONFIGS for s in SEEDS])

    rng = np.random.default_rng(0)
    summary = {"random": evaluate(lambda obs: int(rng.integers(2))), "heuristic": evaluate(heuristic)}
    plt.figure(figsize=(5.5, 2.8))
    for label in CONFIGS:
        rs = [r for r in runs if r[0] == label]
        curves = np.array([np.convolve(r[1], np.ones(100) / 100, mode="valid") for r in rs])
        x = np.arange(curves.shape[1]) + 100
        plt.plot(x, curves.mean(0), label=label)
        plt.fill_between(x, curves.min(0), curves.max(0), alpha=0.2)
        summary[label] = {"eval_mean": float(np.mean([r[2] for r in rs])), "eval_per_seed": [r[2] for r in rs],
                          "last500_train_mean": float(np.mean([r[1][-500:].mean() for r in rs])),
                          "states": [r[3] for r in rs]}
    plt.axhline(summary["random"], color="gray", ls="--", lw=1, label="Random policy")
    plt.xlabel("Training episode")
    plt.ylabel("Pipes passed (100-ep avg)")
    plt.legend(fontsize=7, loc="upper left")
    plt.tight_layout()
    os.makedirs("figures", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    plt.savefig("figures/learning_curve.pdf")
    with open("results/pilot.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
