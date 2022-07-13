import time
from math import ceil, log2

from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

try:
    from common import RIGHT, CLOSE, WRONG, PROGRESS
except ModuleNotFoundError:  # this is only here to help pytest find the module
    from wordle_autosolver.common import RIGHT, CLOSE, WRONG, PROGRESS


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


def open_website(website: str, num_boards=1, master=False, endless=False,
                 quiet=False) -> int:
    """Opens the requested website based on the given parameters.

    Args:
        website:
            The URL of the website to be opened
        num_boards:
            The number of simultaneous games being played (each guess is made
            across all boards at once) (default: 1)
        master:
            A boolean value representing whether the game mode is Wordzy Master
            (default: False)
        endless:
            A boolean value representing whether the program is in endless mode
            (default: False)
        quiet:
            A boolean value representing whether to print any messages to the
            console (default: False)

    Returns:
        The number of boards used by the website. This should normally be the
        same value as `num_boards`, but there are some cases where the chosen
        website cannot play that exact number of games, so be sure to verify
        this result before using the number of boards requested by the user.
    """
    global _driver
    if not quiet:
        print("\nConnecting to the target website...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # go fullscreen
    # stop unexpected messages being printed to the console from the webdriver
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument("--log-level=3")
    if quiet:  # do not open an actual browser -- do it all behind-the-scenes
        options.add_argument('--headless')
    # exit any driver that was being used before and reinitialize it
    quit_driver()
    _driver = webdriver.Chrome(options=options)
    # alter the URL if necessary to play the correct version of the chosen game
    if 'wordzmania' in website and master:
        website += 'Master'
    time.sleep(3)
    if any(x in website for x in ('sedecordle', '64ordle')):
        website += '?mode=' + ('free' if endless else 'daily')
    elif 'octordle' in website:
        website += 'free' if endless else 'daily'
    elif 'quordle' in website and endless:
        website += 'practice'
    elif 'fibble' in website and endless:
        website += '?unlimited'
    elif 'nordle' in website:
        website += str(num_boards)
    # # # CURRENTLY NOT WORKING -- ENDLESS WORDLE WILL DEFAULT TO DAILY WORDLE
    # elif 'wordle' in website and endless:
    #     website = 'https://devbanana.itch.io/infinidle'
    # # #
    _driver.get(website)  # this is when it attempts to connect to the website
    if not quiet:
        print("Connected to '{}'".format(website))
    time.sleep(3)  # give the page elements a few seconds to load
    # must navigate to the correct page on some websites
    if 'wordzmania' in website:
        num_boards = navigate_wordzy(num_boards, endless, quiet)
    elif 'dordle' in website:
        navigate_dordle(endless)
    elif 'infinidle' in website:
        navigate_infinidle()
    elif 'wordle' in website:
        navigate_wordle()
    elif 'quordle' in website:
        navigate_quordle()
    time.sleep(4)
    return num_boards


###############################################################################
#                   HELPER FUNCTIONS FOR SPECIFIC WEBSITES                    #
###############################################################################


def navigate_wordle() -> None:
    """Navigates the Wordle website before beginning the solve."""
    game_app = _driver.find_element(by=By.TAG_NAME, value='game-app')
    root = game_app.shadow_root
    # close instructions dialog
    modal = root.find_element(By.CSS_SELECTOR, '#game > game-modal')
    modal_root = modal.shadow_root
    icon = modal_root.find_element(By.CSS_SELECTOR, 'div > div > div')
    icon.click()
    time.sleep(1)
    # change theme to dark (optional)
    root.find_element(value='settings-button').click()
    switch = root.find_element(By.CSS_SELECTOR,
                               '#game > game-page > game-settings')
    switch_root = switch.shadow_root
    switch_root.find_element(value='dark-theme').click()
    page = root.find_element(By.CSS_SELECTOR, '#game > game-page')
    page_root = page.shadow_root
    page_root.find_element(By.CSS_SELECTOR,
                           'div > div > header > game-icon').click()
    time.sleep(2)


def navigate_dordle(endless: bool) -> None:
    """Navigates the Dordle website before beginning the solve."""
    iframe = _driver.find_element(by=By.XPATH, value='//*[@id="game_drop"]')
    _driver.switch_to.frame(iframe)
    _driver.find_element(value='free' if endless else 'daily').click()
    # change theme to dark (optional)
    _driver.find_element(By.XPATH, '//*[@id="body"]/table/tbody/tr/td[5]'
                         ).click()
    _driver.find_element(By.XPATH,
                         '//*[@id="options"]/div[4]/table/tbody/tr/td[3]'
                         ).click()
    _driver.find_element(By.XPATH, '//*[@id="body"]/table/tbody/tr/td[5]'
                         ).click()
    time.sleep(2)


def navigate_quordle() -> None:
    """Navigates the Quordle website before beginning the solve."""
    _driver.find_element(By.XPATH,
                         '//*[@id="root"]/div/nav/div/div[2]/button[2]'
                         ).click()
    _driver.find_element(By.XPATH,
                         '//*[@id="options-dropdown"]/button[1]').click()
    time.sleep(1)
    _driver.find_element(
        By.XPATH,
        '//*[@id="settings-panel"]/div[2]/div[2]/div[1]/label/div[1]'
        ).click()
    _driver.find_element(By.XPATH,
                         '//*[@id="settings-panel"]/div[1]/button').click()
    time.sleep(1)


def navigate_infinidle() -> None:
    """Navigates the Infinidle website before beginning the solve."""
    _driver.find_element(By.CLASS_NAME, 'load_iframe_btn').click()
    time.sleep(3)
    iframe = _driver.find_element(by=By.XPATH, value='//*[@id="game_drop"]')
    _driver.switch_to.frame(iframe)


def navigate_wordzy(num_boards: int, endless: bool, quiet=False) -> int:
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
    if not quiet:
        print("Navigated to '{}'.".format(_driver.current_url))
    return num_boards


def validate_wordzy_game(num_boards: int, endless: bool):
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


def auto_guess_default(remaining: list[str], guesses: list[str], best: str,
                       hard: bool, master: bool, endless: bool) -> str:
    """Enters `best` into the webpage and ignores all other arguments.

    This is the default `auto_guess` function. Currently used on the following
    websites: "wordle", "dordle", "quordle", "octordle", "sedecordle",
    "duotrigordle", "64ordle", "nordle", and "fibble".

    Returns:
        The word which was selected as the guess.
    """
    webpage = _driver.find_element(by=By.TAG_NAME, value='html')
    time.sleep(0.5)
    webpage.send_keys(best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(1)
    return best


def auto_response_default(guess: str, remaining: list[str], entered: list[str],
                          expected: list[int], hard: bool, master: bool,
                          liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the current webpage.

    This is the default `auto_response` function. Currently used on the
    following websites: "octordle" and "sedecordle".

    Required Args:
        guess:
            The most recent guess entered into the game
        remaining:
            The list of remaining possible answers
        expected:
            A list of all board indexes where the answer has not been entered

    Ignored Args:
        entered:
            A list of all words which have been entered into the game so far
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    responses = []
    boards = list(_driver.find_element(by=By.ID,
                                       value="box-holder-{}".format(n + 1))
                  for n in range(len(remaining)))
    for board in tqdm(expected, ascii=PROGRESS, leave=False):
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


def auto_guess_wordzy(remaining: list[str], guesses: list[str], best: str,
                      hard: bool, master: bool, endless: bool) -> str:
    """Enters `best` into the current Wordzy game.

    Required Args:
        remaining:
            The list of all remaining possible answers
        best:
            The most recently calculated best guess according to the solver
        endless:
            A boolean value representing whether the program is in endless mode

    Ignored Args:
        guesses:
            The list of all valid guesses
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master

    Returns:
        The word which was selected as the guess.
    """
    global _auto_guess_count, _dialog_closed
    time.sleep(3)
    validate_wordzy_game(len(remaining), endless)
    for stage in _driver.find_elements(by=By.TAG_NAME,
                                       value='cm-display-stage'):
        for button in stage.find_elements(by=By.TAG_NAME, value='button'):
            if (button.get_attribute('color') == 'green' and
                    'play_arrow' in button.text and
                    'mat-button-disabled' in button.get_attribute('class')):
                exit('\n\nGame was not solved in time.\n')
    if len(remaining) > 1:
        _auto_guess_count += 1
    keyboard = {}
    for key in _driver.find_element(
            by=By.CLASS_NAME, value='keys'
            ).find_elements(
            by=By.CLASS_NAME, value='key'):
        keyboard[key.text.split()[0].strip().lower()] = key
    if ((not _dialog_closed or len(remaining) == 1) and
            _auto_guess_count == 3):
        time.sleep(2.5)
        dialogs = _driver.find_elements(by=By.CLASS_NAME,
                                        value='info-dialog')
        if len(dialogs) > 0:
            dialogs[0].find_element(by=By.TAG_NAME, value='button').click()
            time.sleep(1)
            if len(remaining) > 1:
                _dialog_closed = True
    webpage = _driver.find_element(by=By.TAG_NAME, value='html')
    webpage.send_keys(best)
    webpage.send_keys(Keys.ENTER)
    time.sleep(3)
    return best


def auto_response_wordzy(guess: str, remaining: list[str], entered: list[str],
                         expected: list[int], hard: bool, master: bool,
                         liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Wordzy website.

    Required Args:
        guess:
            The most recent guess entered into the game
        remaining:
            The list of remaining possible answers
        expected:
            A list of all board indexes where the answer has not been entered
        master:
            A boolean value representing whether the game mode is Wordzy Master
        endless:
            A boolean value representing whether the program is in endless mode

    Ignored Args:
        entered:
            A list of all words which have been entered into the game so far
        hard:
            A boolean value representing whether the game mode is Hard
        liar:
            A boolean value representing whether the game mode is Fibble

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    # check if game has ended
    n_games = len(remaining)
    validate_wordzy_game(n_games, endless)
    # if the game has ended, the last guess must have been correct
    for stage in _driver.find_elements(by=By.TAG_NAME,
                                       value='cm-display-stage'):
        for button in stage.find_elements(by=By.TAG_NAME, value='button'):
            if (button.get_attribute('color') == 'green' and
                    'play_arrow' in button.text):
                return [(''.join([RIGHT for _ in guess]), expected[0])]
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
    for board in tqdm(expected, ascii=PROGRESS, leave=False):
        validate_wordzy_game(n_games, endless)
        # find the most recent response
        while not (focus_key.text.split()[-1]).isnumeric():
            if 'ENTER' in focus_key.text:
                break
            focus_key.click()
            time.sleep(0.5)
        # I'm not 100% sure why this is here, but I'm afraid to delete it
        if (('ENTER' not in focus_key.text and
             board != int(focus_key.text.split()[-1]) - 1) or
            ('ENTER' in focus_key.text and
             len(expected) > 1 and
             board == expected[-1] and
             guess in remaining[board])):
            responses.append((''.join(RIGHT for _ in guess), board))
            continue
        # the rest of this makes sense -- read the response on the focused game
        focused = stage.find_elements(by=By.CLASS_NAME, value='focused')
        if len(focused) == 0:
            focused = stage.find_element(by=By.TAG_NAME, value='cm-word-grid')
        else:
            focused = focused[0]
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


def auto_response_wordle(guess: str, remaining: list[str], entered: list[str],
                         expected: list[int], hard: bool, master: bool,
                         liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Wordle website.

    Required Args:
        guess:
            The most recent guess entered into the game

    Ignored Args:
        remaining:
            The list of remaining possible answers
        entered:
            A list of all words which have been entered into the game so far
        expected:
            A list of all board indexes where the answer has not been entered
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    response = ''
    game_app = _driver.find_element(by=By.TAG_NAME, value='game-app')
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


def auto_response_infinidle(guess: str, remaining: list[str],
                            entered: list[str], expected: list[int],
                            hard: bool, master: bool, liar: bool, endless: bool
                            ) -> list[tuple[str, int]]:
    """WARNING: Currently not implemented."""
    _driver.save_screenshot('infinidle/ss.png')
    # now check rgb values of specific pixels to figure out what's going on
    pass


def auto_response_dordle(guess: str, remaining: list[str], entered: list[str],
                         expected: list[int], hard: bool, master: bool,
                         liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Dordle website.

    Required Args:
        guess:
            The most recent guess entered into the game
        expected:
            A list of all board indexes where the answer has not been entered

    Ignored Args:
        remaining:
            The list of remaining possible answers
        entered:
            A list of all words which have been entered into the game so far
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    game = _driver.find_element(by=By.XPATH, value='//*[@id="game"]')
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


def auto_response_quordle(guess: str, remaining: list[str], entered: list[str],
                          expected: list[int], hard: bool, master: bool,
                          liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Quordle website.

    Required Args:
        guess:
            The most recent guess entered into the game
        expected:
            A list of all board indexes where the answer has not been entered

    Ignored Args:
        remaining:
            The list of remaining possible answers
        entered:
            A list of all words which have been entered into the game so far
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    responses = []
    boards = list(_driver.find_elements(by=By.XPATH,
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


def auto_response_duotrigordle(guess: str, remaining: list[str],
                               entered: list[str], expected: list[int],
                               hard: bool, master: bool, liar: bool,
                               endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Duotrigordle website.

    Required Args:
        entered:
            A list of all words which have been entered into the game so far
        expected:
            A list of all board indexes where the answer has not been entered

    Ignored Args:
        guess:
            The most recent guess entered into the game
        remaining:
            The list of remaining possible answers
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    responses = []
    boards = list(_driver.find_elements(by=By.CLASS_NAME, value="board"))
    for board in tqdm(expected, ascii=PROGRESS, leave=False):
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


def auto_response_64ordle(guess: str, remaining: list[str], entered: list[str],
                          expected: list[int], hard: bool, master: bool,
                          liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the 64ordle website.

    Required Args:
        guess:
            The most recent guess entered into the game
        remaining:
            The list of remaining possible answers
        expected:
            A list of all board indexes where the answer has not been entered

    Ignored Args:
        entered:
            A list of all words which have been entered into the game so far
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    responses = []
    boards = list(_driver.find_element(by=By.ID,
                                       value="box-holder-{}".format(n + 1))
                  for n in range(len(remaining)))
    for board in tqdm(expected, ascii=PROGRESS, leave=False):
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


def auto_response_nordle(guess: str, remaining: list[str], entered: list[str],
                         expected: list[int], hard: bool, master: bool,
                         liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Nordle website.

    Required Args:
        guess:
            The most recent guess entered into the game
        expected:
            A list of all board indexes where the answer has not been entered

    Ignored Args:
        remaining:
            The list of remaining possible answers
        entered:
            A list of all words which have been entered into the game so far
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    game = _driver.find_element(by=By.ID, value='words')
    columns = list(game.find_elements(by=By.CLASS_NAME, value='column'))
    responses = []
    for board in tqdm(expected, ascii=PROGRESS, leave=False):
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


def auto_response_fibble(guess: str, remaining: list[str], entered: list[str],
                         expected: list[int], hard: bool, master: bool,
                         liar: bool, endless: bool) -> list[tuple[str, int]]:
    """Finds and returns the expected response(s) on the Fibble website.

    Required Args:
        entered:
            A list of all words which have been entered into the game so far

    Ignored Args:
        guess:
            The most recent guess entered into the game
        remaining:
            The list of remaining possible answers
        expected:
            A list of all board indexes where the answer has not been entered
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        endless:
            A boolean value representing whether the program is in endless mode

    Returns:
        A list of 2-tuples where the first element is the response and the
        second element is the index of the board that gave that response.
    """
    response = ''
    row = _driver.find_elements(by=By.CLASS_NAME, value='Row')[len(entered)]
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
        1, True, False, False,
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
        auto_guess_default, auto_response_default
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
        0, False, True, False,
        auto_guess_wordzy, auto_response_wordzy
    ),
    'fibble': (
        'https://fibble.xyz/',
        1, False, False, True,
        auto_guess_default, auto_response_fibble
    ),
    'infinidle': (
        'https://devbanana.itch.io/infinidle',
        1, False, False, False,
        auto_guess_default, auto_response_infinidle
    )
}
