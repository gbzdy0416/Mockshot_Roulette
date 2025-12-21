from game import Player
import random


class BaselinePlayer(Player):
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


class RandomPlayer(Player):
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def decide(self, state):
        return self.rng.randint(0, 6)


class TBaselinePlayer(Player):
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
