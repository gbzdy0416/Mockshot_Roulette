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
            return curbullet[0]  # 0 -> fake -> self, 1 -> real -> opponent
        elif pr_real < 0.5:
            return 0
        else:
            return 1


class RandomPlayer(Player):
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def decide(self, state):
        return self.rng.randint(0, 3)


class TBaselinePlayer(Player):
    def __init__(self, t_shoot=0.5, t_reveal = 0.5):
        self.t_shoot = t_shoot
        self.t_reveal = t_reveal
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
        elif reveal > 0 and curbullet[1] == 0 and abs(pr_real - 0.5) <= self.t_reveal:
            return 3
        elif curbullet[1] == 1:
            return curbullet[0]  # 0 -> fake -> self, 1 -> real -> opponent
        elif pr_real < self.t_shoot:
            return 0
        else:
            return 1
