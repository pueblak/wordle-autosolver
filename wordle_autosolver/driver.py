import time  # pragma: no cover
from argparse import ArgumentParser  # pragma: no cover
from json import load, dump  # pragma: no cover
from traceback import print_exc  # pragma: no cover

from tqdm import tqdm  # pragma: no cover
from selenium.webdriver.common.by import By  # pragma: no cover

try:  # pragma: no cover
    from common import set_response_data, get_response_data, GameMode
    from common import get_best_guess_updated, get_response_data_updated
    from common import filter_remaining, PROGRESS, rec_build_best_tree
    from common import colored_response, best_guesses
    from solver import solve_wordle, manual_guess, manual_response
    from solver import simulate, simulated_response, SessionInfo
    from auto import SITE_INFO, open_website, get_driver, quit_driver
    from auto import auto_response_fibble, auto_read_fibble_start
    from data import load_all_data, save_all_data, clean_all_data
except ModuleNotFoundError:  # this is only here to help pytest find the module
    from wordle_autosolver.common import set_response_data, get_response_data
    from wordle_autosolver.common import get_best_guess_updated, GameMode
    from wordle_autosolver.common import get_response_data_updated, PROGRESS
    from wordle_autosolver.common import filter_remaining, best_guesses
    from wordle_autosolver.common import rec_build_best_tree, colored_response
    from wordle_autosolver.solver import solve_wordle, SessionInfo
    from wordle_autosolver.solver import manual_guess, manual_response
    from wordle_autosolver.solver import simulate, simulated_response
    from wordle_autosolver.auto import SITE_INFO, open_website, get_driver
    from wordle_autosolver.auto import quit_driver, auto_response_fibble
    from wordle_autosolver.auto import auto_read_fibble_start
    from wordle_autosolver.data import load_all_data, save_all_data
    from wordle_autosolver.data import clean_all_data


def parse_command_line_args() -> tuple[int, bool, bool, bool, str, int, bool,
                                       str, int, bool, bool, bool, bool]:
    """Parse all command line arguments using `argparse.ArgumentParser`."""
    parser = ArgumentParser(
        description=('Solve a Wordle game on one board or multiple by '
                     'calculating the best guesses at every step.'))
    parser.add_argument('--num', type=int, default=1,
                        help='number of simultaneous games (default: 1)')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('--nyt', action='store_true', default=False,
                        help=('only consider answers that are in the New York '
                              'Times official word list'))
    group1.add_argument('--hard', action='store_true', default=False,
                        help='use if playing on hard mode (default: False)')
    group1.add_argument('--master', action='store_true', default=False,
                        help=('only set this flag if the game does '
                              'not tell you which colors belong to '
                              'which letters (default: False)'))
    group1.add_argument('--liar', action='store_true', default=False,
                        help=('use if playing Fibble where one letter in each '
                              'response is always a lie (default: False)'))
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('--play', action='store_true',
                        help=('set this flag to play a game of Wordle using '
                              'the command line'))
    group2.add_argument('--auto', choices=['wordle', 'wordzy', 'dordle',
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
    group2.add_argument('--sim', type=int, default=0, metavar='MAX_SIMS',
                        help=('set this flag to simulate MAX_SIMS unique games'
                              ' and give resulting stats'))
    parser.add_argument('--quiet', action='store_true',
                        help='set this flag to hide unneeded console output')
    group3 = parser.add_mutually_exclusive_group()
    group3.add_argument('--continue', type=int, default=1,
                        metavar='LIMIT', dest='board_limit',
                        help=('set this flag to continue playing on multiple '
                              'boards up to the given number (max 500) '
                              '-- setting the limit to "-1" will test all '
                              'possible starting words to find the best one(s)'
                              ' (be aware that this process may be very slow)')
                        )
    group3.add_argument('--endless', action='store_true', dest='inf',
                        help='use to play the same game over and over')
    group3.add_argument('--challenge', action='store_true', dest='stro',
                        help=('play the daily wordle, dordle, quordle, and '
                              'octordle in order, using the answers from each '
                              'puzzle as the starting words for the next ('
                              'inspired by YouTube channel Scott Stro-solves)')
                        )
    parser.add_argument('--best', action='store_true',
                        help=('set this flag to generate a minimal guess tree '
                              '(be aware that this process may be very slow) '
                              'once completed, the program will continue as '
                              'normal using this generated tree to recommend '
                              'guesses'))
    parser.add_argument('--clean', action='store_true',
                        help=('empty the contents of "data/best_guess.json", '
                              '"data/responses.json", and each of their '
                              'variants to relieve some storage space (the '
                              'program will not execute any other commands '
                              'when this flag is set)'))
    parser.add_argument('--light', action='store_true',
                        help=('set this flag to force all websites to switch '
                              'to light mode (if available) -- when "auto" '
                              'is not set, this flag is ignored'))
    parser.add_argument('--start', metavar='WORD', nargs='+', default=[],
                        help=('set this flag if there are certain words you '
                              'want to start with regardless of the response'))
    args = parser.parse_args()
    if args.clean:  # pragma: no cover
        clean_all_data()
        exit()
    lim = max(min(args.board_limit, 500), args.num)
    mode = GameMode()
    if args.hard:
        mode.hard = True
    elif args.master:
        mode.master = True
    elif args.liar:
        mode.liar = True
    if args.play:
        mode.play = True
    if args.inf:
        mode.endless = True
    return (args.num, lim, mode, args.site, args.nyt, args.start, args.sim,
            args.stro, args.best, args.quiet, not args.light)


def main() -> None:  # pragma: no cover
    """Main entry point into the program."""
    # main variable initializations
    (n_games, lim, mode, site, nyt, start,
        sim, stro, best, quiet, dark) = parse_command_line_args()
    (answers, guesses, nordle_guesses, freq,
        saved_best, resp_data) = load_all_data(mode.hard, mode.master,
                                               mode.liar, nyt, not quiet)
    set_response_data(resp_data)

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
        if mode.liar:
            site = 'fibble'
    auto_guess = manual_guess
    auto_response = simulated_response if mode.play else manual_response
    if site is not None:
        if site == 'wordle':
            (addr, n_games, _, mode.master, mode.liar,
                auto_guess, auto_response) = SITE_INFO[site]
        elif site == 'wordzy':
            (addr, _, mode.hard, _, mode.liar,
                auto_guess, auto_response) = SITE_INFO[site]
        elif site == 'nordle':
            (addr, _, mode.hard, mode.master, mode.liar,
                auto_guess, auto_response) = SITE_INFO[site]
        elif site == 'fibble':
            (addr, n_games, mode.hard, mode.master, mode.liar,
                auto_guess, auto_response) = SITE_INFO[site]
        else:
            (addr, n_games, mode.hard, mode.master, mode.liar,
                auto_guess, auto_response) = SITE_INFO[site]
        n_games = open_website(addr, n_games, mode, quiet=quiet, dark=dark)
        lim = max(lim, n_games)
    if mode.endless:
        lim = n_games + 1
        if site == 'wordzy':
            n_games = 2
            lim = 256  # the website struggles to respond around this point
    elif stro:
        n_games = 1
        lim = 8

    # main functions to call
    if best:
        tree = {}
        max_depth = 2
        while len(tree) == 0:
            tree = rec_build_best_tree(answers, guesses, start[0],
                                       mode, max_depth)
        with open('data/{}.json'.format(start[0]), 'w') as data:
            dump(tree, data, indent=2)
        saved_best = tree
    if sim > 0:
        session = SessionInfo(n_games, answers, guesses, saved_best, freq,
                              start, mode)
        simulate(session, sim, show=not quiet)
    elif sim == -1:
        best_case = -8
        best_start = []
        worst_case = {}
        with open('data/ordered_guesses.json', 'r') as ordered:
            worst_case = load(ordered)
        modified = sorted(answers, key=lambda x: worst_case[x])
        for starter in tqdm(modified, ascii=PROGRESS):
            session = SessionInfo(n_games, answers, guesses, saved_best, freq,
                                  [starter], mode)
            _, worst = simulate(session, len(answers), best_case, show=False,
                                return_if_worse=True)
            if worst == best_case:
                best_start.append(starter)
            elif worst > best_case:
                best_case = worst
                best_start = [starter]
        print(best_case, '=', best_start)
    if sim != 0:
        save_all_data(session.hard, session.master, session.liar,
                      get_best_guess_updated(), saved_best,
                      get_response_data_updated(), get_response_data(), nyt,
                      not quiet)
        exit()
    solution = [], []
    while n_games <= lim:
        session = SessionInfo(n_games, answers, guesses, saved_best, freq,
                              start, mode)
        if site == 'fibble':
            guess = (manual_guess(session) if auto_guess == manual_guess
                     else auto_read_fibble_start())
            session.entered.append(guess)
            session.guesses.remove(guess)
            response = (manual_response(session) if auto_guess == manual_guess
                        else auto_response_fibble(session))[0][0]
            filtered = filter_remaining(answers, guess, response, mode)
            session.remaining[0] = filtered
            if not quiet:
                print(('\n  Given word is: {}\n  with response: {}\n'
                       '    {} possible answers').format(
                    guess.upper(),
                    colored_response(guess, response, mode),
                    len(filtered)
                ))
            session.actual_best = best_guesses(filtered, session.guesses,
                                               session.mode, show=True)[0]
        elif site == 'nordle':
            session.saved_best = {}
            session.guesses = nordle_guesses
        try:
            session = solve_wordle(session, auto_guess, auto_response,
                                   not quiet)
        except Exception:
            print_exc()
            print()
            print(session)
            exit(1)
        solution = session.solved, session.entered
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
                    if mode.endless:
                        n_games += 1
                    else:
                        n_games *= 2
        elif site == 'dordle' and mode.endless:
            time.sleep(4)
            get_driver().find_element(value='new_game').click()
            time.sleep(2)
        elif site == 'quordle' and mode.endless:
            time.sleep(4)
            get_driver().find_element(
                by=By.XPATH,
                value='//*[@id="root"]/div/div[1]/div/button[1]'
            ).click()
            time.sleep(2)
        elif (site is not None) and not (mode.master or mode.liar):
            time.sleep(8)
            quit_driver()
            if not mode.endless:
                n_games *= 2
            if n_games not in wordle_sites:
                site = 'nordle'
                addr, _, _, _, _, auto_guess, auto_response = SITE_INFO[site]
                session.saved_best = {}
                session.guesses = nordle_guesses
            else:
                site = wordle_sites[n_games]
                if not mode.hard and site == 'wordle':
                    (addr, n_games, _, mode.master, mode.liar,
                     auto_guess, auto_response) = SITE_INFO[site]
                elif site == 'wordzy':
                    (addr, _, mode.hard, _, mode.liar,
                     auto_guess, auto_response) = SITE_INFO[site]
                else:
                    (addr, n_games, mode.hard, mode.master, mode.liar,
                     auto_guess, auto_response) = SITE_INFO[site]
            open_website(addr, n_games, mode, quiet=quiet, dark=dark)
        elif site is not None and mode.liar and mode.endless:
            get_driver().find_element(
                By.XPATH, '//*[@id="root"]/div/div[3]/div[1]/span[2]/a'
            ).click()
            time.sleep(2)
        if stro:
            start = solution[0]
    save_all_data(mode.hard, mode.master, mode.liar, get_best_guess_updated(),
                  saved_best, get_response_data_updated(), get_response_data(),
                  nyt, not quiet)
    if site is not None:
        input("PRESS ENTER TO EXIT")
        quit_driver()
