from __future__ import annotations

from random import sample, shuffle, choice
from itertools import combinations
from typing import Callable, Optional
from math import factorial as fac

from tqdm import tqdm

try:  # pragma: no cover
    from common import GameMode
    from common import RIGHT, CLOSE, WRONG, PROGRESS, SYM_ALTS
    from common import get_response, filter_remaining
    from common import colored_response, count_remaining
    from common import best_guesses, set_best_guess_updated
except ModuleNotFoundError:  # this is only here to help pytest find the module
    from wordle_autosolver.common import GameMode, SYM_ALTS
    from wordle_autosolver.common import RIGHT, CLOSE, WRONG, PROGRESS
    from wordle_autosolver.common import get_response, filter_remaining
    from wordle_autosolver.common import colored_response, count_remaining
    from wordle_autosolver.common import best_guesses, set_best_guess_updated


simulated_answers: list[str] = []

WORST_ANSWERS = [
    'fuzzy', 'epoxy', 'nymph', 'cynic', 'boozy', 'vivid', 'depot', 'movie',
    'their', 'aroma', 'allow', 'tacit', 'swill', 'ferry', 'forgo', 'fewer',
    'lowly', 'foyer', 'flair', 'foray', 'snout', 'bunny', 'hunky', 'funny',
    'boxer', 'baker', 'booby', 'place', 'dizzy', 'fluff'
]
BEST_STARTERS = [  # these have been tested and will always solve in 6 or less
    'adobe', 'shave', 'spine', 'shore', 'salve', 'trial', 'snide', 'snare',
    'sweat', 'shade', 'soapy', 'smite', 'wiser', 'resin', 'sonar', 'anger',
    'realm', 'lance', 'opera', 'sower', 'ashen', 'atone', 'chase', 'snore',
    'spelt', 'cater', 'shine', 'serif', 'slept', 'suave', 'serum', 'alien',
    'ratio', 'adore', 'louse', 'torus', 'arose', 'slain', 'askew', 'snail',
    'cameo', 'petal', 'beast', 'solve', 'liner', 'salty', 'feast', 'paste',
    'swear', 'renal', 'nosey', 'skate', 'mason', 'slime', 'poise', 'stray',
    'caste', 'scare', 'islet', 'stole', 'rebus', 'lathe', 'stove', 'trace',
    'leapt', 'solar', 'swine', 'stead', 'onset', 'miser', 'oaken', 'lager',
    'snarl', 'smart', 'baste', 'snort', 'alike', 'pesto', 'stare', 'inlet',
    'spiel', 'siren', 'loser', 'amuse', 'staid', 'canoe', 'spade', 'snake',
    'crest', 'skier', 'aisle', 'scald', 'abode', 'slope', 'alert', 'pleat',
    'stake', 'aider', 'snipe', 'shard', 'spire', 'arson', 'slant', 'glare',
    'spare', 'lapse', 'sinew', 'sepia', 'spike', 'taper', 'alter', 'scent',
    'smote', 'saute', 'pause', 'shake', 'roast', 'parse', 'arise', 'store',
    'spied', 'suite', 'shrew', 'heist', 'shire', 'saner', 'safer', 'shied',
    'strap', 'motel', 'stoke', 'stern', 'stave', 'sedan', 'smear', 'slide',
    'risen', 'haste', 'shear', 'super', 'react', 'salon', 'leant', 'screw',
    'spore', 'regal', 'leash', 'stair', 'poser', 'irate', 'unset', 'stale',
    'scone', 'shoal', 'prime', 'rusty'
]  # they are also all possible answers in classic Wordle


class SessionInfo:
    """Class holding all variables that define the current state of the game"""
    def __init__(self, num_boards: int, answers: list[str], guesses: list[str],
                 saved_best: dict, freq: dict[str, float],
                 starters: Optional[list[str]] = None,
                 mode: Optional[GameMode] = None) -> None:
        self.entered = []
        self.unentered_answers = set()
        self.solve_count = 0
        self.num_boards = num_boards
        self.answers = answers[:]
        self.guesses = guesses[:]
        self.saved_best = saved_best
        self.freq = freq
        self.starters = [] if starters is None else starters[:]
        self.mode = GameMode() if mode is None else mode
        self.expected = list(range(num_boards))
        self.remaining = [answers[:] for _ in range(num_boards)]
        self.solved = ['*****' for _ in range(num_boards)]
        self.subtree = [saved_best for _ in range(num_boards)]
        self.best = [[] for _ in range(num_boards)]
        self.actual_best = (choice(BEST_STARTERS)
                            if len(starters) == 0
                            else starters[0])

    def copy(self, *,
             num_boards: Optional[int] = None,
             answers: Optional[list[str]] = None,
             guesses: Optional[list[str]] = None,
             saved_best: Optional[dict] = None,
             freq: Optional[dict[str, float]] = None,
             starters: Optional[list[str]] = None,
             mode: Optional[GameMode] = None,
             ) -> SessionInfo:
        return SessionInfo(
            self.num_boards if num_boards is None else num_boards,
            self.answers if answers is None else answers,
            self.guesses if guesses is None else guesses,
            self.saved_best if saved_best is None else saved_best,
            self.freq if freq is None else freq,
            self.starters if starters is None else starters,
            self.mode if mode is None else mode
        )

    def __str__(self):
        PADDING, MAX_LENGTH = 24, 20

        def block_style(target: list, max_len: int, padding: int) -> str:
            """Helper function for SessionInfo.__str__."""
            block_list = []
            curr_str = ''
            index = 0
            while index < len(target):
                item = target[index]
                future_size = len(curr_str) + len(str(item))
                future_size += int(bool(curr_str))
                future_size += int(index < len(target) - 1)
                if curr_str == '' or future_size <= max_len:
                    if curr_str != '':
                        curr_str += ' '
                    curr_str += str(item).upper()
                    curr_str += ',' if index < len(target) - 1 else ''
                    index += 1
                else:
                    block_list.append(curr_str)
                    curr_str = ''
            block_list.append(curr_str)
            ret = '\n'.join([(' ' * padding) + x for x in block_list]).strip()
            if ret == '':
                return 'None'
            return ret

        return ('================SESSION_INFO================\n'
                '            # of games: {:d}\n'
                '             game mode: {}\n'
                ' # of possible answers: {:d}\n'
                '    # of valid guesses: {:d}\n'
                '              starters: {}\n'
                '         entered words: {}\n'
                '             solutions: {}\n'
                '     unentered answers: {}\n'
                ' # of unfinished games: {:d}\n'
                ' # of matching answers: {}\n'
                + str('\n'.join(
                    ' best guesses [GAME {:d}]: {}'.format(
                        n + 1, block_style(self.best[n], MAX_LENGTH, PADDING)
                    ) for n in range(self.num_boards)
                    ) + '\n'
                    if self.num_boards <= 8 else
                    '  # best guesses found: {:d}\n'.format(
                        sum(len(b) for b in self.best)
                    ))
                + '    best overall guess: {}'
                ).format(
                    self.num_boards,
                    str(self.mode),
                    len(self.answers),
                    len(self.guesses),
                    block_style(self.starters, MAX_LENGTH, PADDING),
                    block_style(self.entered, MAX_LENGTH, PADDING),
                    block_style(self.solved, MAX_LENGTH, PADDING),
                    block_style(list(self.unentered_answers),
                                MAX_LENGTH, PADDING),
                    len(self.expected),
                    block_style([len(r) for r in self.remaining],
                                MAX_LENGTH, PADDING),
                    self.actual_best.upper()
                )


def get_worst_liar_response(guess: str, answer: str, remaining: list[str]):
    """Finds a valid liar response which results in the most remaining answers.

    Args:
        guess:
            The word which was guessed by the player
        answer:
            A potential answer word to be tested
        remaining:
            The list of remaining possible answers

    Returns:
        The response which results in the most remaining possible answers.
    """
    mode = GameMode()
    response = get_response(guess, answer, mode)
    mode.liar = True
    worst_response = ''
    worst_count = 0
    for sym_idx in range(len(response)):
        for alt in SYM_ALTS[response[sym_idx]]:
            response = response[:sym_idx] + alt + response[sym_idx + 1:]
            count = count_remaining(remaining, guess, response, mode)
            if count > worst_count:
                worst_response = response
                worst_count = count
    return worst_response


###############################################################################
#                    CODE FOR MANUAL AND SIMULATED INPUTS                     #
###############################################################################


def manual_guess(session: SessionInfo, help: bool = False) -> str:
    """Prompts the user to enter their most recent guess.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved
        help:
            A boolean value representing whether to show the best next guess
            (default: False)

    Returns:
        The word which was selected as the guess.
    """
    guesses = session.guesses
    if session.mode.hard:
        guesses = set(sum(session.remaining, []))
    if help:
        print("\n  Best guess is {}\n".format(session.actual_best.upper()))
    guess = input("  What is your next guess?\n    (Enter '!help' to see "
                  "the best guess)\n  >>> ").strip().lower()
    while guess not in guesses:
        if guess == '!help':
            return manual_guess(session, True)
        guess = input("  Invalid guess. Try again.\n  >>> ").strip().lower()
    if guess in session.solved:
        board = session.solved.index(guess) + 1
        print("\n    The answer{} is {}\n".format(
                '' if session.num_boards == 1 else
                (' on board ' + str(board)), guess.upper()))
    return guess


def manual_response(session: SessionInfo) -> list[tuple[str, int]]:
    """Prompts the user to enter the response(s) given by the game.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    guess = session.entered[-1]
    for board in range(session.num_boards):
        if len(session.remaining[board]) > 1:
            response = input(
                "  What was the response" + (
                    "" if session.num_boards == 1 else
                    " on board {}".format(board + 1)
                ) + "?\n  >>> "
            ).strip().upper()
            rem = filter_remaining(session.remaining[board], guess, response,
                                   session.mode)
            while True:
                err_message = None
                if len(response) != len(guess):
                    err_message = ('Response must be correct length ({}). '
                                   'Try again.\n>>> ').format(len(guess))
                elif any(x not in (RIGHT, CLOSE, WRONG) for x in response):
                    err_message = ('Invalid character in response. '
                                   'Expected one of: "{}", "{}", or "{}". '
                                   'Try again.\n>>> '
                                   ).format(RIGHT, CLOSE, WRONG)
                elif len(rem) == 0:
                    err_message = ('The given response eliminates all possible'
                                   ' answers remaining. Are you sure you '
                                   'entered it correctly? Try again.\n>>>')
                if err_message is None:
                    break
                response = input(err_message).strip().upper()
                rem = filter_remaining(session.remaining[board], guess,
                                       response, session.mode)
            yield response, board


def simulated_guess(session: SessionInfo) -> str:
    """Returns `session.actual_best`."""
    return session.actual_best


def simulated_response(session: SessionInfo) -> list[tuple[str, int]]:
    """Prompts the program to give response(s) based on the simulated answers.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    global simulated_answers
    if (len(session.entered) == 1
            and len(simulated_answers) != session.num_boards):
        simulated_answers = sample(session.remaining[0],
                                   session.num_boards)  # pragma: no cover
    responses = []
    for board in session.expected:
        if session.mode.liar:
            responses.append(
                (get_worst_liar_response(session.entered[-1],
                                         simulated_answers[board],
                                         session.remaining[board]),
                 board)
            )
        else:
            responses.append(
                (get_response(session.entered[-1], simulated_answers[board],
                              session.mode), board)
            )
    return responses


###############################################################################
#                   MAIN FUNCTION FOR SOLVING WORDLE GAMES                    #
###############################################################################


def solve_wordle(session: SessionInfo,
                 auto_guess: Callable[[SessionInfo], str],
                 auto_response: Callable[[SessionInfo], list[tuple[str, int]]],
                 allow_print=False) -> SessionInfo:
    """PRIMARY SOLVE FUNCTION - Solves Wordle(s) based on the given parameters.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved
        auto_guess:
            A function which takes a SessionInfo instance and returns a str;
            for an example of what is expected, refer to `manual_guess`
        auto_response:
            A function which takes a SessionInfo instance and returns a list;
            for an example of what is expected, refer to `manual_response`
        allow_print:
            A boolean value representing whether the program should print info
            to the console (each guess/response, PROGRESS bars, etc.) (default:
            False)

    Returns:
        The given SessionInfo instance after it has been modified by the solver
    """
    if allow_print:
        print(
            '\n\nStarting solver.' + (
                '' if session.num_boards == 1 else
                ' Simulating {} simultaneous Wordle games.'.format(
                    session.num_boards
                )
            )
        )
    if allow_print and not session.mode.play:
        print("\nSuggested starting word is {}\n".format(
            session.actual_best.upper()
        ))
    # continue as long as there are still any unsolved boards
    while (any(len(r) > 1 for r in session.remaining) or
           (session.mode.play and
            not all(x in session.entered for x in session.solved))):
        # print the currently known letters/answers and display the best guess
        if session.num_boards > 1 and allow_print and not session.mode.play:
            print("\nSolved {:>2d}/{:<2d} boards: [{}]".format(
                session.solve_count, session.num_boards,
                ', '.join(session.solved).upper()
            ))
        if any(x not in session.entered for x in session.starters):
            for guess in session.starters:
                if guess not in session.entered:
                    session.actual_best = guess
                    if allow_print and not session.mode.play:
                        print("\n  Predetermined guess is {}\n"
                              .format(guess.upper()))
                    break
        elif allow_print and auto_guess != manual_guess:
            print("\n  {} {}...\n".format((
                    'Entering'
                    if session.actual_best in session.solved
                    else 'Guessing'
                ), session.actual_best.upper()
            ))
        # enter the guess into the game; update `entered` and `guesses`
        session.entered.append(auto_guess(session))
        session.guesses.remove(session.entered[-1])
        # parse the response for each board and find the best guess(es)
        session.best = [[] for _ in range(session.num_boards)]
        for response, board in auto_response(session):
            if all(x == RIGHT for x in response) and board in session.expected:
                session.expected.remove(board)
                session.solve_count += 1
            session.best[board], session.remaining[board] = _parse_response(
                response, board, auto_response, session, allow_print)
        # recommend guessing any answers which have been found but not entered
        _find_best_overall_guess(session, allow_print)
    # function complete -- print any final information the user might need
    if allow_print:
        print('\n{} complete.\n'.format(
            'Game' if session.mode.play else 'Solve'
        ))
    if len(session.unentered_answers) > 0 and auto_guess != manual_guess:
        # if in "auto" mode, and all answers are known, enter them one by one
        if allow_print:
            print('Entering all remaining answers... ({} total)'.format(
                len(session.unentered_answers)
            ))
        for index, answer in enumerate(session.solved):
            if answer not in session.unentered_answers:
                if allow_print:
                    print('  Entered  {:>4d}/{:<4d} {}'.format(
                        index + 1, len(session.remaining), answer.upper()
                    ))
                continue
            if allow_print:
                print('  Entering {:>4d}/{:<4d} {}'.format(
                    index + 1, len(session.remaining), answer.upper()
                ))
            session.actual_best = answer
            session.entered.append(auto_guess(session))
    if len(session.solved) > 4 and auto_guess == manual_guess and allow_print:
        # if 5 or more games and "manual" mode, list all solutions in order
        print("\nSOLUTIONS:")
        for index, answer in enumerate(session.solved):
            print("{:>4d}. {}".format(index + 1, answer))
    session.unentered_answers = (
        set(session.solved) & set(session.answers)) - set(session.entered)
    return session


def _parse_response(response: str, board: int, auto_response: Callable,
                    session: SessionInfo, allow_print: bool
                    ) -> tuple[list[str], list[str]]:
    """Helper function for `solve_wordle`."""
    guess = session.entered[-1]
    answers = session.remaining[board]
    if (allow_print and
            (session.mode.play or (auto_response != manual_response
                                   and len(answers) > 1))):
        print("  Response was \"{}\" on board {}".format(
            colored_response(guess, response, session.mode), board + 1
        ))
    if len(answers) == 1:  # this board has already been solved
        return [], answers
    # just in case filtering results in an empty list, keep one element
    valid_answer = answers[0]
    answers = filter_remaining(answers, guess, response, session.mode)
    if len(answers) == 0:  # response does not match any known answers
        if allow_print:
            print("\n\nBOARD {} USES A NEW WORD\n\n".format(board + 1))
        answers = session.guesses  # create a new list using ALL words
        # valid_answer only holds true up to the previous guess
        for entry in session.entered[:-1]:
            resp = get_response(entry, valid_answer, session.mode)
            answers = filter_remaining(answers, entry, resp, session.mode)
        # now filter the new list using the current guess and response
        answers = filter_remaining(answers, guess, response, session.mode)
    if len(answers) == 0:  # response STILL does not match
        exit('ERROR: BAD RESPONSE ON BOARD {}: {}'
             .format(board + 1, response))
    if session.num_boards > 1:
        for index in range(len(response)):
            if all(r[index] == answers[0][index] for r in answers):
                pattern = session.solved[board]
                session.solved[board] = (pattern[:index] + answers[0][index]
                                         + pattern[index + 1:])
    # update subtree (and by extension, also saved_best)
    if guess not in session.subtree:
        session.subtree[board][guess] = {}
        set_best_guess_updated()
    if response not in session.subtree[board][guess]:
        session.subtree[board][guess][response] = {}
        set_best_guess_updated()
    session.subtree[board] = session.subtree[board][guess][response]
    # print best guesses (or the answer) to the console
    best = []
    if len(answers) == 1:
        solution = answers[0]
        session.solved[board] = solution
        if allow_print and (not session.mode.play or
                            response == ''.join([RIGHT for _ in response])):
            print("\n    The answer{} is {}\n".format(
                    '' if session.num_boards == 1 else
                    (' on board ' + str(board + 1)), solution.upper()))
        return [], answers
    elif (auto_response != simulated_response or
            all(guess in session.entered for guess in session.starters)):
        # update tree with best guesses if the game is still unsolved
        subset = list(session.subtree[board].keys())  # use any saved answers
        if len(subset) == 0:
            subset = session.guesses  # default to the entire allowed word list
        if session.mode.hard:
            for entry in session.entered:
                resp = get_response(entry, answers[0], session.mode)
                subset = filter_remaining(subset, entry, resp, session.mode)
        best = sorted(
            best_guesses(answers, subset, session.mode, show=allow_print),
            key=lambda x: session.freq[x], reverse=True)[:16]
        for best_guess in best:
            if best_guess not in session.subtree[board]:
                session.subtree[board][best_guess] = {}
                set_best_guess_updated()
        if allow_print and not session.mode.play:
            print('  Best guess(es){}: {}'.format(
                '' if session.num_boards == 1 else
                (' on board ' + str(board + 1)),
                (', '.join(best[:8]).upper() +
                    ('' if len(best) <= 8 else ', ...'))
                ))
            print('    {} possible answers{}'.format(len(answers),
                  (': ' + str(', '.join(answers)).upper())
                   if (len(answers) <= 9) else ''))
    return best, answers


def _find_best_overall_guess(session: SessionInfo, allow_print: bool
                             ) -> tuple[str, set]:
    """Helper function for `solve_wordle`."""
    session.unentered_answers = (
        set(session.solved) & set(session.answers)) - set(session.entered)
    if ((len(session.unentered_answers) > 0 or
         session.solve_count < session.num_boards) and
            all(guess in session.entered for guess in session.starters)):
        options = set(session.unentered_answers
                      if len(session.unentered_answers) > 0
                      else sum(session.best, []))
        if 1 <= len(options) <= 2:
            session.actual_best = sorted(
                list(options), key=lambda x: session.freq[x], reverse=True
            )[0]
        else:
            best_score = len(session.guesses) * session.num_boards
            for next_guess in tqdm(options, ascii=PROGRESS, leave=False,
                                   disable=not allow_print):
                worst = []
                for board in range(session.num_boards):
                    found = set()
                    worst_case = 1
                    if len(session.remaining[board]) == 1:
                        continue  # ignore any solved boards
                    for answer in session.remaining[board]:
                        response = get_response(next_guess, answer,
                                                session.mode)
                        if response in found:
                            continue
                        found.add(response)
                        count = count_remaining(session.remaining[board],
                                                next_guess, response,
                                                session.mode)
                        if count > worst_case:
                            worst_case = count
                    worst.append(worst_case)
                total = sum(worst)
                if total < best_score:
                    best_score = total
                    session.actual_best = next_guess
                elif total == best_score and session.freq[
                    session.actual_best
                ] < session.freq[next_guess]:
                    session.actual_best = next_guess
        if session.actual_best in session.unentered_answers:
            solved_board = session.solved.index(session.actual_best)
            if solved_board in session.expected:
                session.expected.remove(solved_board)
        if allow_print and not session.mode.play:
            print("\n  Best next guess: {}".format(
                session.actual_best.upper()
            ))


def simulate(session: SessionInfo, total_sims: int = 0, best: int = -8,
             *, show: bool = True, return_if_worse: bool = False,
             ) -> tuple[float, int]:
    """Runs a simulation to collect data about the given parameters.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved
        total_sims:
            The maximum number of games to simulate when collecting data; when
            not set, this will simulate every possible game (default: 0)
        best:
            Integer value representing the best worst-case score of all other
            simulations using different starting parameters (default: -8)
        show:
            A boolean value representing whether to show PROGRESS bars and more
            detailed results (default: True)

    Returns:
        A 2-tuple where the first element is the average score and the second
        element is the worst score across all simulations. The score is
        calculated as `score = num_boards + 5 - len(entered)`, where `entered`
        is the list of all guesses used to solve the game.
    """
    global simulated_answers
    answers = session.answers
    n, r = len(answers), session.num_boards
    max_sims = fac(n) / (fac(r) * fac(n - r))
    if total_sims == 0:
        total_sims = max_sims
    generated = []
    if session.num_boards == 1:
        if total_sims < len(answers):
            generated = answers[:]
            shuffle(generated)
            generated = generated[:total_sims]
        else:
            generated += [ans for ans in WORST_ANSWERS if ans in answers]
            generated += [ans for ans in answers if ans not in WORST_ANSWERS]
    elif total_sims < max_sims:
        while len(generated) < total_sims:
            answer_list = ','.join(sample(answers, session.num_boards))
            if answer_list not in generated:
                generated.append(answer_list)
    else:
        generated = [','.join(c) for c in
                     combinations(answers, session.num_boards)]
    total_sims = len(generated)
    scores = {}
    failures = []
    starting = str(session.starters)[1:-1]
    if show:
        print("Simulating {} unique games{}...".format(
            len(generated),
            '' if starting == '' else ' with starting word(s) ' + starting)
        )
    for answer_list in tqdm(generated, ascii=PROGRESS,
                            leave=False, disable=not show):
        simulated_answers = answer_list.split(',')
        result = solve_wordle(session.copy(), simulated_guess,
                              simulated_response)
        score = -8
        if result.solved == simulated_answers:
            score = session.num_boards + 5
            score -= len(result.entered) + len(result.unentered_answers)
        if score < best and return_if_worse:
            return score, score
        if score not in scores:
            scores[score] = 0
        if score < 0:
            failures.append(answer_list)
        scores[score] += 1
    avg = sum(score * count for score, count in scores.items()) / total_sims
    worst = min(scores.keys())
    if show:
        print('\n\nSimulation complete.\n\n SCORE | COUNT | %TOTAL')
        for score in range(-8, 6):
            if score in scores:
                count = scores[score]
                print('{:^7d}|{:^7d}| {:<.4f}'.format(score, count, 100 *
                                                      count / total_sims))
        print("\nAVERAGE = {:.2f}".format(avg))
        if len(failures) < 64:
            print("FAILURES = {}".format(str(failures)))
        print()
    return avg, worst
