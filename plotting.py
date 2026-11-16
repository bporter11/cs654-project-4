"""Plots and result-file helpers for the Flappy Bird experiments."""

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def moving_average(values, window=100):
    values = np.asarray(values, dtype=np.float64)
    if len(values) < window:
        return values
    return np.convolve(values, np.ones(window) / window, mode="valid")


def save_results(summary, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as file:
        json.dump(summary, file, indent=2)


def save_learning_curve(runs, configurations, random_score, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    plt.figure(figsize=(5.5, 2.8))

    for label in configurations:
        scores = [run["scores"] for run in runs if run["label"] == label]
        curves = np.array([moving_average(score) for score in scores])
        if curves.size == 0:
            continue
        x = np.arange(curves.shape[1]) + 100
        plt.plot(x, curves.mean(axis=0), label=label)
        plt.fill_between(x, curves.min(axis=0), curves.max(axis=0), alpha=0.2)

    plt.axhline(
        random_score, color="gray", linestyle="--", linewidth=1, label="Random policy"
    )
    plt.xlabel("Training episode")
    plt.ylabel("Pipes passed (100-ep avg)")
    plt.legend(fontsize=7, loc="upper left")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
