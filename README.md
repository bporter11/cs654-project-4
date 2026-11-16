# Reinforcement Learning for Flappy Bird (CS 654, Project 4)

Team: Brian Porter, Vinayaka Hegde, Sanjana Sasmal, Preston Huynh

`flappy_rl.py` contains everything in one file: a simplified Flappy Bird game, tabular Q-learning, and the pilot experiments reported in the project proposal.

## 1. Install

You need Python 3.11, 3.12, or 3.13. Install the exact package versions used for the proposal:

```bash
pip install numpy==2.4.2 matplotlib==3.10.8 gymnasium==1.4.0 pygame==2.6.1
```

## 2. Run

From the folder that contains `flappy_rl.py`:

```bash
python flappy_rl.py
```

The run takes about 2 minutes on CPU; no GPU is needed. A `pkg_resources is deprecated` warning from Pygame is harmless.

The script does the following:

1. Checks the game with Gymnasium's environment checker, then prints the score of a simple hand-coded controller.
2. Trains Q-learning in 3 configurations: sparse reward with the basic state, sparse reward with the expanded state, and shaped reward with the basic state. Each configuration runs with 3 random seeds for 5,000 episodes.
3. Evaluates each trained agent, and a random policy, on 20 unseen levels.
4. Saves the results.

## 3. Results

The script creates two files next to itself:

- `results/pilot.json`: all numbers. The proposal table uses the `eval_mean` values.
- `figures/learning_curve.pdf`: the learning-curve figure in the proposal.

Everything is seeded, so you should get exactly these values:

| Configuration | Pipes passed (`eval_mean`) |
|---|---|
| Random policy | 0.0 |
| Sparse reward, basic state | 27.95 (28.0 in the proposal) |
| Sparse reward, expanded state | 0.38 (0.4) |
| Shaped reward, basic state | 1.32 (1.3) |

The hand-coded controller scores 45.4. Episodes are capped at 59 pipes.

## Optional: watch the game

```python
from flappy_rl import FlappyBirdEnv
env = FlappyBirdEnv(render_mode="human")
obs, _ = env.reset(seed=0)
done = False
while not done:
    obs, r, term, trunc, _ = env.step(int(obs[0] > obs[3] + 15))  # hand-coded controller
    done = term or trunc
```
