"""Training, evaluation, and pilot-experiment orchestration."""

import os
from multiprocessing import Pool

import numpy as np
from gymnasium.utils.env_checker import check_env

from agent_q_learning import QLearningAgent
from environment import Environment
from flappy_bird_env import FlappyBirdEnv
from plotting import save_learning_curve, save_results


CONFIGURATIONS = {
    "Sparse reward, basic state": ("sparse", "basic"),
    "Sparse reward, expanded state": ("sparse", "expanded"),
    "Shaped reward, basic state": ("shaped", "basic"),
}


def heuristic(observation):
    """Simple controller used as a solvability sanity check."""
    return int(observation[0] > observation[3] + 15)


def evaluate(policy, reward_mode="sparse", episodes=20, seed=10_000, render=False):
    environment = Environment(
        reward_mode=reward_mode,
        render_mode="human" if render else None,
    )
    scores = []
    try:
        for episode in range(int(episodes)):
            observation, _ = environment.reset(seed=seed + episode)
            while True:
                observation, _, terminated, truncated, info = environment.step(
                    policy(observation)
                )
                if terminated or truncated:
                    break
            scores.append(info["score"])
    finally:
        environment.close()
    return float(np.mean(scores))


def train_one(configuration, seed, episodes, eval_episodes):
    label = configuration
    reward_mode, state_representation = CONFIGURATIONS[label]
    environment = Environment(reward_mode=reward_mode)
    agent = QLearningAgent(
        environment,
        state_representation=state_representation,
        alpha=0.1,
        gamma=0.99,
        epsilon_start=0.1,
        seed=seed,
    )
    try:
        scores = agent.train(episodes=episodes, seed=seed)
        eval_mean = evaluate(
            agent.evaluate_action,
            reward_mode=reward_mode,
            episodes=eval_episodes,
        )
        return {
            "label": label,
            "seed": int(seed),
            "scores": scores.tolist(),
            "eval_mean": eval_mean,
            "states": len(agent.q_values),
        }
    finally:
        environment.close()


def _train_one_from_tuple(arguments):
    return train_one(*arguments)


def run_experiments(
    episodes=5000,
    seeds=(0, 1, 2),
    eval_episodes=20,
    workers=1,
    output_dir=".",
    check_environment=True,
    render_heuristic=False,
):
    """Run all pilot configurations and save JSON and PDF outputs."""
    if check_environment:
        check_env(FlappyBirdEnv(), skip_render_check=True)

    random_rng = np.random.default_rng(0)
    random_score = evaluate(
        lambda observation: int(random_rng.integers(2)),
        episodes=eval_episodes,
    )
    heuristic_score = evaluate(
        heuristic,
        episodes=eval_episodes,
        render=render_heuristic,
    )
    print("Environment check passed.")
    print(f"Hand-coded controller score: {heuristic_score:.2f}")

    jobs = [
        (label, seed, episodes, eval_episodes)
        for label in CONFIGURATIONS
        for seed in seeds
    ]
    if workers > 1:
        with Pool(processes=workers) as pool:
            runs = pool.map(_train_one_from_tuple, jobs)
    else:
        runs = [_train_one_from_tuple(job) for job in jobs]

    summary = {"random": random_score, "heuristic": heuristic_score}
    for label in CONFIGURATIONS:
        label_runs = [run for run in runs if run["label"] == label]
        summary[label] = {
            "eval_mean": float(np.mean([run["eval_mean"] for run in label_runs])),
            "eval_per_seed": [run["eval_mean"] for run in label_runs],
            "last500_train_mean": float(
                np.mean([np.mean(run["scores"][-500:]) for run in label_runs])
            ),
            "states": [run["states"] for run in label_runs],
        }

    results_path = os.path.join(output_dir, "results", "pilot.json")
    figure_path = os.path.join(output_dir, "figures", "learning_curve.pdf")
    save_results(summary, results_path)
    save_learning_curve(runs, CONFIGURATIONS, random_score, figure_path)

    print(f"Saved results to {results_path}")
    print(f"Saved learning curve to {figure_path}")
    return summary
