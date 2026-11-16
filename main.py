"""Command-line entry point for the modular Flappy Bird project."""

import argparse
import json

from argument import add_arguments
from experiments import run_experiments


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="CS 654 Project 4: Q-learning for Flappy Bird"
    )
    return add_arguments(parser).parse_args()


def main():
    args = parse_arguments()
    summary = run_experiments(
        episodes=args.episodes,
        seeds=args.seeds,
        eval_episodes=args.eval_episodes,
        workers=args.workers,
        output_dir=args.output_dir,
        check_environment=not args.skip_check,
        render_heuristic=args.render,
        record_video=args.record_video,
        video_dir=args.video_dir,
        video_episodes=args.video_episodes,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
