# Mockshot Roulette: a controlled decision-making benchmark inspired from the game "Buckshot Roulette".
This repository contains a controlled decision-making benchmark where agents operate under partial observability and must balance risky actions, information acquisition, and limited resources.  
The project investigates whether learning-based policies can systematically outperform human-designed heuristics in such settings.

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
At each turn, an agent chooses one of four actions:

- **Shoot self**
- **Shoot opponent**
- **Heal** (resource-limited)
- **Reveal** the current hidden state (resource-limited)

The game terminates when either agent’s health reaches zero or when all actions are exhausted.  
The final reward is defined as the health difference between the two agents.

---

## Baseline Policies

We implement multiple heuristic baselines to reflect human-designed strategies:

- **Rule-based Baseline**: deterministic logic using health thresholds and estimated risk
- **Threshold Baselines**: parameterized heuristics controlling aggressiveness and information usage
- **Random Policy**: random action selection

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

We evaluate learned policies using two complementary protocols:

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