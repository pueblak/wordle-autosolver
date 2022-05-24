from math import ceil
import os
import time
from argparse import ArgumentParser
from math import log2
from random import sample, shuffle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from json import load, dump
from tqdm import tqdm


RIGHT = 'O'
CLOSE = 'H'
WRONG = 'X'

RS = 2**28  # file size limit (in bytes) for imports
response_data = {}
response_data_updated = False
best_guess_updated = False
is_ms_os = os.name == 'nt'
progress = '__...:::!!|' if is_ms_os else None
driver = None
auto_guess_count = 0
dialog_closed = False
simulated_answers = []


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


def filter_remaining(remaining, guess, response, master):
    filtered = []
    for answer in remaining:
        if get_response(guess, answer, master) == response:
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
    for guess in tqdm(guesses, leave=False, ascii=progress,
                      disable=(is_ms_os and not show)):
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


def best_avg_guesses(answers, guesses=[], master=False):
    if len(guesses) == 0:
        guesses = answers
    average = dict([(x, 0) for x in guesses])
    count = dict([(x, {}) for x in guesses])
    best_avg = len(answers)**2
    for guess in tqdm(guesses, leave=False, ascii=progress):
        for answer in answers:
            response = get_response(guess, answer, master)
            if response not in count[guess]:
                count[guess][response] = count_remaining(answers, guess,
                                                         response,
                                                         master=master)
            average[guess] += count[guess][response]
        if average[guess] < best_avg:
            best_avg = average[guess]
    best = [x for x in guesses if average[x] == best_avg]
    priority = set(best) & set(answers)
    if len(priority) > 0:
        return list(priority)
    return best


def expand_saved_best(saved, guesses, answers, master):
    print('Calculating best follow-up guess for each starting guess...')
    for guess1 in tqdm(saved.keys(), ascii=progress):
        for response1 in tqdm(saved[guess1].keys(), leave=False,
                              disable=is_ms_os):
            filtered1 = filter_remaining(answers, guess1, response1, master)
            best = saved[guess1][response1].keys()
            for guess2 in tqdm(best, leave=False, disable=is_ms_os):
                if len(saved[guess1][response1][guess2]) > 0:
                    continue
                saved[guess1][response1][guess2] = {}
                for answer in tqdm(filtered1, leave=False, disable=is_ms_os):
                    response2 = get_response(guess2, answer, master)
                    filtered2 = filter_remaining(filtered1, guess2,
                                                 response2, master)
                    if response2 not in saved[guess1][response1][guess2]:
                        saved[guess1][response1][guess2][response2] = dict(
                            [(guess, {}) for guess in
                             best_guesses(filtered2, guesses, master=master)]
                        )
    print('Finished calculating.')


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


def load_all_data(master):
    global response_data, response_data_updated
    print('Loading precalculated data...')
    freq_data = {}
    with open('data/freq_map.json', 'r') as data:
        freq_data = load(data)
    answers = []
    with open('data/curated_words.txt', 'r') as curated:
        for line in curated.readlines():
            answers.append(line.strip())
    guesses = []
    with open('data/allowed_words.txt', 'r') as allowed:
        for line in allowed.readlines():
            guesses.append(line.strip())
    guesses.sort(key=lambda x: freq_data[x], reverse=True)
    resp_file = 'data/responses' + ('_master' if master else '') + '.json'
    if is_ms_os or os.path.getsize(resp_file) < RS:
        with open(resp_file, 'r') as responses:
            response_data = load(responses)
            response_data_updated = False
    best_guess_file = 'data/best_guess.json'
    if master:
        best_guess_file = 'data/best_guess_master.json'
    saved_best = dict([(x, {}) for x in guesses])
    with open(best_guess_file, 'r') as bestf:
        saved_best = load(bestf)
    print('Finished loading.')
    return answers, guesses, freq_data, saved_best


def save_all_data(master):
    print('Saving all newly discovered data...')
    best_guess_file = 'data/best_guess.json'
    if master:
        best_guess_file = 'data/best_guess_master.json'
    if best_guess_updated:
        before = str(os.path.getsize(best_guess_file)) + 'B'
        with open(best_guess_file, 'w') as bestf:
            dump(saved_best, bestf, sort_keys=True, indent=2)
        after = str(os.path.getsize(best_guess_file)) + 'B'
        print('  "{}"  {:>8} > {:<8}'.format(best_guess_file, before, after))
    resp_file = 'data/responses' + ('_master' if master else '') + '.json'
    if response_data_updated and (is_ms_os or os.path.getsize(resp_file) < RS):
        before = str(os.path.getsize(resp_file)) + 'B'
        with open(resp_file, 'w') as responses:
            dump(response_data, responses, sort_keys=True)
        after = str(os.path.getsize(resp_file)) + 'B'
        print('  "{}"  {:>8} > {:<8}'.format(resp_file, before, after))
    print('Save complete.')


def solve_wordle(saved_best, freq, guesses, answers, starting_guesses,
                 num_boards, hard, master, auto_guess, auto_response,
                 allow_print=False):
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
    actual_best = 'ratio'
    if allow_print:
        print("\nBest starting guess is '{}'".format(actual_best))
    while any(len(r) > 1 for r in remaining):
        if num_boards > 1 and allow_print:
            print("\nSolved {:>2d}/{:<2d} boards: {}".format(solve_count,
                                                             num_boards,
                                                             solved))
        if any(x not in entered for x in starting_guesses):
            for guess in starting_guesses:
                if guess not in entered:
                    actual_best = guess
                    if allow_print:
                        print("  Predetermined guess is '{}'\n".format(guess))
                    break
        guess = auto_guess(remaining, guesses, actual_best, hard, master)
        entered.append(guess)
        best = [[] for _ in range(num_boards)]
        for response, board in auto_response(guess, remaining, entered,
                                             expected, hard, master):
            if len(remaining[board]) == 1:
                continue
            valid_answer = remaining[board][0]
            remaining[board] = filter_remaining(remaining[board], guess,
                                                response, master)
            rem = remaining[board]
            if len(rem) == 0:  # response does not match any known answers
                if allow_print:
                    print("\n\nBOARD {} USES A NEW WORD\n\n".format(board + 1))
                remaining[board] = guesses
                for entry in entered[:-1]:
                    resp = get_response(entry, valid_answer, master)
                    remaining[board] = filter_remaining(remaining[board],
                                                        entry, resp, master)
                remaining[board] = filter_remaining(remaining[board], guess,
                                                    response, master)
            if len(remaining[board]) == 0:  # response STILL does not match
                exit('ERROR: BAD RESPONSE ON BOARD {}: {}'.format(board + 1,
                                                                  response))
            if all(x == RIGHT for x in response) and board in expected:
                expected.remove(board)
            if num_boards > 1:
                for index in range(len(response)):
                    if all(r[index] == rem[0][index] for r in rem):
                        pattern = solved[board]
                        solved[board] = (pattern[:index] + rem[0][index]
                                         + pattern[index + 1:])
            best[board] = []
            # update subtree (and by extension, also saved_best)
            if guess not in subtree[board]:
                subtree[board][guess] = {}
                best_guess_updated = True
            subset = []  # decide which subset of words will be considered
            if response in subtree[board][guess]:
                subset = list(subtree[board][guess][response].keys())
            else:
                subtree[board][guess][response] = {}
                best_guess_updated = True
            if len(subset) == 0:
                subset = guesses  # default to the entire allowed word list
            if hard:
                for entry in entered:
                    resp = get_response(entry, remaining[board][0], False)
                    subset = filter_remaining(subset, entry, resp, False)
            best[board] = best_guesses(remaining[board], subset,
                                       master=master, show=allow_print)
            subtree[board] = subtree[board][guess][response]
            # print best guesses (or the answer) to the console
            if len(remaining[board]) == 1:
                solution = remaining[board][0]
                solved[board] = solution
                solve_count += 1
                if allow_print:
                    print("\n    The answer{} is '{}'\n".format(
                          '' if num_boards == 1 else
                          (' on board ' + str(board + 1)), solution))
            else:
                # update tree with best guesses if the game is still unsolved
                for best_guess in best[board]:
                    if best_guess not in subtree[board]:
                        subtree[board][best_guess] = {}
                        best_guess_updated = True
                best[board].sort(key=lambda x: freq[x], reverse=True)
                if allow_print:
                    print('  Best guess(es){}: {}'.format(
                        '' if num_boards == 1 else
                        (' on board ' + str(board + 1)),
                        str(best[board][:6])[1:-1]))
                    print('  {} possible answers{}'.format(len(rem),
                          (': ' + str(rem)[1:-1]) if (len(rem) <= 6) else ''))
        # make sure to guess any answers which have been found but not entered
        unentered_answers = (set(solved) & set(answers)) - set(entered)
        if len(unentered_answers) > 0 or solve_count < num_boards:
            best_score = len(guesses) * len(remaining)
            # sum collapses 2D list into 1D
            options = (sum(best, []) if len(unentered_answers) == 0
                       else unentered_answers)
            if len(options) == 1:
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
        if allow_print:
            print("\n  Your next guess should be '{}'".format(actual_best))
    if allow_print:
        print('\nSolve complete.\n')
    if len(unentered_answers) > 0 and auto_guess != manual_guess:
        if allow_print:
            print('Entering all remaining answers... ({} total)'.format(
                len(unentered_answers)))
        prev = len(solved) - len(unentered_answers)
        for index, answer in enumerate(unentered_answers):
            if allow_print:
                print("  Entering {:>4d}/{:<4d} '{}'".format(
                    prev + index + 1, prev + len(unentered_answers), answer
                ))
            if index == len(answers) - 1:
                time.sleep(3)  # pause for dramatic effect (and for wordzy)
            auto_guess(remaining, guesses, answer, hard, master)
            entered.append(answer)
    if len(solved) > 4 and auto_guess == manual_guess and allow_print:
        for index, answer in enumerate(solved):
            print("{:>4d}. {}".format(index + 1, answer))
    return num_boards + 5 - len(entered)


def manual_guess(remaining, guesses, best, hard, master):
    if hard:
        guesses = remaining[0]
    guess = input("What was your last guess?\n>>> ").strip().lower()
    while guess not in guesses:
        guess = input("Invalid guess. Try again.\n>>> ").strip().lower()
    return guess


def manual_response(guess, remaining, entered, expected, hard, master):
    for board in range(n_games):
        if len(remaining[board]) > 1:
            response = input(
                "What was the response" + (
                    "" if n_games == 1 else
                    " on board {}".format(board + 1)
                ) + "?\n>>> "
            ).strip().upper()
            rem = filter_remaining(remaining[board], guess, response,
                                   master)
            while (any(x not in (RIGHT, CLOSE, WRONG) for x in response)
                    or (len(rem) == 0) or (len(response) != len(guess))):
                response = input("Invalid response. Try again.\n>>> "
                                 ).strip().upper()
                rem = filter_remaining(remaining[board], guess, response,
                                       master)
            yield response, board


def simulated_guess(remaining, guesses, best, hard, master):
    return best


def simulated_response(guess, remaining, entered, expected, hard, master):
    global simulated_answers
    if len(entered) == 1 and len(simulated_answers) != len(remaining):
        simulated_answers = sample(remaining[0], len(remaining))
    responses = []
    for board in expected:
        responses.append(
            (get_response(guess, simulated_answers[board], master), board)
        )
    return responses


def simulate(saved, freq, guesses, answers, start, num_games, hard,
             master, auto_guess, auto_response, total_sims, best, show):
    global simulated_answers
    generated = []
    if num_games == 1:
        if total_sims < len(generated):
            generated = answers[:]
            shuffle(generated)
            generated = generated[:total_sims]
        else:
            worst_answers = ['fuzzy', 'epoxy', 'nymph', 'cynic', 'boozy',
                             'vivid', 'depot', 'movie', 'their', 'aroma',
                             'allow', 'tacit', 'swill', 'ferry', 'forgo',
                             'fewer', 'lowly', 'foyer', 'flair', 'foray',
                             'snout', 'bunny', 'hunky', 'funny', 'boxer',
                             'baker', 'place']
            generated += worst_answers
            generated += [ans for ans in answers if ans not in worst_answers]
    else:
        while len(generated) < total_sims:
            answer_list = ','.join(sample(answers, num_games))
            if answer_list not in generated:
                generated.append(answer_list)
    scores = {}
    starting = str(start)[1:-1]
    if show:
        print("Simulating {} unique games with starting word(s) {}...".format(
            len(generated), 'ratio' if starting == '' else starting))
    for answer_list in tqdm(generated, ascii=progress,
                            leave=False, disable=not show):
        simulated_answers = answer_list.split(',')
        score = solve_wordle(saved, freq, guesses, answers, start, num_games,
                             hard, master, simulated_guess, simulated_response,
                             False)
        if score < best and not show:
            return score, score
        if score not in scores:
            scores[score] = 0
        scores[score] += 1
    if show:
        print('\n\nSimulation complete.\n\n SCORE | COUNT | %TOTAL')
        for score in range(-12, 5):
            if score in scores:
                count = scores[score]
                print('\n{:^7d}|{:^7d}| {:<.6f}'.format(score, count,
                                                        count / total_sims))
        print()
    avg = sum(score * count for score, count in scores.items()) / total_sims
    worst = min(scores.keys())
    return avg, worst


###############################################################################
#          LOGIC FOR SOLVING GAMES AUTOMATICALLY ON VARIOUS WEBSITES          #
###############################################################################


def open_website(site, num_boards=1, master=False):
    global driver
    print("Connecting to the target website...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    if 'wordzmania' in site and master:
        site += 'Master'
    time.sleep(3)
    driver.get(site)
    print("Connected to '{}'.".format(site))
    time.sleep(5)
    if 'wordzmania' in site:  # must navigate to the correct page on this site
        num_boards = navigate_wordzy(num_boards)
    return num_boards


def navigate_wordzy(num_boards):
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
    play_button = driver.find_element(by=By.CLASS_NAME,
                                      value='play-button')
    play_button.click()
    print("Navigated to '{}'.".format(driver.current_url))
    return num_boards


def validate_wordzy_game(num_boards):
    stage = driver.find_elements(by=By.TAG_NAME, value='cm-game-stage')
    while len(stage) == 0:
        time.sleep(3)
        stage = driver.find_elements(by=By.TAG_NAME, value='cm-game-stage')
        if len(stage) > 0:
            break
        print('\n\n    ERROR: PAGE IS NOT RESPONDING - ATTEMPTING RELOAD...\n')
        time.sleep(7)
        if driver.current_url == 'https://wordzmania.com/Wordzy/Classic':
            navigate_wordzy(num_boards)
            time.sleep(5)


def auto_guess_wordzy(remaining, guesses, best, hard, master):
    global auto_guess_count, dialog_closed
    time.sleep(3)
    validate_wordzy_game(n_games)
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


def auto_response_wordzy(guess, remaining, entered, expected, hard, master):
    # check if game has ended
    validate_wordzy_game(n_games)
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
    for board in expected:
        validate_wordzy_game(n_games)
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


def auto_guess_nordle(remaining, guesses, best, hard, master):
    pass


def auto_response_nordle(guess, remaining, entered, expected, hard, master):
    pass


def auto_guess_wordle(remaining, guesses, best, hard, master):
    time.sleep(3)
    for modal in driver.find_elements(by=By.TAG_NAME, value='game-modal'):
        for icon in modal.find_elements(by=By.TAG_NAME, value='game-icon'):
            if icon.get_attribute('icon') == 'close':
                icon.click()
                time.sleep(1.5)
                break
    webpage = driver.find_element(by=By.TAG_NAME, value='html')
    webpage.send_keys(best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(2)
    return best


def auto_response_wordle(guess, remaining, entered, expected, hard, master):
    responses = []
    for row in driver.find_elements(by=By.TAG_NAME, value='game-row'):
        word = ''.join(tile.get_attribute('letter') for tile in
                       row.find_elements(by=By.TAG_NAME, value='game-tile'))
        if word == guess:
            response = ''
            for tile in row.find_elements(by=By.TAG_NAME, value='game-tile'):
                evaluation = tile.get_attribute('evaluation')
                if evaluation == 'absent':
                    response += WRONG
                elif evaluation == 'present':
                    response += CLOSE
                elif evaluation == 'correct':
                    response += RIGHT
            responses.append((response, 0))
            break
    return responses


def auto_guess_dordle(remaining, guesses, best, hard, master):
    pass


def auto_response_dordle(guess, remaining, entered, expected, hard, master):
    pass


def auto_guess_quordle(remaining, guesses, best, hard, master):
    pass


def auto_response_quordle(guess, remaining, entered, expected, hard, master):
    pass


def auto_guess_octordle(remaining, guesses, best, hard, master):
    pass


def auto_response_octordle(guess, remaining, entered, expected, hard, master):
    pass


def auto_guess_sedecordle(remaining, guesses, best, hard, master):
    pass


def auto_response_sedecordle(guess, remaining, entered, expected,
                             hard, master):
    pass


def auto_guess_duotrigordle(remaining, guesses, best, hard, master):
    pass


def auto_response_duotrigordle(guess, remaining, entered, expected,
                               hard, master):
    pass


def auto_guess_64ordle(remaining, guesses, best, hard, master):
    pass


def auto_response_64ordle(guess, remaining, entered, expected, hard, master):
    pass


def parse_command_line_args():
    parser = ArgumentParser(
        description=('Solve a Wordle game on one board or multiple by '
                     'calculating the best guesses at every step.'))
    parser.add_argument('-n', type=int, default=1,
                        help='number of simultaneous games (default: 1)')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-hard', action='store_true',
                        help='use if playing on hard mode (default: False)')
    group1.add_argument('-master', action='store_true',
                        help=('only set this flag if the game does '
                              'not tell you which colors belong to '
                              'which letters (default: False)'))
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('-auto', choices=['wordle', 'wordzy'],
                        metavar='WEBSITE', default=None, dest='site',
                        help=('set this flag to automate play on the given '
                              'website (requires chromedriver) -- NOTE: '
                              'websites with a fixed number of boards will '
                              'override the N argument for number of boards'))
    group2.add_argument('-simulate', type=int, default=0, dest='num_sims',
                        help=('set this flag to simulate all possible games '
                              'and give resulting stats'))
    parser.add_argument('-continue', type=int, default=1,
                        metavar='LIMIT', dest='board_limit',
                        help=('set this flag to continue playing on multiple '
                              'boards up to the given number (max 1024)'))
    parser.add_argument('-starters', metavar='WORD', nargs='+', default=[],
                        help=('set this flag if there are certain words you '
                              'want to start with regardless of the response'))
    args = parser.parse_args()
    limit = max(min(args.board_limit, 1024), args.n)
    ret_val = (args.n, args.hard, args.master, args.site,
               limit, args.starters, args.num_sims)
    return ret_val


if __name__ == "__main__":
    # main variable initializations
    n_games, hard, master, site, limit, start, sim = parse_command_line_args()
    answers, guesses, freq, saved_best = load_all_data(master)

    # setup for website auto-solve feature
    if site == 'wordle':
        if n_games == 1:
            site = 'wordle'
        elif n_games == 2:
            site = 'dordle'
        elif n_games == 4:
            site = 'quordle'
        elif n_games == 8:
            site = 'octordle'
        elif n_games == 16:
            site = 'sedecordle'
        elif n_games == 32:
            site = 'duotrigordle'
        elif n_games == 64:
            site = '64ordle'
        else:
            site = 'nordle'
    site_info = {
        'wordzy': (
            'https://wordzmania.com/Wordzy/',
            n_games, master, auto_guess_wordzy, auto_response_wordzy
        ),
        'wordle': (
            'https://www.nytimes.com/games/wordle/index.html',
            1, False, auto_guess_wordle, auto_response_wordle
        ),
        'dordle': (
            'https://zaratustra.itch.io/dordle',
            2, False, auto_guess_dordle, auto_response_dordle
        ),
        'quordle': (
            'https://www.quordle.com/',
            4, False, auto_guess_quordle, auto_response_quordle
        ),
        'octordle': (
            'https://octordle.com/',
            8, False, auto_guess_octordle, auto_response_octordle
        ),
        'sedecordle': (
            'https://www.sedecordle.com/',
            16, False, auto_guess_sedecordle, auto_response_sedecordle
        ),
        'duotrigordle': (
            'https://duotrigordle.com/',
            32, False, auto_guess_duotrigordle, auto_response_duotrigordle
        ),
        '64ordle': (
            'https://64ordle.au/',
            64, False, auto_guess_64ordle, auto_response_64ordle,
        ),
        'nordle': (
            'https://www.nordle.us/?n=' + str(n_games),
            n_games, False, auto_guess_nordle, auto_response_nordle
        )
    }
    auto_guess = manual_guess
    auto_response = manual_response
    if site is not None:
        addr, n_games, master, auto_guess, auto_response = site_info[site]
        n_games = open_website(addr, n_games, master)

    # optional functions to call
    # print(best_avg_guesses(answers, guesses, master))
    # print(best_guesses(answers, guesses, master=master, show=True))
    # calculate_best_guesses(saved_best, guesses, answers, master, 2000, 2150)
    # expand_saved_best(saved_best, guesses, answers, master)

    # main functions to call
    if sim > 0:
        simulate(saved_best, freq, guesses, answers, start, n_games,
                 hard, master, auto_guess, auto_response, sim, -8, True)
        save_all_data(master)
        exit()
    elif sim == -1:
        best_worst = [-8, []]
        worst_case = best_guesses(answers, guesses, master=master, show=True,
                                  return_all=True)
        modified = sorted(guesses, key=lambda x: worst_case[x])[:500]
        for starter in tqdm(modified, ascii=progress):
            _, worst = simulate(saved_best, freq, guesses, answers,
                                [starter], n_games, hard, master,
                                auto_guess, auto_response, len(answers),
                                best_worst[0], False)
            if worst == best_worst[0]:
                best_worst[1].append(starter)
            elif worst > best_worst[0]:
                best_worst[0] = worst
                best_worst[1] = [starter]
        print(best_worst)
        save_all_data(master)
        exit()
    solve_wordle(saved_best, freq, guesses, answers, start, n_games,
                 hard, master, auto_guess, auto_response)
    while n_games < limit:
        if site is not None and site == 'wordzy':
            time.sleep(5)
            dx = driver.find_element(by=By.CLASS_NAME, value='share-container')
            for button in dx.find_elements(by=By.TAG_NAME, value='button'):
                if button.get_attribute('color') == 'green':
                    button.click()
                    n_games *= 2
        solve_wordle(saved_best, freq, guesses, answers, start, n_games,
                     hard, master, auto_guess, auto_response)
    save_all_data(master)
