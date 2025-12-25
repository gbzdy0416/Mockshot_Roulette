import game
from baseline_player import TBaselinePlayer, RandomPlayer, RolloutPlayer
import random
from tqdm.auto import tqdm
import numpy as np


def build_player_pool(n_tbase, seed):
    rng = random.Random(seed)
    players = [RolloutPlayer(n_rollouts=n+1, rollout_policy=TBaselinePlayer(0.6, 0.25, 0.4), seed=seed+n)
           for n in range(20)]
    players.extend([RandomPlayer(seed + i) for i in range(int(n_tbase/100) + 3)])
    for _ in tqdm(range(n_tbase), desc="Generating Players"):
        t_shoot = rng.random()
        t_reveal = rng.random() * 0.5
        t_use = rng.random()
        players.append(TBaselinePlayer(t_shoot, t_reveal, t_use))

    return players


def collect_data(players, rounds=200000, seed=92122):
    features = []
    strategies = []
    rng = random.Random(seed)
    for i in tqdm(range(rounds), desc="Collecting play data"):
        player1, player2 = rng.choices(players, k=2)
        for begin in range(2):
            state = game.init_game(seed=rng.randint(0, 100000), real=rng.randint(1, 10),
                               fake=rng.randint(1, 10), heal=rng.randint(0, 2),
                               reveal=rng.randint(0, 2),
                               damage_per_shot=int(100 / rng.randint(2, 10)) + 1,
                               skip_round=rng.randint(0, 2), skip_bullet=rng.randint(0, 2),
                               double=rng.randint(0, 2), begin=begin)
            res, _, f, s = game.run_game(state, player1, player2)
            winner = 1 if res < 0 else 0
            features.extend(f[winner])
            strategies.extend(s[winner])
            if rng.random() > 0.5 and (not isinstance(player1, RandomPlayer)) and (not isinstance(player2, RandomPlayer)):
                features.extend(f[winner ^ 1])
                strategies.extend(s[winner ^ 1])
    return features, strategies


player_pool = build_player_pool(100, 92122)
X_all, y_all = collect_data(players=player_pool, rounds=50000)
X_np = np.array(X_all, dtype=np.float32)
bad = []
for i, a in enumerate(y_all):
    if not isinstance(a, (int, np.integer)):
        bad.append((i, type(a), a))
        break

print("First bad y:", bad[0] if bad else "None")

y_np = np.array(y_all, dtype=np.int64)
counts = np.bincount(y_np, minlength=8)
print(counts, counts / counts.sum())
print(len(X_np))
np.savez("data/dataset_v1.npz", X=X_np, y=y_np)
