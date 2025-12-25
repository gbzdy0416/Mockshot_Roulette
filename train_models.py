import os
import random
from tqdm.auto import tqdm
import joblib
import numpy as np
import game
from baseline_player import BaselinePlayer, TBaselinePlayer, RandomPlayer, RolloutPlayer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

MODEL = "mlp"   # "lr" | "rf" | "mlp"
DATA_PATH = "data/dataset_v1.npz"
MODEL_DIR = "models"
RANDOM_SEED = 81925

EVAL_GAMES = 10000
EVAL_SEED0 = 92122

# Canonical (fixed) environment config for evaluation
CANONICAL_ENV = dict(real=5, fake=5, heal=1, reveal=1, damage_per_shot=34)


class ModelPlayer(game.Player):
    def __init__(self, clf):
        self.clf = clf

    def decide(self, state):
        x = np.array([game.state_to_feature(state)], dtype=np.float32)
        a = self.clf.predict(x)[0]
        return int(a)


def build_model(model_name: str):
    if model_name == "lr":
        return LogisticRegression(
            max_iter=2000,
            n_jobs=-1,
            random_state=RANDOM_SEED,
        )
    if model_name == "rf":
        return RandomForestClassifier(
            n_estimators=150,
            max_depth=14,
            n_jobs=-1,
            random_state=RANDOM_SEED
        )
    if model_name == "mlp":
        return Pipeline([
            ("scaler", StandardScaler()),
            ("mlp", MLPClassifier(
                hidden_layer_sizes=(32, 32),
                alpha=1e-4,
                max_iter=1000,
                early_stopping=True,
                random_state=RANDOM_SEED,
            ))
        ])
    raise ValueError(f"Unknown MODEL: {model_name}")


def train_from_npz(data_path: str, model_name: str):
    data = np.load(data_path)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int64)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=RANDOM_SEED,
        stratify=y
    )

    clf = build_model(model_name)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    print("\n=== Classification report ===")
    print(classification_report(y_test, y_pred, digits=4))

    print("=== Confusion matrix (rows=true, cols=pred) ===")
    print(confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3, 4, 5, 6]))

    return clf

def play_many_games(player0, player1, n_games: int, seed0: int, env_kwargs: dict):
    wins0 = 0
    draws = 0
    total_score = 0.0
    illegal0 = 0
    illegal1 = 0

    for i in tqdm(
            range(n_games),
            desc=f"Eval {player0.__class__.__name__} vs {player1.__class__.__name__}",
            ncols=100
    ):
        st = game.init_game(seed=seed0 + i, **env_kwargs)
        res, final_state, _, _ = game.run_game(st, player0, player1)

        # res = hp0 - hp1
        total_score += res

        if res > 0:
            wins0 += 1
        elif res == 0:
            draws += 1

        illegal0 += final_state["illegal_move"][0]
        illegal1 += final_state["illegal_move"][1]

    win_rate = wins0 / n_games
    draw_rate = draws / n_games
    avg_score = total_score / n_games
    avg_illegal0 = illegal0 / n_games
    avg_illegal1 = illegal1 / n_games

    return {
        "win_rate_p0": win_rate,
        "draw_rate": draw_rate,
        "avg_score(hp0-hp1)": avg_score,
        "avg_illegal_p0": avg_illegal0,
        "avg_illegal_p1": avg_illegal1,
    }


def main():
    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"Loading data from: {DATA_PATH}")
    clf = train_from_npz(DATA_PATH, MODEL)

    model_path = os.path.join(MODEL_DIR, f"policy_{MODEL}.joblib")
    joblib.dump(clf, model_path)
    print(f"\nSaved model to: {model_path}")

    model_player = ModelPlayer(clf)

    # Baselines for evaluation
    baseline = BaselinePlayer()
    rand = RandomPlayer(seed=RANDOM_SEED)
    tbase_1 = TBaselinePlayer(t_shoot=0.5, t_reveal=0.2, t_use=0.3)
    tbase_2 = TBaselinePlayer(t_shoot=0.7, t_reveal=0.2, t_use=0.5)
    r_20 = RolloutPlayer(n_rollouts=20)
    r_10 = RolloutPlayer(n_rollouts=40)
    print("\n==============================")
    print("Evaluation: Canonical setting")
    print("==============================")

    # Control: Baseline vs Baseline should be ~50% win for player0 (up to randomness)
    metrics_mb = play_many_games(model_player, baseline, EVAL_GAMES, EVAL_SEED0 + 100000, CANONICAL_ENV)
    print("\n[Model vs Baseline]")
    print(metrics_mb)

    metrics_mt = play_many_games(model_player, tbase_1, EVAL_GAMES, EVAL_SEED0 + 300000, CANONICAL_ENV)
    print("\n[Model vs TBaseline(0.5,0.2,0.3)]")
    print(metrics_mt)

    metrics_mr = play_many_games(model_player, rand, EVAL_GAMES, EVAL_SEED0 + 400000, CANONICAL_ENV)
    print("\n[Model vs Random]")
    print(metrics_mr)

    metrics_mt2 = play_many_games(model_player, tbase_2, EVAL_GAMES, EVAL_SEED0 + 500000, CANONICAL_ENV)
    print("\n[Model vs TBaseline(0.7,0.2,0.5)]")
    print(metrics_mt2)

    metrics_r20 = play_many_games(model_player, r_20, EVAL_GAMES, EVAL_SEED0 + 500000, CANONICAL_ENV)
    print("\n[Model vs Rollout(n=20)]")
    print(metrics_r20)

    metrics_r10 = play_many_games(model_player, r_10, EVAL_GAMES, EVAL_SEED0 + 500000, CANONICAL_ENV)
    print("\n[Model vs Rollout(n=10)]")
    print(metrics_r10)

    metrics_bb = play_many_games(baseline, baseline, EVAL_GAMES, EVAL_SEED0, CANONICAL_ENV)
    print("\n[Baseline vs Baseline]")
    print(metrics_bb)

    metrics_rr = play_many_games(r_10, r_10, EVAL_GAMES, EVAL_SEED0, CANONICAL_ENV)
    print("\n[Rollout vs Rollout]")
    print(metrics_rr)

if __name__ == "__main__":
    main()