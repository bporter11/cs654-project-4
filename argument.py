"""Command-line arguments for the modular Flappy Bird project."""


def add_arguments(parser):
    parser.add_argument(
        "--episodes", type=int, default=5000, help="training episodes per run"
    )
    parser.add_argument(
        "--eval-episodes", type=int, default=20, help="evaluation episodes"
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[0, 1, 2],
        help="random seeds used for each configuration",
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="parallel experiment workers"
    )
    parser.add_argument(
        "--output-dir", default=".", help="directory for results and figures"
    )
    parser.add_argument(
        "--render", action="store_true", help="watch the hand-coded controller"
    )
    parser.add_argument(
        "--record-video",
        action="store_true",
        help="save evaluation episodes as MP4 files in the videos folder",
    )
    parser.add_argument(
        "--video-episodes",
        type=int,
        default=5,
        help="number of evaluation episodes to record per configuration",
    )
    parser.add_argument(
        "--video-dir",
        default="videos",
        help="directory where recorded videos are saved",
    )
    parser.add_argument(
        "--skip-check", action="store_true", help="skip Gymnasium environment check"
    )
    return parser
