import copy
import random
import abc


class Player(metaclass=abc.ABCMeta):
    all_type = 'file'

    @abc.abstractmethod
    def decide(self, state):
        pass


def init_game(seed=42, damage_per_shot=34, real=5, fake=5, heal=1, reveal=1, skip_bullet=1, double=1, skip_round=1, begin=None):
    rng = random.Random(seed)
    chamber = [[1, 0] for _ in range(real)] + [[0, 0] for _ in range(fake)]
    rng.shuffle(chamber)
    state = {
        "chamber": chamber,
        "pos": 0,
        "Left_real": real,
        "Left_fake": fake,
        "hp": [100, 100],
        "max_hp": 100,
        "damage_per_shot": damage_per_shot,
        "heal_left": [heal, heal],
        "reveal_left": [reveal, reveal],
        "skip_bullet_left": [skip_bullet, skip_bullet],
        "skip_round_left": [skip_round, skip_round],
        "double_left": [double, double],
        "skip_round_mark": 0,
        "double_mark": 0,
        "turn": rng.randint(0, 1) if begin is None else begin % 2,
        "illegal_move": [0, 0],
    }
    return state


def use_reveal(state):
    if state["pos"] >= len(state["chamber"]):
        raise Exception("Trying to reveal a bullet out of range... There must be a bug!")
    if state["reveal_left"][state["turn"]] > 0:
        state["chamber"][state["pos"]][1] = 1
        state["reveal_left"][state["turn"]] -= 1
    else:
        illegal_penalty(state)


def use_heal(state):
    if state["heal_left"][state["turn"]] > 0:
        state["hp"][state["turn"]] = min(state["hp"][state["turn"]] + state["damage_per_shot"], state["max_hp"])
        state["heal_left"][state["turn"]] -= 1
    else:
        illegal_penalty(state)

def use_skip_round(state):
    if state["skip_round_left"][state["turn"]] > 0:
        state["skip_round_mark"] = 1
        state["skip_round_left"][state["turn"]] -= 1
    else:
        illegal_penalty(state)

def use_skip_bullet(state):
    if state["skip_bullet_left"][state["turn"]] > 0:
        state["pos"] += 1
        state["skip_bullet_left"][state["turn"]] -= 1
    else:
        illegal_penalty(state)

def use_double(state):
    if state["double_left"][state["turn"]] > 0:
        state["double_mark"] = 1
        state["double_left"][state["turn"]] -= 1
    else:
        illegal_penalty(state)
def game_finish(state):
    hp = state["hp"]
    return -1 if hp[0] <= 0 else 1 if hp[1] <= 0 else 0


def shot(state, goal):
    # goal: 0 to self, 1 to opponent
    if state["pos"] >= len(state["chamber"]):
        raise Exception("Trying to shoot a bullet out of range... There must be a bug!")
    if state["chamber"][state["pos"]][0] == 1:
        state["hp"][state["turn"] ^ goal] -= state["damage_per_shot"] * (state["double_mark"] + 1)
        state["turn"] ^= 1 ^ state["skip_round_mark"]
        state["skip_round_mark"] = 0
        state["Left_real"] -= 1
    else:
        if goal == 1:
            state["turn"] ^= 1 ^ state["skip_round_mark"]
            state["skip_round_mark"] = 0
        state["Left_fake"] -= 1
    state["pos"] += 1
    state["double_mark"] = 0


def check_finish(state):
    if state["hp"][0] <= 0 or state["hp"][1] <= 0 or state["pos"] >= len(state["chamber"]):
        return state["hp"][0] - state["hp"][1]
    else:
        return None  # Continue


def illegal_penalty(state):
    state["hp"][state["turn"]] -= state["damage_per_shot"]
    state["illegal_move"][state["turn"]] += 1
    state["turn"] ^= 1


def run_game(state, player1: Player, player2: Player):
    players = [player1, player2]
    strategy_list = [[],[]]
    state_list = [[],[]]
    while check_finish(state) is None:
        state_list[state["turn"]].append(state_to_feature(state))
        strategy = players[state["turn"]].decide(state)
        strategy_list[state["turn"]].append(strategy)
        if strategy == 0:  # shoot self
            shot(state, 0)
        elif strategy == 1:  # shoot opponent
            shot(state, 1)
        elif strategy == 2:  # heal
            use_heal(state)
        elif strategy == 3:  # reveal
            use_reveal(state)
        elif strategy == 4:  # double
            use_double(state)
        elif strategy == 5:
            use_skip_round(state) # skip round
        elif strategy == 6:
            use_skip_bullet(state) # skip bullet
        else:
            illegal_penalty(state)
    return check_finish(state), state, state_list, strategy_list


def state_to_feature(state):
    pr_real = state["Left_real"] / (state["Left_real"] + state["Left_fake"] + 10 ** -10)
    bullet = state["chamber"][state["pos"]][0] if state["chamber"][state["pos"]][1] == 1 else pr_real
    hp = (state["hp"][state["turn"]]) / (state["max_hp"])
    heal = 1 if state["heal_left"][state["turn"]] > 0 else 0
    reveal = 1 if state["reveal_left"][state["turn"]] > 0 else 0
    double = 1 if state["double_left"][state["turn"]] > 0 else 0
    skip_round = 1 if state["skip_round_left"][state["turn"]] > 0 else 0
    skip_bullet = 1 if state["skip_bullet_left"][state["turn"]] > 0 else 0
    double_mark = state["double_mark"]
    sr_mark = state["skip_round_mark"]
    heal_opponent = 1 if state["heal_left"][state["turn"] ^ 1] > 0 else 0
    reveal_opponent = 1 if state["reveal_left"][state["turn"] ^ 1] > 0 else 0
    double_opponent = 1 if state["double_left"][state["turn"] ^ 1] > 0 else 0
    skip_round_opponent = 1 if state["skip_round_left"][state["turn"] ^ 1] > 0 else 0
    skip_bullet_opponent = 1 if state["skip_bullet_left"][state["turn"] ^ 1] > 0 else 0
    hp_opponent = (state["hp"][state["turn"] ^ 1]) / (state["max_hp"])
    uncertainty = abs(pr_real - 0.5) * 2
    pos = state["pos"] / len(state["chamber"])
    is_revealed = state["chamber"][state["pos"]][1]
    hp_diff = hp - hp_opponent
    return [bullet, hp, hp_opponent, heal, reveal, heal_opponent, reveal_opponent, uncertainty, pos, is_revealed,
            hp_diff, double, skip_round, skip_round_opponent, skip_bullet, skip_bullet_opponent, double_opponent,
            double_mark, sr_mark]
