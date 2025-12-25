import random
import game
import copy
class BaselinePlayer(game.Player):
    def decide(self, state):
        curhp = state["hp"][state["turn"]]
        heal = state["heal_left"][state["turn"]]
        reveal = state["reveal_left"][state["turn"]]
        d = state["damage_per_shot"]
        maxhp = state["max_hp"]
        pr_real = state["Left_real"] / (state["Left_fake"] + state["Left_real"] + 10 ** -10)
        curbullet = state["chamber"][state["pos"]]
        if heal > 0 and maxhp - curhp >= d:
            return 2
        elif reveal > 0 and curbullet[1] == 0:
            return 3
        elif curbullet[1] == 1:
            if state["double_left"][state["turn"]] > 0 and state["double_mark"] == 0 and curbullet[0] == 1:
                return 4
            return curbullet[0]  # 0 -> fake -> self, 1 -> real -> opponent
        elif state["skip_round_left"][state["turn"]] > 0 and state["skip_round_mark"] == 0:
            return 5
        elif state["skip_bullet_left"][state["turn"]] > 0:
            return 6
        elif pr_real < 0.5:
            return 0
        else:
            if state["double_left"][state["turn"]] > 0 and state["double_mark"] == 0:
                return 4
            return 1


class RandomPlayer(game.Player):
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def decide(self, state):
        return self.rng.randint(0, 6)


class TBaselinePlayer(game.Player):
    def __init__(self, t_shoot=0.5, t_reveal = 0.5, t_use = 0.5):
        self.t_shoot = t_shoot
        self.t_reveal = t_reveal
        self.t_use = t_use
    def decide(self, state):
        curhp = state["hp"][state["turn"]]
        heal = state["heal_left"][state["turn"]]
        reveal = state["reveal_left"][state["turn"]]
        d = state["damage_per_shot"]
        maxhp = state["max_hp"]
        pr_real = state["Left_real"] / (state["Left_fake"] + state["Left_real"] + 10 ** -10)
        curbullet = state["chamber"][state["pos"]]
        uncertainty = abs(pr_real - 0.5)
        if heal > 0 and maxhp - curhp >= d:
            return 2
        elif reveal > 0 and curbullet[1] == 0 and uncertainty <= self.t_reveal:
            return 3
        elif curbullet[1] == 1:
            if state["double_left"][state["turn"]] > 0 and state["double_mark"] == 0 and curbullet[0] == 1:
                return 4
            return curbullet[0]  # 0 -> fake -> self, 1 -> real -> opponent
        elif state["skip_round_left"][state["turn"]] > 0 and state["skip_round_mark"] == 0 and uncertainty < self.t_use:
            return 5
        elif state["skip_bullet_left"][state["turn"]] > 0 and uncertainty < self.t_use:
            return 6
        elif pr_real < self.t_shoot:
            return 0
        else:
            if state["double_left"][state["turn"]] > 0 and state["double_mark"] == 0:
                return 4
            return 1

class RolloutPlayer(game.Player):
    """
    One-step rollout search:
    - For each candidate action a, apply a to a deepcopy(state)
    - Then finish the game with fixed rollout policies for both sides
    - Choose a with best average outcome over N rollouts
    """
    def __init__(self, n_rollouts=20, seed=0, rollout_policy=None):
        self.n_rollouts = int(n_rollouts)
        self.rng = random.Random(seed)

        # Default rollout policy: a moderately sensible threshold heuristic
        self.rollout_policy = rollout_policy if rollout_policy is not None else \
            __import__("baseline_player").TBaselinePlayer(t_shoot=0.6, t_reveal=0.25, t_use=0.4)

    def decide(self, state):
        player_id = state["turn"]
        legal = legal_actions(state)

        best_a = legal[0]
        best_v = -1e18
        base_seed = self.rng.randint(0, 10**9)

        for a in legal:
            v = 0.0
            for k in range(self.n_rollouts):
                st = copy.deepcopy(state)
                apply_action(st, a)

                p0 = self.rollout_policy
                p1 = self.rollout_policy
                res, _, _, _ = game.run_game(st, p0, p1)

                v += res if player_id == 0 else -res

            v /= self.n_rollouts
            if v > best_v:
                best_v = v
                best_a = a

        return best_a


def legal_actions(state):
    turn = state["turn"]
    acts = [0, 1]

    if state["heal_left"][turn] > 0 and state["hp"][turn] < state["max_hp"]:
        acts.append(2)
    if state["reveal_left"][turn] > 0 and state["chamber"][state["pos"]][1] == 0:
        acts.append(3)
    if state["double_left"][turn] > 0 and state["double_mark"] == 0:
        acts.append(4)
    if state["skip_round_left"][turn] > 0 and state["skip_round_mark"] == 0:
        acts.append(5)
    if state["skip_bullet_left"][turn] > 0 and state["pos"] + 1 <= len(state["chamber"]):
        acts.append(6)

    return acts


def apply_action(state, action):
    if action == 0:
        game.shot(state, 0)
    elif action == 1:
        game.shot(state, 1)
    elif action == 2:
        game.use_heal(state)
    elif action == 3:
        game.use_reveal(state)
    elif action == 4:
        game.use_double(state)
    elif action == 5:
        game.use_skip_round(state)
    elif action == 6:
        game.use_skip_bullet(state)
    else:
        game.illegal_penalty(state)