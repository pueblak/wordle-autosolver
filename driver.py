import time
from argparse import ArgumentParser
from json import load, dump

from tqdm import tqdm


try:
    from common import *
    from solver import *
    from auto import *
    from data import *
except ImportError as e:
    from .common import *
    from .solver import *
    from .auto import *
    from .data import *


def parse_command_line_args() -> tuple[int, bool, bool, bool, str, int, bool,
                                       str, int, bool, bool, bool, bool]:
    """Parse all command line arguments using `argparse.ArgumentParser`."""
    parser = ArgumentParser(
        description=('Solve a Wordle game on one board or multiple by '
                     'calculating the best guesses at every step.'))
    parser.add_argument('-n', type=int, default=1,
                        help='number of simultaneous games (default: 1)')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-nyt', action='store_true', default=False,
                        help=('only consider answers that are in the New York '
                              'Times official word list'))
    group1.add_argument('-hard', action='store_true', default=False,
                        help='use if playing on hard mode (default: False)')
    group1.add_argument('-master', action='store_true', default=False,
                        help=('only set this flag if the game does '
                              'not tell you which colors belong to '
                              'which letters (default: False)'))
    group1.add_argument('-liar', action='store_true', default=False,
                        help=('use if playing Fibble where one letter in each '
                              'response is always a lie (default: False)'))
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('-auto', choices=['wordle', 'wordzy', 'dordle',
                                          'quordle', 'octordle', 'sedecordle',
                                          'duotrigordle', '64ordle', 'nordle',
                                          'fibble'],
                        metavar='WEBSITE', default=None, dest='site',
                        help=('set this flag to automate play on the given '
                              'website (requires chromedriver) -- NOTE: '
                              'websites with a fixed number of boards will '
                              'override the N argument for number of boards '
                              "-- valid websites are: 'wordle', 'wordzy', "
                              "'dordle', 'quordle', 'octordle', 'sedecordle', "
                              "'duotrigordle', '64ordle', 'nordle', and "
                              "'fibble'"))
    group2.add_argument('-sim', type=int, default=0, metavar='MAX_SIMS',
                        help=('set this flag to simulate MAX_SIMS unique games'
                              ' and give resulting stats'))
    parser.add_argument('-quiet', action='store_true',
                        help='set this flag to hide unneeded console output')
    group3 = parser.add_mutually_exclusive_group()
    group3.add_argument('-continue', type=int, default=1,
                        metavar='LIMIT', dest='board_limit',
                        help=('set this flag to continue playing on multiple '
                              'boards up to the given number (max 500) '
                              '-- setting the limit to "-1" will test all '
                              'possible starting words to find the best one(s)'
                              ' (be aware that this process may be very slow)')
                        )
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
    parser.add_argument('-clean', action='store_true',
                        help=('empty the contents of "data/best_guess.json", '
                              '"data/responses.json", and each of their '
                              'variants to relieve some storage space (the '
                              'program will not execute any other commands '
                              'when this flag is set)'))
    parser.add_argument('-start', metavar='WORD', nargs='+', default=[],
                        help=('set this flag if there are certain words you '
                              'want to start with regardless of the response'))
    args = parser.parse_args()
    if args.clean:
        clean_all_data()
        exit()
    lim = max(min(args.board_limit, 500), args.n)
    ret = (args.n, args.hard, args.master, args.liar, args.site, lim, args.nyt,
           args.start, args.sim, args.inf, args.stro, args.best, args.quiet)
    return ret


def main():
    # main variable initializations
    (n_games, hard, master, liar, site, lim, nyt,
        start, sim, inf, stro, best, quiet) = parse_command_line_args()
    (answers, guesses, n_guesses, freq,
        saved_best, resp_data) = load_all_data(hard, master, liar, nyt,
                                               not quiet)
    if len(resp_data) == 0:
        precalculate_responses(guesses, answers, master)
    set_response_data(resp_data)
    if best:
        tree = {}
        max_depth = 2
        while len(tree) == 0:
            tree = rec_build_best_tree(answers, guesses, start[0], master,
                                       liar, max_depth)
        with open('data/{}.json'.format(start[0]), 'w') as data:
            dump(tree, data, indent=2)
        saved_best = tree

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
        if liar:
            site = 'fibble'
    auto_guess = manual_guess
    auto_response = manual_response
    if site is not None:
        if not hard and site == 'wordle':
            (addr, n_games, _, master, liar,
                auto_guess, auto_response) = SITE_INFO[site]
        elif site == 'wordzy':
            (addr, _, hard, _, liar,
                auto_guess, auto_response) = SITE_INFO[site]
        elif site == 'nordle':
            (addr, _, hard, master, liar,
                auto_guess, auto_response) = SITE_INFO[site]
        else:
            (addr, n_games, hard, master, liar,
                auto_guess, auto_response) = SITE_INFO[site]
        n_games = open_website(addr, n_games, master, inf, quiet)
        lim = max(lim, n_games)
    if inf:
        lim = n_games + 1
        if site == 'wordzy':
            n_games = 2
            lim = 256  # the website struggles to respond around this point
    elif stro:
        n_games = 1
        lim = 8

    # main functions to call
    if sim > 0:
        simulate(saved_best, freq, answers, guesses, start, n_games, hard,
                 master, liar, sim, show=not quiet)
        exit()
    elif sim == -1:
        best_case = [-8, []]
        worst_case = {}
        with open('data/ordered_guesses.json', 'r') as ordered:
            worst_case = load(ordered)
        modified = sorted(answers, key=lambda x: worst_case[x])
        for starter in tqdm(modified, ascii=progress):
            _, worst = simulate(saved_best, freq, answers, guesses,
                                [starter], n_games, hard, master, liar,
                                len(answers), best_case[0], False)
            if worst == best_case[0]:
                best_case[1].append(starter)
            elif worst > best_case[0]:
                best_case[0] = worst
                best_case[1] = [starter]
        print(best_case)
        exit()
    solution = [], []
    while n_games <= lim:
        if site == 'fibble':
            guess = (manual_guess(answers, guesses, 'lying', False, False, inf)
                     if auto_guess == manual_guess
                     else auto_read_fibble_start())
            response = (manual_response(guess, answers, [], [0],
                                        False, False, False, inf)
                        if auto_guess == manual_guess else
                        auto_response_fibble(guess, answers, [], [0],
                                             False, False, False, inf))[0][0]
            filtered = filter_remaining(answers, guess, response, False, True)
            solution = solve_wordle(saved_best, freq, filtered, guesses, start,
                                    n_games, hard, master, liar, inf,
                                    auto_guess, auto_response, not quiet)
        elif site == 'nordle':
            solution = solve_wordle({}, freq, answers, n_guesses, start,
                                    n_games, hard, master, liar, inf,
                                    auto_guess, auto_response, not quiet)
        else:
            solution = solve_wordle(saved_best, freq, answers, guesses, start,
                                    n_games, hard, master, liar, inf,
                                    auto_guess, auto_response, not quiet)
        if quiet:
            sol = solution[0]
            score = n_games + 5 - len(solution[1]) - int(site == 'wordzy')
            print('\n  SOLUTION={}\n     SCORE={}\n'.format(sol, score))
        if n_games == lim:
            break
        if site == 'wordzy':
            time.sleep(8)
            dx = get_driver().find_element(By.CLASS_NAME, 'share-container')
            for button in dx.find_elements(by=By.TAG_NAME, value='button'):
                if button.get_attribute('color') == 'green':
                    button.click()
                    if inf:
                        n_games += 1
                    else:
                        n_games *= 2
        elif site == 'dordle' and inf:
            time.sleep(4)
            get_driver().find_element(value='new_game').click()
            time.sleep(2)
        elif site == 'quordle' and inf:
            time.sleep(4)
            get_driver().find_element(
                by=By.XPATH,
                value='//*[@id="root"]/div/div[1]/div/button[1]'
            ).click()
            time.sleep(2)
        elif (site is not None) and not (master or liar):
            time.sleep(8)
            quit_driver()
            if not inf:
                n_games *= 2
            if n_games not in wordle_sites:
                site = 'nordle'
                addr, _, _, _, _, auto_guess, auto_response = SITE_INFO[site]
            else:
                site = wordle_sites[n_games]
                if not hard and site == 'wordle':
                    (addr, n_games, _, master, liar,
                     auto_guess, auto_response) = SITE_INFO[site]
                elif site == 'wordzy':
                    (addr, _, hard, _, liar,
                     auto_guess, auto_response) = SITE_INFO[site]
                else:
                    (addr, n_games, hard, master, liar,
                     auto_guess, auto_response) = SITE_INFO[site]
            open_website(addr, n_games, master, inf, quiet)
        elif site is not None and liar and inf:
            get_driver().find_element(
                By.XPATH, '//*[@id="root"]/div/div[3]/div[1]/span[2]/a'
            ).click()
            time.sleep(2)
        if stro:
            start = solution[0]
    save_all_data(hard, master, liar, get_best_guess_updated(), saved_best,
                  get_response_data_updated(), get_response_data(), nyt,
                  not quiet)
    if site is not None:
        input("PRESS ENTER TO EXIT")
        quit_driver()


if __name__ == '__main__':
    main()
