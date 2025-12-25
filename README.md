# Mockshot Roulette: a controlled decision-making benchmark inspired from the game "Buckshot Roulette".
Mockshot Roulette is a controlled two-player decision-making benchmark inspired by the game "Buckshot Roulette".
The benchmark is designed to study decision robustness under partial observability, non-linear action interactions, and limited resources.

Rather than optimizing for a single learning algorithm, the benchmark focuses on evaluating how different inductive biases perform under identical evaluation protocols.

---

## Overview

We design a two-player, turn-based game environment with the following characteristics:

- **Partial observability**: the true state of future actions is only partially revealed
- **Information-gathering actions**: agents may spend limited resources to reduce uncertainty
- **Risk–reward trade-offs**: actions may benefit either the agent or the opponent depending on hidden state
- **Resource constraints**: healing and information actions are available in limited quantities

The environment serves as a benchmark to evaluate decision-making policies trained from heuristic-generated data.

---

## Environment

Each episode consists of a finite sequence of actions drawn from a hidden binary state (e.g., risky vs. safe outcomes).  
At each turn, an agent chooses one of the following discrete actions:

| ID | Action | Description |
|----|-------|-------------|
| 0 | Shoot self | Fire the current bullet at self |
| 1 | Shoot opponent | Fire the current bullet at opponent |
| 2 | Heal | Restore health (limited resource) |
| 3 | Reveal | Reveal the current bullet |
| 4 | Double | Double damage of current bullet |
| 5 | Skip round | Skip opponent’s next turn |
| 6 | Skip bullet | Skip the current bullet |
| 7 | Random reveal | Reveal a random bullet |


The game terminates when either agent’s health reaches zero or when all actions are exhausted.  
The final reward is defined as the health difference between the two agents.

### Observations and Information Structure

The game is partially observable.
- Public information includes remaining bullets, both players’ health, and item counts.
- Private information includes outcomes revealed via reveal or random reveal actions.
- The true order of unrevealed bullets is hidden from both players.

Agents receive observations derived from public state and their own private information only.

---

## Baseline Policies

We implement multiple heuristic baselines to reflect human-designed strategies:

- **Rule-based Baseline**: deterministic logic using health thresholds and estimated risk
- **Threshold Baselines**: parameterized heuristics controlling aggressiveness and information usage
- **Random Policy**: random action selection
- **Rollout Baselines**: simulate a play with another baseline player to determine its action

Rollout agents are intended as strong planning-based reference policies rather than optimal solutions.

These baselines provide strong, interpretable reference points for evaluation.

---

## Learning Models

We train and evaluate multiple classes of supervised learning models:

- **Logistic Regression** (linear baseline)
- **Random Forests** (tree-based ensemble)
- **Neural Network (MLP)**

Models are trained on state–action pairs collected from self-play among heuristic agents under domain randomization.

---

## Evaluation

All methods evaluated on this benchmark must follow the canonical evaluation protocol below.
### Canonical environment
- real=fake=5
- damage=34
- items=1

### Evaluation
- games=10000
- begin with randomly chosen player
- seed=92122

### Offline Evaluation
- Multi-class action prediction accuracy
- Precision / recall / F1-score per action

### Online Evaluation
- Head-to-head games against heuristic baselines
- Metrics include:
    - Wining rate
    - Average health difference
    - Illegal action rate (Should be 0 for every player except random player)

All evaluations are conducted under a canonical game setting for fair comparison.

### Expected Results (Canonical Setting)

All results are averaged over 10,000 games with randomized starting player.

| Method           | Win Rate vs Baseline | Draw Rate | Avg Score |
|------------------|----------------------|-----------|-----------|
| Baseline         | ~0.40                | ~0.16     | ≈ 0       |
| Random           | ~0.07                | ~0.04     | << 0      |
| Logistic Reg. BC | ~0.34                | ~0.12     | < 0       |
| MLP BC           | ~0.32                | ~0.11     | < 0       |
| TBaseline (0.7)  | ~0.28                | ~0.14     | < 0       |
| Rollout (n=5)    | ~0.81                | ~0.01     | > 0       |
| Rollout (n=10)   | ~0.82                | ~0.01     | > 0       |

### Performance Against Planning-Based Agents

| Method           | Win Rate vs Rollout (n=5) |
|------------------|---------------------------|
| Random           | ~0.003                    |
| Logistic Reg. BC | ~0.12                     |
| MLP BC           | ~0.11                     |
| Rollout (n=5)    | ~0.48                     |
| Rollout (n=10)   | ~0.49                     |

---

## Repository Structure
.\
├── game.py                # Game environment and mechanics \
├── baseline_player.py     # Heuristic baseline agents\
├── train_and_eval.py      # Training and evaluation pipeline\
├── data/                  # Collected training data will be saved here\
├── models/                # Trained models will be saved here\
└── README.md

---

## How to Use
1. Install Dependencies via
`pip install -r requirements.txt`.
2. Use `python data_extraction.py` to generate training data.
3. Use `python train_models.py` to train and evaluate a model. You can change the global variable `MODEL` to switch from models.
4. Extending the Project
   -Add new heuristic baselines by subclassing Player\
   -Add new models by extending build_model() in train_and_eval.py\
   -Modify environment dynamics in game.py to study alternative decision settings