import time
from math import ceil, log2

from tqdm import tqdm

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
except ImportError:
    print('Failed to import selenium.\n')

from common import *


driver = None
auto_guess_count = 0
dialog_closed = False


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
                          liar, endless):
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
                         liar, endless):
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
                         liar, endless):
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
                         liar, endless):
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
                         liar, endless):
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
                          liar, endless):
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
                               hard, master, liar, endless):
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
                          liar, endless):
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


def get_driver():
    return driver


def quit_driver():
    driver.quit()
