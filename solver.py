from random import sample, shuffle
from itertools import combinations
from typing import Callable

try:
    from common import *
except ImportError:
    from .common import *


simulated_answers: list[str] = []

WORST_ANSWERS = [
    'fuzzy', 'epoxy', 'nymph', 'cynic', 'boozy', 'vivid', 'depot', 'movie',
    'their', 'aroma', 'allow', 'tacit', 'swill', 'ferry', 'forgo', 'fewer',
    'lowly', 'foyer', 'flair', 'foray', 'snout', 'bunny', 'hunky', 'funny',
    'boxer', 'baker', 'booby', 'place', 'dizzy', 'fluff'
]
BEST_STARTERS = [
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
]


###############################################################################
#                   MAIN FUNCTION FOR SOLVING WORDLE GAMES                    #
###############################################################################


def solve_wordle(saved_best: dict, freq: dict[str, float], answers: list[str],
                 guesses: list[str], starters: list[str], num_boards: int,
                 hard: bool, master: bool, liar: bool, endless: bool,
                 auto_guess: Callable[[list[str], list[str], str, bool, bool,
                                       bool], str],
                 auto_response: Callable[[str, list[str], list[str], list[int],
                                          bool, bool, bool, bool],
                                         list[tuple[str, int]]],
                 allow_print=False):
    """PRIMARY SOLVE FUNCTION - Solves wordle(s) based on the given parameters.

    Args:
        saved_best:
            A dict representing the decision tree used to find best guesses
        freq:
            A dict mapping all valid guesses to their frequency of use
        answers:
            The list of all possible answers
        guesses:
            The list of all valid guesses
        starters:
            A list of guesses the player wishes to begin with regardless of the
            game's response (may be empty) -- manual guesses may ignore these
        num_boards:
            The number of simultaneous games being played (each guess is made
            across all boards at once)
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode
        auto_guess:
            A function which takes six arguments and returns a str; for an
            example of what is expected, refer to `manual_guess`
        auto_response:
            A function which takes eight arguments and returns a list; for an
            example of what is expected, refer to `manual_response`
        allow_print:
            A boolean value representing whether the program should print info
            to the console (each guess/response, progress bars, etc.) (default:
            False)

    Returns:
        A 2-tuple containing two lists of str: the first list contains the
        solutions for each board, in order; the second list contains every word
        guessed by the user (or the program), also in order.
    """
    if allow_print:
        print(
            '\n\nStarting solver.' + (
                '' if num_boards == 1 else
                ' Simulating {} simultaneous Wordle games.'.format(num_boards)
            )
        )
    entered = []
    unentered_answers = set()
    expected = [n for n in range(num_boards)]
    remaining = [[x for x in answers] for _ in range(num_boards)]
    solved = ['*****' for _ in range(num_boards)]
    solve_count = 0
    subtree = [saved_best for _ in range(num_boards)]
    actual_best = sample(BEST_STARTERS, 1)[0]
    if allow_print:
        print(
            "\nSuggested starting word is {}\n".format(actual_best.upper()))
    while any(len(r) > 1 for r in remaining):
        if num_boards > 1 and allow_print:
            print("\nSolved {:>2d}/{:<2d} boards: [{}]".format(
                solve_count, num_boards, ', '.join(solved).upper()))
        if any(x not in entered for x in starters):
            for guess in starters:
                if guess not in entered:
                    actual_best = guess
                    if allow_print:
                        print(
                            "\n  Predetermined guess is {}\n".format(
                                guess.upper()))
                    break
        elif allow_print and auto_guess != manual_guess:
            print("\n  {} {}...\n".format(
                'Entering' if actual_best in solved else 'Guessing',
                actual_best.upper()))
        guess = auto_guess(remaining, guesses, actual_best,
                           hard, master, endless)
        entered.append(guess)
        best = [[] for _ in range(num_boards)]
        for response, board in auto_response(guess, remaining, entered,
                                             expected, hard, master, liar,
                                             endless):
            rem = remaining[board]  # simply used to shorten "remaining[board]"
            if all(x == RIGHT for x in response) and board in expected:
                expected.remove(board)
            if len(rem) == 1:
                best[board] = []
                continue
            if allow_print and auto_response != manual_response:
                print("  Response was \"{}\" on board {}".format(response,
                                                                 board + 1))
            # just in case filtering results in an empty list, keep one element
            valid_answer = rem[0]
            rem = filter_remaining(rem, guess, response, master, liar)
            if len(rem) == 0:  # response does not match any known answers
                if allow_print:
                    print("\n\nBOARD {} USES A NEW WORD\n\n".format(board + 1))
                rem = guesses  # create a new list using all words
                # valid_answer only holds true up to the previous guess
                for entry in entered[:-1]:
                    resp = get_response(entry, valid_answer, master)
                    rem = filter_remaining(rem, entry, resp, master, liar)
                # now filter the new list using the current guess and response
                rem = filter_remaining(rem, guess, response, master, liar)
            if len(rem) == 0:  # response STILL does not match
                exit('ERROR: BAD RESPONSE ON BOARD {}: {}'.format(board + 1,
                                                                  response))
            if num_boards > 1:
                for index in range(len(response)):
                    if all(r[index] == rem[0][index] for r in rem):
                        pattern = solved[board]
                        solved[board] = (pattern[:index] + rem[0][index]
                                         + pattern[index + 1:])
            # update subtree (and by extension, also saved_best)
            if guess not in subtree[board]:
                subtree[board][guess] = {}
                set_best_guess_updated()
            if response not in subtree[board][guess]:
                subtree[board][guess][response] = {}
                set_best_guess_updated()
            subtree[board] = subtree[board][guess][response]
            # print best guesses (or the answer) to the console
            best[board] = []
            if len(rem) == 1:
                solution = rem[0]
                solved[board] = solution
                solve_count += 1
                if allow_print:
                    print("\n    The answer{} is {}\n".format(
                          '' if num_boards == 1 else
                          (' on board ' + str(board + 1)), solution.upper()))
            elif (auto_response != simulated_response or
                    all(guess in entered for guess in starters)):
                # update tree with best guesses if the game is still unsolved
                subset = list(subtree[board].keys())  # use any saved answers
                if len(subset) == 0:
                    subset = guesses  # default to the entire allowed word list
                if hard:
                    for entry in entered:
                        resp = get_response(entry, rem[0], False)
                        subset = filter_remaining(subset, entry, resp, False)
                best[board] = best_guesses(rem, subset, master=master,
                                           liar=liar, show=allow_print)[:32]
                for best_guess in best[board]:
                    if best_guess not in subtree[board]:
                        subtree[board][best_guess] = {}
                        set_best_guess_updated()
                best[board].sort(key=lambda x: freq[x], reverse=True)
                if allow_print:
                    print('  Best guess(es){}: {}'.format(
                        '' if num_boards == 1 else
                        (' on board ' + str(board + 1)),
                        (', '.join(best[board][:8]).upper() +
                            ('' if len(best[board]) <= 8 else ', ...'))
                        ))
                    print('    {} possible answers{}'.format(len(rem),
                          (': ' + str(', '.join(rem)).upper())
                           if (len(rem) <= 9) else ''))
            remaining[board] = rem
        # make sure to guess any answers which have been found but not entered
        unentered_answers = (set(solved) & set(answers)) - set(entered)
        if ((len(unentered_answers) > 0 or solve_count < num_boards) and
                all(guess in entered for guess in starters)):
            best_score = len(guesses) * num_boards
            # sum collapses 2D list into 1D
            options = (sum(best, []) if len(unentered_answers) == 0
                       else unentered_answers)
            if 1 <= len(options) <= 2:
                actual_best = list(options)[0]
            else:
                if (len(entered) - len(set(solved) & set(answers)) > 2 and
                        len(unentered_answers) == 0):
                    options = set(guesses) - set(entered)
                for next_guess in tqdm(options, ascii=progress, leave=False,
                                       disable=not allow_print):
                    total = 0
                    for board in range(num_boards):
                        found = set()
                        worst_case = 1
                        if len(remaining[board]) == 1:
                            continue
                        for answer in remaining[board]:
                            response = get_response(next_guess, answer, master)
                            if response in found:
                                continue
                            found.add(response)
                            count = count_remaining(remaining[board],
                                                    next_guess, response,
                                                    worst_case, master, liar)
                            if count > worst_case:
                                worst_case = count
                        total += worst_case
                    if total < best_score:
                        best_score = total
                        actual_best = next_guess
                # if no unentered answer narrows down the pool, don't use one
                if best_score == sum(len(r) for r in remaining):
                    actual_best = sum(best, [])[0]
            if actual_best in unentered_answers:
                solved_board = solved.index(actual_best)
                if solved_board in expected:
                    expected.remove(solved_board)
            if allow_print:
                print("\nBest next guess: {}".format(actual_best.upper()))
    if allow_print:
        print('\nSolve complete.\n')
    if len(unentered_answers) > 0 and auto_guess != manual_guess:
        if allow_print:
            print('Entering all remaining answers... ({} total)'.format(
                len(unentered_answers)))
        for index, answer in enumerate(solved):
            if answer not in unentered_answers:
                if allow_print:
                    print('  Entered  {:>4d}/{:<4d} {}'.format(
                        index + 1, len(remaining), answer.upper()
                    ))
                continue
            if allow_print:
                print('  Entering {:>4d}/{:<4d} {}'.format(
                    index + 1, len(remaining), answer.upper()
                ))
            auto_guess(remaining, guesses, answer, hard, master, endless)
            entered.append(answer)
    if len(solved) > 4 and auto_guess == manual_guess and allow_print:
        for index, answer in enumerate(solved):
            print("{:>4d}. {}".format(index + 1, answer))
    return solved, entered


###############################################################################
#                    CODE FOR MANUAL AND SIMULATED INPUTS                     #
###############################################################################


def manual_guess(remaining: list[str], guesses: list[str], best: str,
                 hard: bool, master: bool, endless: bool) -> str:
    """Prompts the user to enter their most recent guess.

    Required Args:
        remaining:
            The list of all remaining possible answers
        guesses:
            The list of all valid guesses
        best:
            The most recently calculated best guess according to the solver
        hard:
            A boolean value representing whether the game mode is Hard

    Ignored Args:
        master:
            A boolean value representing whether the game mode is Wordzy Master
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        The word which was selected as the guess.
    """
    if hard:
        guesses = remaining[0]
    print("\n  Suggested guess is {}\n".format(best.upper()))
    guess = input("  What was your last guess?\n  >>> ").strip().lower()
    while guess not in guesses:
        guess = input("  Invalid guess. Try again.\n  >>> ").strip().lower()
    return guess


def manual_response(guess: str, remaining: list[str], entered: list[str],
                    expected: list[int], hard: bool, master: bool, liar: bool,
                    endless: bool) -> list[tuple[str, int]]:
    """Prompts the user to enter the response(s) given by the game.

    Required Args:
        guess:
            The most recent guess entered into the game
        remaining:
            The list of remaining possible answers
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble

    Ignored Args:
        entered:
            A list of all words which have been entered into the game so far
        expected:
            A list of all board indexes where the answer has not been entered
        hard:
            A boolean value representing whether the game mode is Hard
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    n_games = len(remaining)
    for board in range(n_games):
        if len(remaining[board]) > 1:
            response = input(
                "  What was the response" + (
                    "" if n_games == 1 else
                    " on board {}".format(board + 1)
                ) + "?\n  >>> "
            ).strip().upper()
            rem = filter_remaining(remaining[board], guess, response,
                                   master, liar)
            while True:
                err_message = None
                if len(response) != len(guess):
                    err_message = ('Response must be correct length ({}). '
                                   'Try again.\n>>> ').format(len(guess))
                elif any(x not in (RIGHT, CLOSE, WRONG) for x in response):
                    err_message = ('Invalid character in response. '
                                   'Expected one of: {"{}", "{}", "{}"}. '
                                   'Try again.\n>>> '
                                   ).format(RIGHT, CLOSE, WRONG)
                elif len(rem) == 0:
                    err_message = ('The given response eliminates all possible'
                                   ' answers remaining. Are you sure you '
                                   'entered it correctly? Try again.\n>>>')
                if err_message is None:
                    break
                response = input(err_message).strip().upper()
                rem = filter_remaining(remaining[board], guess, response,
                                       master, liar)
            yield response, board


def simulated_guess(remaining: list[str], guesses: list[str], best: str,
                    hard: bool, master: bool, endless: bool) -> str:
    """Returns `best` and ignores all other arguments."""
    return best


def simulated_response(guess: str, remaining: list[str], entered: list[str],
                       expected: list[int], hard: bool, master: bool,
                       liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Prompts the program to give response(s) based on the simulated answers.

    Required Args:
        guess:
            The most recent guess entered into the game
        remaining:
            The list of remaining possible answers
        entered:
            A list of all words which have been entered into the game so far
        expected:
            A list of all board indexes where the answer has not been entered
        master:
            A boolean value representing whether the game mode is Wordzy Master

    Ignored Args:
        hard:
            A boolean value representing whether the game mode is Hard
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    global simulated_answers
    if len(entered) == 1 and len(simulated_answers) != len(remaining):
        simulated_answers = sample(remaining[0], len(remaining))
    responses = []
    for board in expected:
        responses.append(
            (get_response(guess, simulated_answers[board], master), board)
        )
    return responses


def simulate(saved: dict, freq: dict[str, float], answers: list[str],
             guesses: list[str], start: list[str], num_games: int, hard: bool,
             master: bool, liar: bool, total_sims: int, best=-8, show=True
             ) -> tuple[float, int]:
    """Runs a simulation to collect data about the given parameters.

    Args:
        saved:
            A dict representing the decision tree used to find best guesses
        freq:
            A dict mapping all valid guesses to their frequency of use
        answers:
            The list of all possible answers
        guesses:
            The list of all valid guesses
        starters:
            A list of guesses the player wishes to begin with regardless of the
            game's response (may be empty, and manual guesses may ignore these)
        num_boards:
            The number of simultaneous games being played (each guess is made
            across all boards at once)
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        total_sims:
            The maximum number of games to simulate when collecting data; when
            `num_games == 1`, this value cannot be greater than `len(answers)`
        best:
            Integer value representing the best worst-case score of all other
            simulations using different starting parameters (default: -8)
        show:
            A boolean value representing whether to show progress bars and more
            detailed results

    Returns:
        A 2-tuple where the first element is the average score and the second
        element is the worst score across all simulations. The score is
        calculated as `score = num_games + 5 - len(entered)`, where `entered`
        is the list of all guesses used to solve the game.
    """
    global simulated_answers
    generated = []
    if num_games == 1:
        if total_sims < len(answers):
            generated = answers[:]
            shuffle(generated)
            generated = generated[:total_sims]
        else:
            generated += WORST_ANSWERS
            generated += [ans for ans in answers if ans not in WORST_ANSWERS]
    elif total_sims < len(answers)**num_games:
        while len(generated) < total_sims:
            answer_list = ','.join(sample(answers, num_games))
            if answer_list not in generated:
                generated.append(answer_list)
    else:
        generated = [','.join(c) for c in combinations(answers, num_games)]
    scores = {}
    failures = []
    starting = str(start)[1:-1]
    if show:
        print("Simulating {} unique games{}...".format(
            len(generated),
            '' if starting == '' else ' with starting word(s) ' + starting)
        )
    for answer_list in tqdm(generated, ascii=progress,
                            leave=False, disable=not show):
        simulated_answers = answer_list.split(',')
        solved, entered = solve_wordle(saved, freq, guesses, answers, start,
                                       num_games, hard, master, liar, False,
                                       simulated_guess, simulated_response)
        score = -8
        if solved == simulated_answers:
            score = num_games + 5 - len(entered)
        if score < best and not show:
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
                print('{:^7d}|{:^7d}| {:<.4f}'.format(score, count,
                                                      count / total_sims))
        print("\nAVERAGE = {:.2f}".format(avg))
        if len(failures) < 64:
            print("FAILURES = {}".format(str(failures)))
        print()
    return avg, worst


if __name__ == '__main__':
    try:
        from driver import main
    except ImportError as e:
        from .driver import main
    main()
