from random import sample, shuffle
from itertools import combinations

from common import *


simulated_answers = []

worst_answers = [
    'fuzzy', 'epoxy', 'nymph', 'cynic', 'boozy', 'vivid', 'depot', 'movie',
    'their', 'aroma', 'allow', 'tacit', 'swill', 'ferry', 'forgo', 'fewer',
    'lowly', 'foyer', 'flair', 'foray', 'snout', 'bunny', 'hunky', 'funny',
    'boxer', 'baker', 'booby', 'place', 'dizzy', 'fluff'
]
best_starters = [
    'adobe', 'shave', 'spine', 'shore', 'salve', 'trial', 'snide', 'snare',
    'sweat', 'shade', 'soapy', 'smite', 'wiser', 'resin', 'scree', 'sonar',
    'realm', 'lance', 'opera', 'sower', 'ashen', 'atone', 'chase', 'snore',
    'spelt', 'cater', 'shine', 'serif', 'slept', 'suave', 'serum', 'alien',
    'ratio', 'adore', 'louse', 'torus', 'arose', 'slain', 'askew', 'snail',
    'cameo', 'petal', 'beast', 'solve', 'liner', 'salty', 'feast', 'paste',
    'swear', 'renal', 'nosey', 'tease', 'skate', 'mason', 'slime', 'poise',
    'lease', 'caste', 'scare', 'islet', 'stole', 'noose', 'rebus', 'lathe',
    'leapt', 'solar', 'swine', 'stead', 'onset', 'miser', 'oaken', 'lager',
    'snarl', 'smart', 'baste', 'snort', 'alike', 'pesto', 'stare', 'inlet',
    'spiel', 'siren', 'cress', 'loser', 'amuse', 'staid', 'canoe', 'spade',
    'crest', 'skier', 'sneer', 'aisle', 'scald', 'abode', 'slope', 'alert',
    'stake', 'aider', 'snipe', 'shard', 'spire', 'arson', 'slant', 'glare',
    'spare', 'lapse', 'sinew', 'sepia', 'spike', 'taper', 'alter', 'scent',
    'smote', 'saute', 'easel', 'pause', 'shake', 'roast', 'parse', 'arise',
    'spied', 'suite', 'shrew', 'heist', 'shire', 'asset', 'saner', 'safer',
    'strap', 'motel', 'stoke', 'stern', 'stave', 'sedan', 'smear', 'slide',
    'risen', 'haste', 'shear', 'super', 'react', 'salon', 'leant', 'screw',
    'spore', 'regal', 'leash', 'stair', 'poser', 'sleet', 'irate', 'unset',
    'trace', 'scone', 'shoal', 'shied', 'stale', 'pleat', 'snake', 'stove'
]


###############################################################################
#                   MAIN FUNCTION FOR SOLVING WORDLE GAMES                    #
###############################################################################


def solve_wordle(saved_best, freq, guesses, answers, starting_guesses,
                 num_boards, hard, master, liar, endless,
                 auto_guess, auto_response, allow_print=False):
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
    actual_best = sample(best_starters, 1)[0]
    if allow_print:
        print(
            "\nSuggested starting word is {}\n".format(actual_best.upper()))
    while any(len(r) > 1 for r in remaining):
        if num_boards > 1 and allow_print:
            print("\nSolved {:>2d}/{:<2d} boards: {}".format(
                solve_count, num_boards, ', '.join(solved).upper()))
        if any(x not in entered for x in starting_guesses):
            for guess in starting_guesses:
                if guess not in entered:
                    actual_best = guess
                    if allow_print:
                        print(
                            "\n  Predetermined guess is {}\n".format(
                                guess.upper()))
                    break
        elif allow_print and auto_guess != manual_guess:
            print("\n  Guessing {}...\n".format(
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
                print("  Response was '{}' on board {}".format(response,
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
                    all(guess in entered for guess in starting_guesses)):
                # update tree with best guesses if the game is still unsolved
                subset = list(subtree[board].keys())  # use any saved answers
                if len(subset) == 0:
                    subset = guesses  # default to the entire allowed word list
                if hard:
                    for entry in entered:
                        resp = get_response(entry, rem[0], False)
                        subset = filter_remaining(subset, entry, resp, False)
                best[board] = best_guesses(rem, subset, master=master,
                                           show=allow_print)[:32]
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
                all(guess in entered for guess in starting_guesses)):
            best_score = len(guesses) * len(remaining)
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
                        worst_case = 0
                        if len(remaining[board]) == 1:
                            continue
                        for answer in remaining[board]:
                            response = get_response(next_guess, answer, master)
                            if response in found:
                                continue
                            found.add(response)
                            count = count_remaining(remaining[board],
                                                    next_guess, response,
                                                    worst_case, master)
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
                expected.remove(solved.index(actual_best))
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


def manual_guess(remaining, guesses, best, hard, master, endless):
    if hard:
        guesses = remaining[0]
    guess = input("What was your last guess?\n>>> ").strip().lower()
    while guess not in guesses:
        guess = input("Invalid guess. Try again.\n>>> ").strip().lower()
    return guess


def manual_response(guess, remaining, entered, expected, hard, master,
                    liar, endless):
    n_games = len(remaining)
    for board in range(n_games):
        if len(remaining[board]) > 1:
            response = input(
                "What was the response" + (
                    "" if n_games == 1 else
                    " on board {}".format(board + 1)
                ) + "?\n>>> "
            ).strip().upper()
            rem = filter_remaining(remaining[board], guess, response,
                                   master, liar)
            while (any(x not in (RIGHT, CLOSE, WRONG) for x in response)
                    or (len(rem) == 0) or (len(response) != len(guess))):
                response = input("Invalid response. Try again.\n>>> "
                                 ).strip().upper()
                rem = filter_remaining(remaining[board], guess, response,
                                       master, liar)
            yield response, board


def simulated_guess(remaining, guesses, best, hard, master, endless):
    return best


def simulated_response(guess, remaining, entered, expected, hard, master,
                       liar, endless):
    global simulated_answers
    if len(entered) == 1 and len(simulated_answers) != len(remaining):
        simulated_answers = sample(remaining[0], len(remaining))
    responses = []
    for board in expected:
        responses.append(
            (get_response(guess, simulated_answers[board], master), board)
        )
    return responses


def simulate(saved, freq, guesses, answers, start, num_games, hard, master,
             liar, auto_guess, auto_response, total_sims, best, show):
    global simulated_answers
    generated = []
    if num_games == 1:
        if total_sims < len(answers):
            generated = answers[:]
            shuffle(generated)
            generated = generated[:total_sims]
        else:
            generated += worst_answers
            generated += [ans for ans in answers if ans not in worst_answers]
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
        print("Simulating {} unique games with starting word(s) {}...".format(
            len(generated), 'ratio' if starting == '' else starting))
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
    if show:
        print('\n\nSimulation complete.\n\n SCORE | COUNT | %TOTAL')
        for score in range(-8, 6):
            if score in scores:
                count = scores[score]
                print('{:^7d}|{:^7d}| {:<.4f}'.format(score, count,
                                                      count / total_sims))
        print()
    avg = sum(score * count for score, count in scores.items()) / total_sims
    if show:
        print("AVERAGE = {:.2f}".format(avg))
        if len(failures) < 64:
            print("FAILURES = {}".format(str(failures)))
        print()
    worst = min(scores.keys())
    return avg, worst
