import os
import time
from argparse import ArgumentParser
from itertools import combinations
from math import ceil, log2
from random import sample, shuffle
from json import load, dump

from tqdm import tqdm

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
except ImportError:
    print('Failed to import selenium.\n')


RIGHT = 'O'
CLOSE = 'H'
WRONG = 'X'

RS = 2**26  # file size limit (in bytes) for imports
response_data = {}
response_data_updated = False
best_guess_updated = False
is_ms_os = os.name == 'nt'
progress = '__...:::!!|' if is_ms_os else None
driver = None
auto_guess_count = 0
dialog_closed = False
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
#              LOGIC FOR CALCULATING RESPONSES AND BEST GUESSES               #
###############################################################################


def get_easy_response(guess, answer):
    if guess == answer:
        return ''.join([RIGHT for _ in answer])
    response = [WRONG for _ in answer]
    # get frequency count of each letter in the answer
    letter_count = dict()
    for letter in answer:
        if letter in letter_count:
            letter_count[letter] += 1
        else:
            letter_count[letter] = 1
    # first loop counts exact matches
    for index in range(len(answer)):
        letter = guess[index]
        if letter == answer[index]:
            response[index] = RIGHT
            letter_count[letter] -= 1
    # second loop counts non-exact matches
    for index in range(len(answer)):
        letter = guess[index]
        if letter != answer[index]:
            if letter in letter_count:
                if letter_count[letter] > 0:
                    response[index] = CLOSE
                    letter_count[letter] -= 1
    return ''.join(response)


def get_master_response(guess, answer):
    if guess == answer:
        return ''.join([RIGHT for _ in answer])
    response = ''
    # get frequency count of each letter in the answer
    letter_count = dict()
    for letter in answer:
        if letter in letter_count:
            letter_count[letter] += 1
        else:
            letter_count[letter] = 1
    # first loop counts exact matches
    for index in range(len(answer)):
        letter = guess[index]
        if letter == answer[index]:
            response += RIGHT
            letter_count[letter] -= 1
    # second loop counts non-exact matches
    for index in range(len(answer)):
        letter = guess[index]
        if letter != answer[index]:
            if letter in letter_count:
                if letter_count[letter] > 0:
                    response += CLOSE
                    letter_count[letter] -= 1
    # third loop counts misses
    while len(response) < len(answer):
        response += WRONG
    return response


def get_response(guess, answer, master):
    global response_data, response_data_updated
    if guess in response_data and answer in response_data[guess]:
        return response_data[guess][answer]
    response = ''
    if master:
        response = get_master_response(guess, answer)
    else:
        response = get_easy_response(guess, answer)
    if guess not in response_data:
        response_data[guess] = {}
    response_data[guess][answer] = response
    response_data_updated = True
    return response


def filter_remaining(remaining, guess, response, master, liar=False):
    filtered = []
    for answer in remaining:
        this_response = get_response(guess, answer, master)
        if liar:
            # check that exactly one letter in the response is wrong
            if 1 == sum(int(this_response[n] != response[n])
                        for n in range(len(answer))):
                filtered.append(answer)
        elif this_response == response:
            filtered.append(answer)
    return filtered


def count_remaining(remaining, guess, response, limit=0, master=False):
    limit = max(limit, len(remaining))
    count = 0
    for answer in remaining:
        if get_response(guess, answer, master) == response:
            count += 1
        if count > limit:
            return count
    return count


def best_guesses(answers, guesses=[], max_limit=-1, master=False, show=False,
                 return_all=False):
    if len(guesses) == 0:
        guesses = answers
    if max_limit == -1:
        max_limit = len(answers)
    worst_case = dict([(x, 0) for x in guesses])
    score = dict([(x, {}) for x in guesses])
    limit = max_limit
    for guess in tqdm(guesses, leave=False, ascii=progress, disable=not show):
        for answer in answers:
            response = get_response(guess, answer, master)
            if response not in score[guess]:
                score[guess][response] = count_remaining(answers, guess,
                                                         response, limit,
                                                         master)
            worst_case[guess] = max(worst_case[guess], score[guess][response])
            if worst_case[guess] > limit:
                break
        if not return_all:
            limit = min(limit, worst_case[guess])
    if return_all:
        return worst_case
    best = [x for x in guesses if worst_case[x] == limit]
    priority = set(best) & set(answers)
    if len(priority) > 0:
        return list(priority)
    return best


def best_avg_guesses(answers, guesses=[], master=False, show=False,
                     return_all=False):
    if len(guesses) == 0:
        guesses = answers
    average = dict([(x, 0) for x in guesses])
    count = dict([(x, {}) for x in guesses])
    best_avg = len(answers)**2
    for guess in tqdm(guesses, leave=False, ascii=progress, disable=not show):
        for answer in answers:
            response = get_response(guess, answer, master)
            if response not in count[guess]:
                count[guess][response] = count_remaining(answers, guess,
                                                         response,
                                                         master=master)
            average[guess] += count[guess][response]
        if average[guess] < best_avg:
            best_avg = average[guess]
    if return_all:
        return average
    best = [x for x in guesses if average[x] == best_avg]
    priority = set(best) & set(answers)
    if len(priority) > 0:
        return list(priority)
    return best


def precalculate_responses(guesses, answers, master):
    global response_data, response_data_updated
    print('Precalculating responses...')
    response_data = dict([(guess, {}) for guess in guesses])
    for guess in tqdm(guesses, ascii=progress):
        for answer in answers:
            response_data[guess][answer] = get_response(guess, answer, master)
    response_data_updated = True
    print('Finished calculating.')


def calculate_best_guesses(saved_best, guesses, answers, master, lo=0, hi=-1):
    global best_guess_updated
    if hi == -1:
        hi = len(guesses)
    print('Calculating best guesses for new words...')
    for guess in tqdm(guesses[lo:hi], ascii=progress):
        for answer in tqdm(answers, leave=False, disable=is_ms_os):
            response = get_response(guess, answer, master)
            if response not in saved_best[guess]:
                filtered = filter_remaining(answers, guess, response, master)
                best = best_guesses(filtered, guesses, master=master)
                saved_best[guess][response] = dict([(x, {}) for x in best])
    best_guess_updated = True
    print('Finished calculating.')


def rec_build_best_tree(answers, guesses, guess, master, liar, depth,
                        show=True):
    if depth == 0:
        if len(answers) == 1:
            return {answers[0]: {}}
        return {}
    tree = {guess: {}}
    for answer in tqdm(answers, ascii=progress, disable=not show):
        response = get_response(guess, answer, master)
        if response in tree[guess]:
            continue
        # after this point, treat this as a loop through all possible responses
        filtered = filter_remaining(answers, guess, response, master, liar)
        if len(filtered) == 1:
            # if there is only one option, then it must be the best guess
            tree[guess][response] = {filtered[0]: {}}
            continue
        info = best_guesses(filtered, guesses, return_all=True)
        valid_path = {}
        limit = 2 ** (depth + 3)
        for next_guess in sorted(guesses, key=lambda x: info[x])[:limit]:
            valid_path = rec_build_best_tree(filtered, guesses, next_guess,
                                             master, liar, depth - 1, False)
            if next_guess in valid_path:
                break
        if len(valid_path) == 0:
            return {}  # if any response has no valid paths, this guess failed
        tree[guess][response] = valid_path
    return tree


###############################################################################
#                   MAIN FUNCTION FOR SOLVING WORDLE GAMES                    #
###############################################################################


def solve_wordle(saved_best, freq, guesses, answers, starting_guesses,
                 num_boards, hard, master, liar, endless,
                 auto_guess, auto_response, allow_print=False):
    global best_guess_updated
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
                            "  Predetermined guess is {}\n".format(
                                guess.upper()))
                    break
        elif allow_print:
            print("\n  Your next guess should be {}\n".format(
                actual_best.upper()))
        guess = auto_guess(remaining, guesses, actual_best,
                           hard, master, endless)
        entered.append(guess)
        best = [[] for _ in range(num_boards)]
        for response, board in auto_response(guess, remaining, entered,
                                             expected, hard, master, endless):
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
                best_guess_updated = True
            if response not in subtree[board][guess]:
                subtree[board][guess][response] = {}
                best_guess_updated = True
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
                        best_guess_updated = True
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
                    endless):
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
                       endless):
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


###############################################################################
#          LOGIC FOR SOLVING GAMES AUTOMATICALLY ON VARIOUS WEBSITES          #
###############################################################################


def open_website(website, num_boards=1, master=False, inf=False, quiet=False):
    global driver
    if not quiet:
        print("Connecting to the target website...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    if quiet:
        # options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    if 'wordzmania' in website and master:
        website += 'Master'
    time.sleep(3)
    if any(x in website for x in ('octordle', 'sedecordle', '64ordle')):
        website += '?mode=' + ('free' if inf else 'daily')
    elif 'quordle' in website and inf:
        website += 'practice'
    elif 'nordle' in website:
        website += str(num_boards)
    # # # CURRENTLY NOT WORKING -- ENDLESS WORDLE WILL DEFAULT TO DAILY WORDLE
    # elif 'wordle' in website and endless:
    #     website = 'https://devbanana.itch.io/infinidle'
    # # #
    driver.get(website)
    if not quiet:
        print("Connected to '{}'.".format(website))
    time.sleep(5)
    # must navigate to the correct page on these websites
    if 'wordzmania' in website:
        num_boards = navigate_wordzy(num_boards, inf, quiet)
    elif 'dordle' in website:
        iframe = driver.find_element(by=By.XPATH, value='//*[@id="game_drop"]')
        driver.switch_to.frame(iframe)
        driver.find_element(value='free' if inf else 'daily').click()
        time.sleep(2)
    elif 'infinidle' in website:
        driver.find_element(By.CLASS_NAME, 'load_iframe_btn').click()
        time.sleep(3)
        iframe = driver.find_element(by=By.XPATH, value='//*[@id="game_drop"]')
        driver.switch_to.frame(iframe)
    return num_boards


def auto_guess_default(remaining, guesses, best, hard, master, endless):
    webpage = driver.find_element(by=By.TAG_NAME, value='html')
    time.sleep(0.5)
    webpage.send_keys(best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(1)
    return best


def auto_response_default(guess, remaining, entered, expected, hard, master,
                          endless):
    responses = []
    boards = list(driver.find_element(by=By.ID,
                                      value="box-holder-{}".format(n + 1))
                  for n in range(len(remaining)))
    for board in tqdm(expected, ascii=progress, leave=False):
        response = ''
        for row in boards[board].find_elements(by=By.TAG_NAME, value="tr"):
            if guess.upper() in ''.join(x.text for x in
                                        row.find_elements(by=By.TAG_NAME,
                                                          value="td")):
                for letter in row.find_elements(by=By.TAG_NAME, value="td"):
                    style = letter.get_attribute("style")
                    if 'rgb(0, 204, 136)' in style:
                        response += RIGHT
                    elif 'rgb(255, 204, 0)' in style:
                        response += CLOSE
                    else:
                        response += WRONG
                break
        responses.append((response, board))
    return responses


def navigate_wordzy(num_boards, endless, quiet=False):
    play_buttons = driver.find_elements(by=By.CLASS_NAME,
                                        value='play-button')
    time.sleep(4)
    if not endless:
        select_button = driver.find_element(by=By.CLASS_NAME,
                                            value='stake-selector')
        select_button.click()
        time.sleep(2)
        listbox = driver.find_element(by=By.CLASS_NAME,
                                      value='mat-select-panel')
        lo = 9999
        for element in listbox.find_elements(by=By.CLASS_NAME,
                                             value='mat-option'):
            lo = min(lo, int(str(element.get_attribute('id')).split('-')[-1]))
        num = str(lo + ceil(log2(min(num_boards, 1024))))
        board_num_select = driver.find_element(by=By.ID,
                                               value='mat-option-' + num)
        while not board_num_select.get_attribute('aria-disabled'):
            num = str(int(num) - 1)
            board_num_select = driver.find_element(by=By.ID,
                                                   value='mat-option-' + num)
        num_boards = 2 ** (int(num) - lo)
        board_num_select.click()
        time.sleep(2)
        play_buttons[0].click()
    else:
        play_buttons[1].click()
    if not quiet:
        print("Navigated to '{}'.".format(driver.current_url))
    return num_boards


def validate_wordzy_game(num_boards, endless):
    stage = driver.find_elements(by=By.TAG_NAME, value='cm-game-stage')
    while len(stage) == 0:
        time.sleep(3)
        stage = driver.find_elements(by=By.TAG_NAME, value='cm-game-stage')
        if len(stage) > 0:
            break
        print('\n\n    ERROR: PAGE IS NOT RESPONDING - ATTEMPTING RELOAD...\n')
        time.sleep(7)
        if driver.current_url == 'https://wordzmania.com/Wordzy/Classic':
            navigate_wordzy(num_boards, endless)
            time.sleep(5)


def auto_guess_wordzy(remaining, guesses, best, hard, master, endless):
    global auto_guess_count, dialog_closed
    time.sleep(3)
    validate_wordzy_game(len(remaining), endless)
    for stage in driver.find_elements(by=By.TAG_NAME,
                                      value='cm-display-stage'):
        for button in stage.find_elements(by=By.TAG_NAME, value='button'):
            if (button.get_attribute('color') == 'green' and
                    'play_arrow' in button.text and
                    'mat-button-disabled' in button.get_attribute('class')):
                exit('\n\nGame was not solved in time.\n')
    if len(remaining) > 1:
        auto_guess_count += 1
    keyboard = {}
    for key in driver.find_element(
            by=By.CLASS_NAME, value='keys'
            ).find_elements(
            by=By.CLASS_NAME, value='key'):
        keyboard[key.text.split()[0].strip().lower()] = key
    if ((not dialog_closed or len(remaining) == 1) and
            auto_guess_count == 3):
        time.sleep(2.5)
        dialogs = driver.find_elements(by=By.CLASS_NAME,
                                       value='info-dialog')
        if len(dialogs) > 0:
            dialogs[0].find_element(by=By.TAG_NAME, value='button').click()
            time.sleep(1)
            if len(remaining) > 1:
                dialog_closed = True
    webpage = driver.find_element(by=By.TAG_NAME, value='html')
    webpage.send_keys(best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(3)
    return best


def auto_response_wordzy(guess, remaining, entered, expected, hard, master,
                         endless):
    # check if game has ended
    n_games = len(remaining)
    validate_wordzy_game(n_games, endless)
    for stage in driver.find_elements(by=By.TAG_NAME,
                                      value='cm-display-stage'):
        for button in stage.find_elements(by=By.TAG_NAME, value='button'):
            if (button.get_attribute('color') == 'green' and
                    'play_arrow' in button.text):
                return [(''.join([RIGHT for _ in guess]), expected[0])]
    responses = []
    focus_key = None
    stage = driver.find_element(by=By.TAG_NAME, value='cm-word-stage')
    buttons = stage.find_elements(by=By.CLASS_NAME, value='key')
    for button in reversed(buttons):
        classes = button.get_attribute('class').split()
        if 'r2' in classes and 'k8' in classes:
            focus_key = button
            break
    while not (focus_key.text.split()[-1]).isnumeric():
        if 'ENTER' in focus_key.text:
            break
        focus_key.click()
        time.sleep(1)
        buttons = stage.find_elements(by=By.CLASS_NAME, value='key')
        for button in reversed(buttons):
            classes = button.get_attribute('class').split()
            if 'r2' in classes and 'k8' in classes:
                focus_key = button
                break
    for board in tqdm(expected, ascii=progress, leave=False):
        validate_wordzy_game(n_games, endless)
        # find the most recent response
        while not (focus_key.text.split()[-1]).isnumeric():
            if 'ENTER' in focus_key.text:
                break
            focus_key.click()
            time.sleep(0.5)
        if (('ENTER' not in focus_key.text and
             board != int(focus_key.text.split()[-1]) - 1) or
            ('ENTER' in focus_key.text and
             len(expected) > 1 and
             board == expected[-1] and
             guess in remaining[board])):
            responses.append((''.join(RIGHT for _ in guess), board))
            continue
        focused = stage.find_elements(by=By.CLASS_NAME, value='focused')
        if len(focused) == 0:
            focused = stage.find_element(by=By.TAG_NAME, value='cm-word-grid')
        else:
            focused = focused[0]
        stuck = False
        response = ''
        while len(response) != len(guess):
            if stuck:
                focused = stage.find_element(by=By.TAG_NAME,
                                             value='cm-word-grid')
            words = focused.find_elements(by=By.TAG_NAME, value='cm-word')
            for word in words:
                response = ''
                letters = word.find_elements(by=By.CLASS_NAME, value='letter')
                colors = letters
                if master:
                    colors = word.find_elements(by=By.CLASS_NAME, value='peg')
                entry = ''.join(x.text.strip() for x in letters).lower()
                if guess == entry:
                    for color in colors:
                        if 't1' in color.get_attribute('class').split():
                            response += WRONG
                        elif 't2' in color.get_attribute('class').split():
                            response += CLOSE
                        elif 't3' in color.get_attribute('class').split():
                            response += RIGHT
                    break
            stuck = True
        focus_key.click()
        time.sleep(0.125)
        responses.append((response, board))
    return responses


def auto_response_nordle(guess, remaining, entered, expected, hard, master,
                         endless):
    game = driver.find_element(by=By.ID, value='words')
    columns = list(game.find_elements(by=By.CLASS_NAME, value='column'))
    responses = []
    for board in tqdm(expected, ascii=progress, leave=False):
        response = ''
        for row in columns[board].find_elements(By.CLASS_NAME, 'guess'):
            word = ''.join(cell.text[0] for cell in
                           row.find_elements(By.CLASS_NAME, 'typed')).lower()
            if word == guess:
                for cell in row.find_elements(By.CLASS_NAME, 'typed'):
                    if 'green' in cell.get_attribute('class'):
                        response += RIGHT
                    elif 'yellow' in cell.get_attribute('class'):
                        response += CLOSE
                    else:
                        response += WRONG
                break
        responses.append((response, board))
    return responses


def auto_guess_wordle(remaining, guesses, best, hard, master, endless):
    global dialog_closed
    time.sleep(1)
    if not dialog_closed:
        game_app = driver.find_element(by=By.TAG_NAME, value='game-app')
        root = game_app.shadow_root
        modal = root.find_element(By.CSS_SELECTOR, '#game > game-modal')
        root = modal.shadow_root
        icon = root.find_element(By.CSS_SELECTOR, 'div > div > div')
        icon.click()
        dialog_closed = True
        time.sleep(1.5)
    webpage = driver.find_element(by=By.TAG_NAME, value='html')
    webpage.send_keys(best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(3)
    return best


def auto_response_wordle(guess, remaining, entered, expected, hard, master,
                         endless):
    response = ''
    game_app = driver.find_element(by=By.TAG_NAME, value='game-app')
    root = game_app.shadow_root
    board = root.find_element(By.CSS_SELECTOR, '#board')
    for game_row in board.find_elements(By.TAG_NAME, 'game-row'):
        if game_row.get_attribute('letters') == guess:
            root = game_row.shadow_root
            break
    row = root.find_element(by=By.CSS_SELECTOR, value='div')
    for tile in row.find_elements(by=By.TAG_NAME, value='game-tile'):
        evaluation = tile.get_attribute('evaluation')
        if evaluation == 'absent':
            response += WRONG
        elif evaluation == 'present':
            response += CLOSE
        elif evaluation == 'correct':
            response += RIGHT
    return [(response, 0)]


def auto_response_infinidle(guess, remaining, entered, expected, hard, master,
                            endless):
    driver.save_screenshot('infinidle/ss.png')
    pass


def auto_response_dordle(guess, remaining, entered, expected, hard, master,
                         endless):
    game = driver.find_element(by=By.XPATH, value='//*[@id="game"]')
    responses = []
    boards = list(game.find_elements(by=By.CLASS_NAME, value="table_guesses"))
    for board in expected:
        response = ''
        for row in boards[board].find_elements(by=By.TAG_NAME, value="tr"):
            if guess.upper() in ''.join(x.text for x in
                                        row.find_elements(by=By.TAG_NAME,
                                                          value="td")):
                for letter in row.find_elements(by=By.TAG_NAME, value="td"):
                    style = letter.get_attribute("style")
                    if 'var(--okc)' in style:
                        response += RIGHT
                    elif 'var(--nc2)' in style:
                        response += CLOSE
                    else:
                        response += WRONG
                break
        responses.append((response, board))
    return responses


def auto_response_quordle(guess, remaining, entered, expected, hard, master,
                          endless):
    responses = []
    boards = list(driver.find_elements(by=By.XPATH,
                                       value='//*[@role="table"]'))
    for board in expected:
        response = ''
        for row in boards[board].find_elements(by=By.XPATH,
                                               value='*[@role="row"]'):
            if guess.upper() in row.get_attribute("aria-label"):
                for letter in row.find_elements(by=By.XPATH,
                                                value='*[@role="cell"]'):
                    label = letter.get_attribute("aria-label")
                    if 'is correct' in label:
                        response += RIGHT
                    elif 'is incorrect' in label:
                        response += WRONG
                    else:
                        response += CLOSE
                break
        responses.append((response, board))
    return responses


def auto_response_duotrigordle(guess, remaining, entered, expected,
                               hard, master, endless):
    responses = []
    boards = list(driver.find_elements(by=By.CLASS_NAME, value="board"))
    for board in tqdm(expected, ascii=progress, leave=False):
        response = ''
        cells = boards[board].find_elements(by=By.CLASS_NAME, value="cell")
        index = (len(entered) - 1) * 5
        for cell in cells[index:index + 5]:
            label = cell.get_attribute("class")
            if 'green' in label:
                response += RIGHT
            elif 'yellow' in label:
                response += CLOSE
            else:
                response += WRONG
        responses.append((response, board))
    return responses


def auto_response_64ordle(guess, remaining, entered, expected, hard, master,
                          endless):
    responses = []
    boards = list(driver.find_element(by=By.ID,
                                      value="box-holder-{}".format(n + 1))
                  for n in range(len(remaining)))
    for board in tqdm(expected, ascii=progress, leave=False):
        response = ''
        for row in boards[board].find_elements(by=By.TAG_NAME, value="tr"):
            if guess.upper() in ''.join(x.text for x in
                                        row.find_elements(by=By.TAG_NAME,
                                                          value="td")):
                for letter in row.find_elements(by=By.TAG_NAME, value="td"):
                    style = letter.get_attribute("style")
                    if 'var(--green)' in style:
                        response += RIGHT
                    elif 'var(--yellow)' in style:
                        response += CLOSE
                    else:
                        response += WRONG
                break
        responses.append((response, board))
    return responses


###############################################################################
#           FUNCTIONS RELATED TO LAUNCHING AND CLOSING THIS PROGRAM           #
###############################################################################


def parse_command_line_args():
    parser = ArgumentParser(
        description=('Solve a Wordle game on one board or multiple by '
                     'calculating the best guesses at every step.'))
    parser.add_argument('-n', type=int, default=1,
                        help='number of simultaneous games (default: 1)')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-nyt', action='store_true',
                        help=('only consider answers that are in the New York '
                              'Times official word list'))
    group1.add_argument('-hard', action='store_true',
                        help='use if playing on hard mode (default: False)')
    group1.add_argument('-master', action='store_true',
                        help=('only set this flag if the game does '
                              'not tell you which colors belong to '
                              'which letters (default: False)'))
    group1.add_argument('-liar', action='store_true',
                        help=('use if playing Fibble where one letter in each '
                              'response is always a lie (default: False)'))
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('-auto', choices=['wordle', 'wordzy', 'dordle',
                                          'quordle', 'octordle', 'sedecordle',
                                          'duotrigordle', '64ordle', 'nordle'],
                        metavar='WEBSITE', default=None, dest='site',
                        help=('set this flag to automate play on the given '
                              'website (requires chromedriver) -- NOTE: '
                              'websites with a fixed number of boards will '
                              'override the N argument for number of boards '
                              "-- valid websites are: 'wordle', 'wordzy', "
                              "'dordle', 'quordle', 'octordle', 'sedecordle', "
                              "'duotrigordle', '64ordle', and 'nordle'"))
    group2.add_argument('-sim', type=int, default=0, metavar='MAX_SIMS',
                        help=('set this flag to simulate MAX_SIMS unique games'
                              ' and give resulting stats'))
    parser.add_argument('-quiet', action='store_true',
                        help='set this flag to hide unneeded console output')
    group3 = parser.add_mutually_exclusive_group()
    group3.add_argument('-continue', type=int, default=1,
                        metavar='LIMIT', dest='board_limit',
                        help=('set this flag to continue playing on multiple '
                              'boards up to the given number (max 1024) '
                              '-- setting the limit to "-1" will test all '
                              'possible starting words to find the best one(s)'
                              ' (be aware that this process may be very slow'))
    group3.add_argument('-endless', action='store_true', dest='inf',
                        help='use to play the same game over and over')
    group3.add_argument('-challenge', action='store_true', dest='stro',
                        help=('play the daily wordle, dordle, quordle, and '
                              'octordle in order, using the answers from each '
                              'puzzle as the starting words for the next ('
                              'inspired by YouTube channel Scott Stro-solves)')
                        )
    parser.add_argument('-best', action='store_true',
                        help=('set this flag to generate a minimal guess tree '
                              '(be aware that this process may be very slow) '
                              'once completed, the program will continue as '
                              'normal using the '))
    parser.add_argument('-start', metavar='WORD', nargs='+', default=[],
                        help=('set this flag if there are certain words you '
                              'want to start with regardless of the response'))
    args = parser.parse_args()
    lim = max(min(args.board_limit, 1024), args.n)
    ret = (args.n, args.hard, args.master, args.liar, args.site, lim, args.nyt,
           args.start, args.sim, args.inf, args.stro, args.best, args.quiet)
    return ret


def load_all_data(master, liar, nyt=False, allow_print=True):
    global response_data, response_data_updated
    if allow_print:
        print('Loading precalculated data...')
    freq_data = {}
    with open('data/freq_map.json', 'r') as data:
        freq_data = load(data)
    ans_file = 'data/nyt_answers.json' if nyt else 'data/curated_answers.json'
    answers = []
    with open(ans_file, 'r') as curated:
        answers = load(curated)
    guesses = []
    with open('data/allowed_guesses.txt', 'r') as allowed:
        guesses = load(allowed)
    nordle_guesses = []
    with open('data/allowed_nordle.json', 'r') as allowed:
        nordle_guesses = load(allowed)
    resp_file = 'data/responses' + ('_master' if master else '') + '.json'
    if is_ms_os or os.path.getsize(resp_file) < RS:
        with open(resp_file, 'r') as responses:
            response_data = load(responses)
            response_data_updated = False
    best_guess_file = 'data/best_guess.json'
    if nyt:
        best_guess_file = 'data/best_guess_nyt.json'
    elif hard:
        best_guess_file = 'data/best_guess_hard.json'
    elif master:
        best_guess_file = 'data/best_guess_master.json'
    elif liar:
        best_guess_file = 'data/best_guess_liar.json'
    saved_best = dict([(x, {}) for x in guesses])
    with open(best_guess_file, 'r') as bestf:
        saved_best = load(bestf)
    if allow_print:
        print('Finished loading.')
    return answers, guesses, nordle_guesses, freq_data, saved_best


def save_all_data(master, liar, nyt=False, allow_print=True):
    if allow_print:
        print('Saving all newly discovered data...')
    filename = 'data/best_guess.json'
    if nyt:
        filename = 'data/best_guess_nyt.json'
    elif hard:
        filename = 'data/best_guess_hard.json'
    elif master:
        filename = 'data/best_guess_master.json'
    elif liar:
        filename = 'data/best_guess_liar.json'
    if best_guess_updated:
        before = str(os.path.getsize(filename)) + 'B'
        with open(filename, 'w') as bestf:
            dump(saved_best, bestf, sort_keys=True, indent=2)
        after = str(os.path.getsize(filename)) + 'B'
        if allow_print:
            print('  "{}"  {:>8} > {:<8}'.format(filename, before, after))
    resp_file = 'data/responses' + ('_master' if master else '') + '.json'
    if response_data_updated and (is_ms_os or os.path.getsize(resp_file) < RS):
        before = str(os.path.getsize(resp_file)) + 'B'
        with open(resp_file, 'w') as responses:
            dump(response_data, responses, sort_keys=True)
        after = str(os.path.getsize(resp_file)) + 'B'
        if allow_print:
            print('  "{}"  {:>8} > {:<8}'.format(resp_file, before, after))
    if allow_print:
        print('Save complete.')


if __name__ == "__main__":
    # main variable initializations
    (n_games, hard, master, liar, site, lim, nyt,
     start, sim, inf, stro, best, quiet) = parse_command_line_args()
    (answers, guesses, n_guesses,
     freq, saved_best) = load_all_data(master, liar, nyt, not quiet)
    if best:
        tree = {}
        max_depth = 2
        while len(tree) == 0:
            tree = rec_build_best_tree(answers, guesses, start[0], master,
                                       liar, max_depth)
        with open('data/{}.json'.format(start[0]), 'w') as data:
            dump(tree, data, indent=2)
        saved_best = tree
    if inf:
        lim = n_games + 1
        if site == 'wordzy':
            n_games = 2
            lim = 256
    elif stro:
        n_games = 1
        lim = 8

    # setup for website auto-solve feature
    wordle_sites = {
        1: 'wordle',
        2: 'dordle',
        4: 'quordle',
        8: 'octordle',
        16: 'sedecordle',
        32: 'duotrigordle',
        64: '64ordle'
    }
    if site == 'wordle':
        if n_games in wordle_sites:
            site = wordle_sites[n_games]
        else:
            site = 'nordle'
    site_info = {
        'wordle': (
            'https://www.nytimes.com/games/wordle/index.html',
            1, False, auto_guess_wordle, auto_response_wordle
        ),
        'dordle': (
            'https://zaratustra.itch.io/dordle',
            2, False, auto_guess_default, auto_response_dordle
        ),
        'quordle': (
            'https://www.quordle.com/#/',
            4, False, auto_guess_default, auto_response_quordle
        ),
        'octordle': (
            'https://octordle.com/',
            8, False, auto_guess_default, auto_response_default
        ),
        'sedecordle': (
            'https://www.sedecordle.com/',
            16, False, auto_guess_default, auto_response_default
        ),
        'duotrigordle': (
            'https://duotrigordle.com/',
            32, False, auto_guess_default, auto_response_duotrigordle
        ),
        '64ordle': (
            'https://64ordle.au/',
            64, False, auto_guess_default, auto_response_64ordle,
        ),
        'nordle': (
            'https://www.nordle.us/?n=',
            0, False, auto_guess_default, auto_response_nordle
        ),
        'wordzy': (
            'https://wordzmania.com/Wordzy/',
            0, master, auto_guess_wordzy, auto_response_wordzy
        ),
        'infinidle': (
            'https://devbanana.itch.io/infinidle',
            1, False, auto_guess_default, auto_response_infinidle
        )
    }
    auto_guess = manual_guess
    auto_response = manual_response
    if site is not None:
        if site == 'wordzy' or site == 'nordle':
            addr, _, master, auto_guess, auto_response = site_info[site]
        else:
            addr, n_games, master, auto_guess, auto_response = site_info[site]
        n_games = open_website(addr, n_games, master, inf, quiet)

    # main functions to call
    if sim > 0:
        simulate(saved_best, freq, guesses, answers, start, n_games, hard,
                 master, liar, auto_guess, auto_response, sim, -8, not quiet)
        exit()
    elif sim == -1:
        best_case = [-8, []]
        worst_case = {}
        with open('data/ordered_guesses.json', 'r') as ordered:
            worst_case = load(ordered)
        modified = sorted(answers, key=lambda x: worst_case[x])
        for starter in tqdm(modified, ascii=progress):
            _, worst = simulate(saved_best, freq, guesses, answers,
                                [starter], n_games, hard, master, liar,
                                auto_guess, auto_response, len(answers),
                                best_case[0], False)
            if worst == best_case[0]:
                best_case[1].append(starter)
            elif worst > best_case[0]:
                best_case[0] = worst
                best_case[1] = [starter]
        print(best_case)
        exit()
    solution = [], []
    if site == 'nordle':
        solution = solve_wordle({}, freq, n_guesses, answers, start,
                                n_games, hard, master, liar, inf,
                                auto_guess, auto_response, not quiet)
    else:
        solution = solve_wordle(saved_best, freq, guesses, answers, start,
                                n_games, hard, master, liar, inf,
                                auto_guess, auto_response, not quiet)
    if quiet:
        score = n_games + 5 - len(solution[1]) - int(site == 'wordzy')
        print('\n  SOLUTION={}\n     SCORE={}\n'.format(solution[0], score))
    while n_games < lim:
        if site == 'wordzy':
            time.sleep(8)
            dx = driver.find_element(by=By.CLASS_NAME, value='share-container')
            for button in dx.find_elements(by=By.TAG_NAME, value='button'):
                if button.get_attribute('color') == 'green':
                    button.click()
                    if inf:
                        n_games += 1
                    else:
                        n_games *= 2
        elif site == 'quordle' and inf:
            time.sleep(8)
            driver.find_element(
                by=By.XPATH,
                value='//*[@id="root"]/div/div[1]/div/button[1]'
            ).click()
            time.sleep(2)
        elif (site is not None) and not (master or liar):
            time.sleep(8)
            driver.quit()
            if not inf:
                n_games *= 2
            if n_games not in wordle_sites:
                site = 'nordle'
                addr, _, master, auto_guess, auto_response = site_info[site]
            else:
                site = wordle_sites[n_games]
                (addr, n_games, master,
                 auto_guess, auto_response) = site_info[site]
            open_website(addr, n_games, master, inf, quiet)
        if stro:
            start = solution[0]
        if site == 'nordle':
            solution = solve_wordle({}, freq, n_guesses, answers, start,
                                    n_games, hard, master, liar, inf,
                                    auto_guess, auto_response, not quiet)
        else:
            solution = solve_wordle(saved_best, freq, guesses, answers, start,
                                    n_games, hard, master, liar, inf,
                                    auto_guess, auto_response, not quiet)
        if quiet:
            sol = solution[0]
            score = n_games + 5 - len(solution[1]) - int(site == 'wordzy')
            print('\n  SOLUTION={}\n     SCORE={}\n'.format(sol, score))
    save_all_data(master, liar, nyt, not quiet)
    if site is not None:
        input("PRESS ENTER TO EXIT")
        driver.quit()
