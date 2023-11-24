""" Generic learning algorithm for adversarial two-person
    zero-sum games of perfect information.

    General approach:  Make a list of strategies based
    on pattern recognition. Use the multi-arm bandit
    approach to learning which strategies win the most.
"""

from collections import Counter
from itertools import chain
from itertools import cycle
from pprint import pprint
from random import choice
from random import choices


# Game Definition ################################

# https://en.wikipedia.org/wiki/Rock%E2%80%93paper%E2%80%93scissors
# scorer['RS'] -> 1 meaning Rock cuts Scissors is +1 for the first player.
scorer = dict(SP=1, PR=1, RS=1, PS=-1, RP=-1, SR=-1, SS=0, PP=0, RR=0)

# Scissors cuts Paper; Paper covers Rock; Rock crushes Scissors
ideal_response = {"P": "S", "R": "P", "S": "R"}
options = ["R", "P", "S"]

# Strategy Utilities #############################


def select_proportional(events, baseline=()):
    rel_freq = Counter(chain(baseline, events))
    population, weights = zip(*rel_freq.items())
    return choices(population, weights)[0]


def select_maximum(events, baseline=()):
    rel_freq = Counter(chain(baseline, events))
    return rel_freq.most_common(1)[0][0]


# Strategies #####################################


def random_reply(p1hist, p2hist):
    return choice(options)


def single_event_proportional(p1hist, p2hist):
    """When opponent plays R two-thirds of the time,
    respond with P two-thirds of the time.'
    """
    prediction = select_proportional(p2hist, options)
    return ideal_response[prediction]


def single_event_greedy(p1hist, p2hist):
    """When opponent plays R more than P or S,
    always respond with P.'
    """
    prediction = select_maximum(p2hist, options)
    return ideal_response[prediction]


def digraph_event_proportional(p1hist, p2hist):
    """When opponent's most recent play is S
    and they usually play R two-thirds of the time
    after an S, respond with P two-thirds of the time.
    """
    recent_play = p2hist[-1:]
    digraphs = zip(p2hist, p2hist[1:])
    followers = [b for a, b in digraphs if a == recent_play]
    prediction = select_proportional(followers, options)
    return ideal_response[prediction]


def digraph_event_greedy(p1hist, p2hist):
    """When opponent's most recent play is S
    and they usually play R two-thirds of the time
    after an S, respond with P all of the time.
    """
    recent_play = p2hist[-1:]
    digraphs = zip(p2hist, p2hist[1:])
    followers = [b for a, b in digraphs if a == recent_play]
    prediction = select_maximum(followers, options)
    return ideal_response[prediction]


strategies = [
    random_reply,
    single_event_proportional,
    single_event_greedy,
    digraph_event_proportional,
    digraph_event_greedy,
]


def play_and_learn(opposition, strategies=strategies, trials=1000, verbose=False):
    strategy_range = range(len(strategies))
    weights = [1] * len(strategies)
    p1hist = []
    p2hist = []
    cum_score = 0
    for trial in range(trials):
        # choose our move
        our_moves = [strategy(p1hist, p2hist) for strategy in strategies]
        i = choices(strategy_range, weights)[0]
        our_move = our_moves[i]

        # get opponent's move
        opponent_move = opposition(p2hist, p1hist)

        # determine the winner
        score = scorer[our_move + opponent_move]
        if verbose:
            print(
                f"{our_move} ~ {opponent_move} = {score:+d}"
                f"\t\t{strategies[i].__name__}"
            )
        cum_score += score

        # update move history and strategy weights
        p1hist.append(our_move)
        p2hist.append(opponent_move)
        for i, our_move in enumerate(our_moves):
            if scorer[our_move + opponent_move] == 1:
                weights[i] += 1

    print(f"---- vs. {opposition.__name__} ----")
    print("Total score:", cum_score)
    pprint(
        sorted(
            [
                (weight, strategy.__name__)
                for weight, strategy in zip(weights, strategies)
            ]
        )
    )


if __name__ == "__main__":

    def human(p1hist, p2hist):
        return input(f"Choose one of {options!r}: ")

    def fixed_ratio(p1hist, p2hist):
        return choices(options, (1, 2, 3))[0]

    def cycling(series):
        iterator = cycle(series)

        def cycle_opponent(p1hist, p2hist):
            return next(iterator)

        return cycle_opponent

    play_and_learn(opposition=fixed_ratio)
    play_and_learn(opposition=random_reply)
    play_and_learn(opposition=cycling("RPRSS"))
    play_and_learn(opposition=human, trials=10, verbose=True)
