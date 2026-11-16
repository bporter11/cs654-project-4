"""Tabular Q-learning agent for the Flappy Bird environment."""

from collections import defaultdict
import pickle

import numpy as np

from agent import Agent


def discretize(observation, state_representation="basic"):
    """Convert the continuous observation into a tabular state.

    The basic state contains distance, relative height, and velocity bins.
    The expanded state adds the height difference between the next two gaps.
    """
    bird_y, velocity, distance, gap_y, following_gap_y = observation
    state = (
        int(distance // 10),
        int(np.clip(bird_y - gap_y, -150, 150) // 10),
        int(velocity),
    )
    if state_representation == "expanded":
        state += (
            int(np.clip(following_gap_y - gap_y, -200, 200) // 25),
        )
    return state


class QLearningAgent(Agent):
    """Epsilon-greedy tabular Q-learning agent."""

    def __init__(
        self,
        env,
        state_representation="basic",
        alpha=0.1,
        gamma=0.99,
        epsilon_start=0.1,
        seed=0,
    ):
        super().__init__(env)
        if state_representation not in {"basic", "expanded"}:
            raise ValueError("state_representation must be 'basic' or 'expanded'")

        self.state_representation = state_representation
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.epsilon_start = float(epsilon_start)
        self.rng = np.random.default_rng(seed)
        self.q_values = defaultdict(
            lambda: np.zeros(self.env.get_action_space().n, dtype=np.float64)
        )

    def epsilon_for_episode(self, episode, total_episodes):
        decay_denominator = max(1, total_episodes / 2)
        return self.epsilon_start * max(
            0.0, 1.0 - episode / decay_denominator
        )

    def make_action(self, observation, test=True, epsilon=0.0):
        state = discretize(observation, self.state_representation)
        if not test and self.rng.random() < epsilon:
            return int(self.rng.integers(self.env.get_action_space().n))
        return int(np.argmax(self.q_values[state]))

    def init_game_setting(self):
        """Q-learning has no per-episode evaluation state to reset."""

    def train_episode(self, episode, total_episodes, seed):
        epsilon = self.epsilon_for_episode(episode, total_episodes)
        observation, _ = self.env.reset(seed=seed)
        state = discretize(observation, self.state_representation)
        steps = 0

        while True:
            action = self.make_action(observation, test=False, epsilon=epsilon)
            observation, reward, terminated, truncated, info = self.env.step(action)
            next_state = discretize(observation, self.state_representation)

            target = reward
            if not terminated:
                target += self.gamma * self.q_values[next_state].max()
            self.q_values[state][action] += self.alpha * (
                target - self.q_values[state][action]
            )

            state = next_state
            steps += 1
            if terminated or truncated:
                return info["score"], steps

    def train(self, episodes, seed):
        scores = []
        for episode in range(int(episodes)):
            score, _ = self.train_episode(
                episode=episode,
                total_episodes=episodes,
                seed=seed * 100_000 + episode,
            )
            scores.append(score)
        return np.asarray(scores, dtype=np.float64)

    def evaluate_action(self, observation):
        return self.make_action(observation, test=True)

    def save(self, path):
        with open(path, "wb") as file:
            pickle.dump(
                {
                    "state_representation": self.state_representation,
                    "alpha": self.alpha,
                    "gamma": self.gamma,
                    "epsilon_start": self.epsilon_start,
                    "q_values": dict(self.q_values),
                },
                file,
            )

    def load(self, path):
        with open(path, "rb") as file:
            state = pickle.load(file)
        self.q_values.clear()
        self.q_values.update(state["q_values"])
