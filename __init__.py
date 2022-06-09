import os
import time
from argparse import ArgumentParser
from json import load, dump

from tqdm import tqdm

from common import *
from solver import *
from auto import *


RS = 2**26  # file size limit (in bytes) for imports


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
