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
        "--skip-check", action="store_true", help="skip Gymnasium environment check"
    )
    return parser
