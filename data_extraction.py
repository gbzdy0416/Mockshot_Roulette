import game
from baseline_player import BaselinePlayer, TBaselinePlayer, RandomPlayer
import random

player_pool = [BaselinePlayer(), TBaselinePlayer(0.3, 0.3, 0.7), TBaselinePlayer(),
               TBaselinePlayer(0, 0.7, 0.3), RandomPlayer()]
import numpy as np


def collect_data(players, rounds=200000, seed=92122):
    features = []
    strategies = []
    rng = random.Random(seed)
    for i in range(rounds):
        player1, player2 = rng.choices(players, k=2)
        state = game.init_game(seed=rng.randint(0, 100000), real=rng.randint(1,10),
                               fake=rng.randint(1,10), heal=rng.randint(0,2),
                               reveal=rng.randint(0,2),
                               damage_per_shot=int(100 / rng.randint(2,10))+1,
                               skip_round=rng.randint(0,2), skip_bullet=rng.randint(0,2),
                               double=rng.randint(0,2))
        res, _, f, s = game.run_game(state, player1, player2)
        winner = 1 if res < 0 else 0
        features.extend(f[winner])
        strategies.extend(s[winner])
    return features, strategies


X_all, y_all = collect_data(players=player_pool)
X_np = np.array(X_all, dtype=np.float32)
y_np = np.array(y_all, dtype=np.int64)
counts = np.bincount(y_np, minlength=4)
print(counts, counts / counts.sum())
print(len(X_np))
np.savez("data/dataset_v1.npz", X=X_np, y=y_np)
