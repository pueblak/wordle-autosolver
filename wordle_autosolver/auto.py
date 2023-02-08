import os
import time
from math import ceil, log2
from typing import Optional

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

try:  # pragma: no cover
    from common import RIGHT, CLOSE, WRONG, PROGRESS, GameMode, IS_MS_OS
    from solver import SessionInfo
except ModuleNotFoundError:  # this is only here to help pytest find the module
    from wordle_autosolver.common import RIGHT, CLOSE, WRONG, PROGRESS
    from wordle_autosolver.common import GameMode, IS_MS_OS
    from wordle_autosolver.solver import SessionInfo


# Note: The following values come from the default installation locations
# used by GitHub-hosted runners
CHROMEPATH_WINDOWS = ('C:/Program Files (x86)/Google/Chrome/Application'
                      '/chrome.exe')
CHROMEDRIVERPATH_WINDOWS = ('C:/SeleniumWebDrivers/ChromeDriver'
                            '/chromedriver.exe')
CHROMEPATH_LINUX = '/usr/bin/google-chrome'
CHROMEDRIVERPATH_LINUX = '/usr/local/share/chrome_driver/chromedriver.exe'

_driver: webdriver.Chrome = None
_auto_guess_count: int = 0
_dialog_closed: bool = False


def get_driver() -> webdriver.Chrome:
    """Returns the current webdriver instance."""
    return _driver


def quit_driver() -> None:
    """Quits the current webdriver instance."""
    if _driver is not None:
        _driver.quit()


def open_website(website: str, num_boards: int = 1,
                 mode: Optional[GameMode] = None,
                 *, quiet: bool = False, dark: bool = True) -> int:
    """Opens the requested website based on the given parameters.

    Args:
        website:
            The URL of the website to be opened
        num_boards:
            The number of simultaneous games being played (each guess is made
            across all boards at once) (default: 1)
        mode:
            A GameMode class instance representing the current game mode
            (default: None)

    Keyword Args:
        quiet:
            A boolean value representing whether to print any messages to the
            console (default: False)
        dark:
            A boolean value representing whether the website should change to
            dark mode, if available (default: True)

    Returns:
        The number of boards used by the website. This should normally be the
        same value as `num_boards`, but there are some cases where the chosen
        website cannot play that exact number of games, so be sure to verify
        this result before using the number of boards requested by the user.
    """
    global _driver
    if mode is None:
        mode = GameMode()
    if not quiet:
        print("\nConnecting to the target website...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # go fullscreen
    # stop unexpected messages being printed to the console from the webdriver
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--log-level=3")
    if dark:
        options.add_argument('--force-dark-mode')
    if quiet:  # do not open an actual browser -- do it all behind-the-scenes
        options.add_argument('--headless')
    # exit any driver that was being used before and reinitialize it
    quit_driver()
    bin_path = CHROMEPATH_WINDOWS if IS_MS_OS else CHROMEPATH_LINUX
    if os.path.exists(bin_path):
        options.binary_location = bin_path
    exe_path = CHROMEDRIVERPATH_WINDOWS if IS_MS_OS else CHROMEDRIVERPATH_LINUX
    if os.path.exists(exe_path):
        _driver = webdriver.Chrome(executable_path=exe_path, options=options)
    else:
        _driver = webdriver.Chrome(options=options)
    # alter the URL if necessary to play the correct version of the chosen game
    if 'wordzmania' in website and mode.master:
        website += 'Master'
    time.sleep(3)
    if any(x in website for x in ('sedecordle', '64ordle')):
        website += '?mode=' + ('free' if mode.endless else 'daily')
    elif 'octordle' in website:
        website += 'free' if mode.endless else 'daily'
    elif 'quordle' in website and mode.endless:
        website += 'practice'
    elif 'fibble' in website and mode.endless:
        website += '?unlimited'
    elif 'nordle' in website:
        website += str(num_boards)
    _driver.get(website)  # this is when it attempts to connect to the website
    if not quiet:
        print("Connected to '{}'".format(website))
    time.sleep(3)  # give the page elements a few seconds to load
    # must navigate to the correct page on some websites
    if 'wordzmania' in website:
        num_boards = navigate_wordzy(num_boards, mode.endless, quiet=quiet)
    elif 'dordle' in website:
        navigate_dordle(mode.endless, dark_mode=dark)
    elif 'wordle' in website:
        navigate_wordle(mode.hard)
    elif 'octordle' in website:
        navigate_octordle(dark_mode=dark)
    time.sleep(4)
    return num_boards


###############################################################################
#                   HELPER FUNCTIONS FOR SPECIFIC WEBSITES                    #
###############################################################################


def navigate_wordle(hard: bool) -> None:
    """Navigates the Wordle website before beginning the solve."""
    close_icon_xpath = '/html/body/div/div/dialog/div/button'
    close_icon = _driver.find_element(by=By.XPATH, value=close_icon_xpath)
    close_icon.click()
    time.sleep(1.5)
    if hard:
        _driver.find_element(value='settings-button').click()
        time.sleep(0.5)
        _driver.find_element(value='hardMode').click()
        close_settings_xpath = '/html/body/div/div/dialog/div/button'
        time.sleep(0.25)
        _driver.find_element(by=By.XPATH, value=close_settings_xpath).click()
        time.sleep(0.5)


def navigate_dordle(endless: bool, *, dark_mode: bool = True) -> None:
    """Navigates the Dordle website before beginning the solve."""
    iframe = _driver.find_element(by=By.XPATH, value='//*[@id="game_drop"]')
    _driver.switch_to.frame(iframe)
    _driver.find_element(value='free' if endless else 'daily').click()
    if dark_mode:
        _driver.find_element(By.XPATH, '//*[@id="body"]/table/tbody/tr/td[5]'
                             ).click()
        _driver.find_element(By.XPATH,
                             '//*[@id="options"]/div[4]/table/tbody/tr/td[3]'
                             ).click()
        _driver.find_element(By.XPATH, '//*[@id="body"]/table/tbody/tr/td[5]'
                             ).click()
    time.sleep(1)


def navigate_octordle(*, dark_mode: bool = True):
    """Navigates the Octordle website before beginning the solve."""
    if not dark_mode:
        _driver.find_element(
            By.XPATH, '//*[@id="header"]/div[1]/a[3]'
        ).click()
        time.sleep(1)
        color = _driver.find_element(
            By.XPATH, '//*[@id="body"]/div/div[2]/div[2]/a'
        )
        while color.text != 'Light':
            color.click()
            time.sleep(0.5)
        _driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/a[2]').click()
        time.sleep(1)


def navigate_wordzy(num_boards: int, endless: bool, *, quiet: bool = False
                    ) -> int:
    """Navigates the Wordzy website before beginning the solve."""
    play_buttons = _driver.find_elements(by=By.CLASS_NAME,
                                         value='play-button')
    time.sleep(4)
    if not endless:
        select_button = _driver.find_element(by=By.CLASS_NAME,
                                             value='stake-selector')
        select_button.click()
        time.sleep(2)
        listbox = _driver.find_element(by=By.CLASS_NAME,
                                       value='mat-select-panel')
        lo = 9999
        for element in listbox.find_elements(by=By.CLASS_NAME,
                                             value='mat-option'):
            lo = min(lo, int(str(element.get_attribute('id')).split('-')[-1]))
        num = str(lo + ceil(log2(min(num_boards, 1024))))
        board_num_select = _driver.find_element(by=By.ID,
                                                value='mat-option-' + num)
        while not board_num_select.get_attribute('aria-disabled'):
            num = str(int(num) - 1)
            board_num_select = _driver.find_element(by=By.ID,
                                                    value='mat-option-' + num)
        num_boards = 2 ** (int(num) - lo)
        board_num_select.click()
        time.sleep(2)
        play_buttons[0].click()
    else:
        play_buttons[1].click()
    if not quiet:  # pragma: no cover
        print("Navigated to '{}'.".format(_driver.current_url))
    return num_boards


def validate_wordzy_game(num_boards: int, endless: bool):  # pragma: no cover
    """Checks if the Wordzy website is behaving correctly."""
    stage = _driver.find_elements(by=By.TAG_NAME, value='cm-game-stage')
    while len(stage) == 0:
        time.sleep(3)
        stage = _driver.find_elements(by=By.TAG_NAME, value='cm-game-stage')
        if len(stage) > 0:
            break
        print('\n\n    ERROR: PAGE IS NOT RESPONDING - ATTEMPTING RELOAD...\n')
        time.sleep(7)
        if _driver.current_url == 'https://wordzmania.com/Wordzy/Classic':
            navigate_wordzy(num_boards, endless)
            time.sleep(5)


def auto_read_fibble_start() -> str:
    """Reads and returns the starting guess before beginning the solve."""
    guess = ''
    row = _driver.find_element(by=By.CLASS_NAME, value='Row')
    for letter in row.find_elements(by=By.CLASS_NAME, value='Row-letter'):
        guess += letter.get_attribute('aria-label').split(':')[0]
    return guess.lower()


###############################################################################
#                   AUTO_GUESS AND AUTO_RESPONSE FUNCTIONS                    #
###############################################################################


def auto_guess_default(session: SessionInfo) -> str:
    """Enters `best` into the webpage and ignores all other arguments.

    This is the default `auto_guess` function. Currently used on the following
    websites: "wordle", "dordle", "quordle", "octordle", "sedecordle",
    "duotrigordle", "64ordle", "nordle", and "fibble".

    Returns:
        The word which was selected as the guess.
    """
    webpage = _driver.find_element(by=By.TAG_NAME, value='html')
    time.sleep(0.5)
    webpage.send_keys(session.actual_best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(1)
    return session.actual_best


def auto_response_default(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the current webpage.

    This is the default `auto_response` function. Currently used on the
    following websites: "octordle" and "sedecordle".

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    guess = session.entered[-1]
    responses = []
    boards = list(_driver.find_element(by=By.ID,
                                       value="box-holder-{}".format(n + 1))
                  for n in range(len(session.remaining)))
    for board in tqdm(session.expected, ascii=PROGRESS, leave=False):
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


def auto_guess_wordzy(session: SessionInfo) -> str:
    """Enters `best` into the current Wordzy game.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        The word which was selected as the guess.
    """
    global _auto_guess_count, _dialog_closed
    time.sleep(3)
    validate_wordzy_game(len(session.remaining), session.mode.endless)
    for stage in _driver.find_elements(by=By.TAG_NAME,
                                       value='cm-display-stage'):
        for button in stage.find_elements(by=By.TAG_NAME, value='button'):
            if (button.get_attribute('color') == 'green' and
                    'play_arrow' in button.text and
                    'mat-button-disabled' in button.get_attribute('class')):
                exit('\n\nGame was not solved in time.\n')
    if len(session.remaining) > 1:
        _auto_guess_count += 1
    keyboard = {}
    for key in _driver.find_element(
            by=By.CLASS_NAME, value='keys'
            ).find_elements(
            by=By.CLASS_NAME, value='key'):
        keyboard[key.text.split()[0].strip().lower()] = key
    if ((not _dialog_closed or len(session.remaining) == 1) and
            _auto_guess_count == 3):
        time.sleep(2.5)
        dialogs = _driver.find_elements(by=By.CLASS_NAME,
                                        value='info-dialog')
        if len(dialogs) > 0:
            dialogs[0].find_element(by=By.TAG_NAME, value='button').click()
            time.sleep(1)
            if len(session.remaining) > 1:
                _dialog_closed = True
    webpage = _driver.find_element(by=By.TAG_NAME, value='html')
    webpage.send_keys(session.actual_best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(3)
    return session.actual_best


def auto_response_wordzy(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Wordzy website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    guess = session.entered[-1]
    # check if game has ended
    n_games = len(session.remaining)
    validate_wordzy_game(n_games, session.mode.endless)
    # if the game has ended, the last guess must have been correct
    for stage in _driver.find_elements(by=By.TAG_NAME,
                                       value='cm-display-stage'):
        for button in stage.find_elements(by=By.TAG_NAME, value='button'):
            if (button.get_attribute('color') == 'green' and
                    'play_arrow' in button.text):
                return [(''.join([RIGHT for _ in guess]), session.expected[0])]
    # if not, find the elements necessary to read each board's response
    responses = []
    focus_key = None
    stage = _driver.find_element(by=By.TAG_NAME, value='cm-word-stage')
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
    # read the response on each board that is still expected to exist
    for board in tqdm(session.expected, ascii=PROGRESS, leave=False):
        validate_wordzy_game(n_games, session.mode.endless)
        # find the most recent response
        while not (focus_key.text.split()[-1]).isnumeric():
            if 'ENTER' in focus_key.text:
                break
            focus_key.click()
            time.sleep(0.5)
        # read the response on the focused game
        focused = stage.find_elements(by=By.CLASS_NAME, value='focused')
        if len(focused) == 0:
            focused = stage.find_element(by=By.TAG_NAME, value='cm-word-grid')
        else:
            focused = focused[0]
        # if the expected board is not found, it must have been completed
        if f'grid{board}' not in focused.find_element(
            By.CLASS_NAME, 'cdk-virtual-scroll-viewport'
        ).get_attribute('class') and guess in session.remaining[board]:
            responses.append((''.join(RIGHT for _ in guess), board))
            continue
        stuck = False
        response = ''
        while len(response) != len(guess):
            # this will cause the program to pause if it cannot find a response
            #   (usually the solution involves just scrolling down on whichever
            #   board it is stuck on until the most recent guess can be seen)
            if stuck:
                focused = stage.find_element(by=By.TAG_NAME,
                                             value='cm-word-grid')
            words = focused.find_elements(by=By.TAG_NAME, value='cm-word')
            for word in words:
                response = ''
                letters = word.find_elements(by=By.CLASS_NAME, value='letter')
                colors = letters
                if session.mode.master:
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


def auto_response_wordle(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Wordle website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    response = ''
    time.sleep(1)
    row = _driver.find_element(
        By.XPATH,
        ('//*[@id="wordle-app-game"]/div[1]/div/'
         f'div[{len(session.entered)}]')
    )
    tiles = row.find_elements(by=By.CSS_SELECTOR, value='div > div')
    for tile in tiles:
        evaluation = tile.get_attribute('data-state')
        if evaluation == 'absent':
            response += WRONG
        elif evaluation == 'present':
            response += CLOSE
        elif evaluation == 'correct':
            response += RIGHT
    return [(response, 0)]


def auto_response_dordle(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Dordle website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    guess = session.entered[-1]
    game = _driver.find_element(by=By.XPATH, value='//*[@id="game"]')
    responses = []
    boards = list(game.find_elements(by=By.CLASS_NAME, value="table_guesses"))
    for board in session.expected:
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


def auto_response_quordle(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Quordle website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    guess = session.entered[-1]
    responses = []
    boards = list(_driver.find_elements(by=By.XPATH,
                                        value='//*[@role="table"]'))
    for board in session.expected:
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


def auto_response_octordle(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Quordle website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    responses = []
    for board in session.expected:
        game_board = _driver.find_element(value=f'board-{board + 1}')
        response = ''
        rows = game_board.find_elements(By.CLASS_NAME, 'board-row')
        for letter in rows[len(session.entered) - 1].find_elements(
            By.CLASS_NAME, 'letter'
        ):
            info = letter.get_attribute('class')
            if 'exact-match' in info:
                response += RIGHT
            elif 'word-match' in info:
                response += CLOSE
            else:
                response += WRONG
        responses.append((response, board))
    return responses


def auto_response_duotrigordle(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Duotrigordle website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    responses = []
    boards = list(_driver.find_elements(by=By.CLASS_NAME, value="board"))
    for board in tqdm(session.expected, ascii=PROGRESS, leave=False):
        response = ''
        cells = boards[board].find_elements(by=By.CLASS_NAME, value="cell")
        index = (len(session.entered) - 1) * 5
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


def auto_response_64ordle(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the 64ordle website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    guess = session.entered[-1]
    responses = []
    boards = list(_driver.find_element(by=By.ID,
                                       value="box-holder-{}".format(n + 1))
                  for n in range(len(session.remaining)))
    for board in tqdm(session.expected, ascii=PROGRESS, leave=False):
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


def auto_response_nordle(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Nordle website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    guess = session.entered[-1]
    game = _driver.find_element(by=By.ID, value='words')
    columns = list(game.find_elements(by=By.CLASS_NAME, value='column'))
    responses = []
    for board in tqdm(session.expected, ascii=PROGRESS, leave=False):
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


def auto_response_fibble(session: SessionInfo) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Fibble website.

    Args:
        session:
            A SessionInfo instance containing all information about the current
            set of games being solved

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    response = ''
    row = _driver.find_elements(by=By.CLASS_NAME, value='Row')[
        len(session.entered) - 1
    ]
    for letter in row.find_elements(by=By.CLASS_NAME, value='Row-letter'):
        label = letter.get_attribute('aria-label')
        if 'correct' in label:
            response += RIGHT
        elif 'elsewhere' in label:
            response += CLOSE
        else:
            response += WRONG
    return [(response, 0)]


SITE_INFO: dict[str, tuple] = {
    'wordle': (
        'https://www.nytimes.com/games/wordle/index.html',
        1, False, False, False,
        auto_guess_default, auto_response_wordle
    ),
    'dordle': (
        'https://zaratustra.itch.io/dordle',
        2, False, False, False,
        auto_guess_default, auto_response_dordle
    ),
    'quordle': (
        'https://www.quordle.com/#/',
        4, False, False, False,
        auto_guess_default, auto_response_quordle
    ),
    'octordle': (
        'https://octordle.com/',
        8, False, False, False,
        auto_guess_default, auto_response_octordle
    ),
    'sedecordle': (
        'https://www.sedecordle.com/',
        16, False, False, False,
        auto_guess_default, auto_response_default
    ),
    'duotrigordle': (
        'https://duotrigordle.com/',
        32, False, False, False,
        auto_guess_default, auto_response_duotrigordle
    ),
    '64ordle': (
        'https://64ordle.au/',
        64, False, False, False,
        auto_guess_default, auto_response_64ordle,
    ),
    'nordle': (
        'https://www.nordle.us/?n=',
        0, False, False, False,
        auto_guess_default, auto_response_nordle
    ),
    'wordzy': (
        'https://wordzmania.com/Wordzy/',
        0, False, False, False,
        auto_guess_wordzy, auto_response_wordzy
    ),
    'fibble': (
        'https://fibble.xyz/',
        1, False, False, True,
        auto_guess_default, auto_response_fibble
    )
}
