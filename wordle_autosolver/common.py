import os
from typing import Union, Optional

from tqdm import tqdm


RIGHT = 'O'
CLOSE = '+'
WRONG = '.'
IS_MS_OS: bool = os.name == 'nt'
PROGRESS: Optional[str] = '__...:::!!|' if IS_MS_OS else None

response_data: dict = {}
response_data_updated: bool = False
best_guess_updated: bool = False

if IS_MS_OS:
    os.system('color')


def set_best_guess_updated(value=True) -> None:
    """Sets the value of `best_guess_updated`.

    Args:
        value:
            The boolean value to set (default: True)
    """
    global best_guess_updated
    best_guess_updated = value


def get_best_guess_updated() -> bool:
    """Gets the value of `best_guess_updated`.

    Returns:
        The boolean value representing whether or not the `best_guess` dict has
        been updated.
    """
    return best_guess_updated


def set_response_data_updated(value=True) -> None:
    """Sets the value of `response_data_updated`.

    Args:
        value:
            The boolean value to set (default: True)
    """
    global response_data_updated
    response_data_updated = value


def get_response_data_updated() -> bool:
    """Gets the value of `best_guess_updated`.

    Returns:
        The boolean value representing whether or not the `response_data` dict
        has been updated.
    """
    return response_data_updated


def set_response_data(value={}) -> None:
    """Sets the value of `response_data`.

    Args:
        value:
            The new dictionary to replace as the data
    """
    global response_data
    response_data = value


def get_response_data() -> dict[str, dict[str, str]]:
    """Gets the value of `response_data`.

    Returns:
        A dictionary mapping the guessed word to another dictionary mapping an
        answer to the resulting response. (In other words, if the guess was
        ALERT and the answer was OLIVE, the response would be `.O+..`, so
        `response_data['alert']['olive'] == '.O+..'` should return `True`.)
    """
    return response_data


def colored_response(guess: str, response: str, master=False) -> str:
    """Returns colored text to match the given guess and response"""
    text = ''
    letters = response if master else guess.upper()
    for letter, symbol in zip(letters, response):
        if symbol == RIGHT:
            text += "\x1b[38;5;102m\x1b[48;5;30m" + letter + "\x1b[0m"
        elif symbol == CLOSE:
            text += "\x1b[38;5;103m\x1b[48;5;30m" + letter + "\x1b[0m"
        else:
            text += letter
    return text


def _get_easy_response(guess: str, answer: str) -> str:
    """Gets expected the response on a normal game of Wordle.

    Args:
        guess:
            The word which was guessed by the player
        answer:
            A potential answer word to be tested

    Returns:
        A string represention of the expected response.
    """
    if guess == answer:
        return ''.join([RIGHT for _ in answer])
    response = [WRONG for _ in answer]  # assume all are wrong by default
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


def _get_master_response(guess: str, answer: str) -> str:
    """Gets the expected response on a game of Wordzy Master.

    Args:
        guess:
            The word which was guessed by the player
        answer:
            A potential answer word to be tested

    Returns:
        A string represention of the expected response.
    """
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
    # third loop fills the rest of the response with misses
    while len(response) < len(answer):
        response += WRONG
    return response


def get_response(guess: str, answer: str, master: bool, use_cache=True) -> str:
    """Gets the expected response based on the version of Wordle being played.

    Args:
        guess:
            The word which was guessed by the player
        answer:
            A potential answer word to be tested
        master:
            A boolean value representing whether the game mode is Wordzy Master
        use_cache:
            A boolean value representing whether to use previously-calculated
            response data being stored by the program (default: True)

    Returns:
        A string represention of the expected response.
    """
    global response_data, response_data_updated
    # Note: this use of memoization appears to speed up calculations by a
    #       factor of 10, but it also uses between 0.4 and 1.2GB of storage
    if use_cache and guess in response_data and answer in response_data[guess]:
        return response_data[guess][answer]
    response = ''
    if master:
        response = _get_master_response(guess, answer)
    else:
        response = _get_easy_response(guess, answer)
    if use_cache:
        if guess not in response_data:
            response_data[guess] = {}
        response_data[guess][answer] = response
        response_data_updated = True
    return response


def filter_remaining(remaining: list[str], guess: str, response: str,
                     master: bool, liar=False, use_cache=True) -> list[str]:
    """Filters a given list of answers based on the given guess and response.

    Args:
        remaining:
            The list of remaining possible answers
        guess:
            The word which was guessed by the player
        response:
            The response from the game after `guess` was entered
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
            (default: False)
        use_cache:
            A boolean value representing whether to use previously-calculated
            response data being stored by the program (default: True)

    Returns:
        A new list which only includes answers that are consistent with the
        given guess and response.
    """
    filtered = []
    if response == ''.join(RIGHT for _ in guess):
        return [guess]
    for answer in remaining:
        this_response = get_response(guess, answer, master, use_cache)
        if liar:
            # check that exactly one letter in the response is wrong
            if 1 == sum(int(this_response[n] != response[n])
                        for n in range(len(answer))):
                filtered.append(answer)
        elif this_response == response:
            filtered.append(answer)
    return filtered


def count_remaining(remaining: list[str], guess: str, response: str,
                    limit: Optional[int] = None, master=False, liar=False,
                    use_cache=True) -> int:
    """Counts the number of answers that are consistent with the given info.

    Args:
        remaining:
            The list of remaining possible answers
        guess:
            The word which was guessed by the player
        response:
            The response from the game after `guess` was entered
        limit:
            The limit which, once exceeded, will immediately return a value;
            if not set, the limit will be ignored (default: None)
        master:
            A boolean value representing whether the game mode is Wordzy Master
            (default: False)
        liar:
            A boolean value representing whether the game mode is Fibble
            (default: False)
        use_cache:
            A boolean value representing whether to use previously-calculated
            response data being stored by the program (default: True)

    Returns:
        The number of answers consistent with the given guess and response. If
        this value would be greater than `limit`, instead return `limit + 1`.
    """
    if limit is None:
        limit = len(remaining)
    count = 0
    for answer in remaining:
        this_response = get_response(guess, answer, master, use_cache)
        if liar:
            # check that exactly one letter in the response is wrong
            if 1 == sum(int(this_response[n] != response[n])
                        for n in range(len(answer))):
                count += 1
        elif this_response == response:
            count += 1
        if count > limit:
            return count
    return count


def best_guesses(answers: list[str], guesses: Optional[list[str]] = None,
                 max_limit: Optional[int] = None, master=False, liar=False,
                 show=False, return_all=False
                 ) -> Union[list[str], dict[str, int]]:
    """Finds the best guesses to narrow down the remaining possible answers.

    This function minimizes the worst-case scenario for every legal guess.
    It will iterate through each possible guess, then for each guess, it will
    iterate through every remaining possible answer. For each guess-answer
    pair, the expected response is found, then that response is used to filter
    the remaining answers. Whichever response results in the largest number of
    remaining answers is recorded as the worst-case result for that guess. The
    function will then return either a list of all guesses with the smallest
    worst-case result or a dict containing the worst-case for every guess.

    Args:
        answers:
            The list of all remaining possible answers
        guesses:
            The list of all valid guesses; if not set, the answer list will be
            used instead (default: None)
        max_limit:
            The maximum value to be considered when counting remaining answers
            such that no count should be exceed `max_limit + 1` (default: -1)
        master:
            A boolean value representing whether the game mode is Wordzy Master
            (default: False)
        liar:
            A boolean value representing whether the game mode is Fibble
            (default: False)
        show:
            A boolean value representing whether a progress bar should be shown
            (default: False)
        return_all:
            A boolean value representing whether to return the worst-case count
            for all guesses as a dict (default: False)

    Returns:
        A list of all guesses which minimize the worst-case number of remaining
        answers. If `return_all == True`, this will instead return a dict where
        the keys are the guesses and the values are the worst-case counts.
    """
    if guesses is None:
        guesses = answers
    if max_limit is None:
        max_limit = len(answers)
    worst_case = dict([(x, 0) for x in guesses])
    score = dict([(x, {}) for x in guesses])
    limit = max_limit
    for guess in tqdm(guesses, leave=False, ascii=PROGRESS, disable=not show):
        for answer in answers:
            response = get_response(guess, answer, master)
            if response not in score[guess]:
                score[guess][response] = count_remaining(answers, guess,
                                                         response, limit,
                                                         master, liar)
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


def best_avg_guesses(answers: list[str], guesses: Optional[list[str]] = None,
                     master=False, liar=False, show=False,
                     return_all=False) -> list[str]:
    """Finds the best guesses to narrow down the remaining possible answers.

    This function minimizes the average result for every legal guess. It will
    iterate through each possible guess, then for each guess, it will iterate
    through every remaining possible answer. For each guess-answer pair, the
    expected response is found, then that response is used to filter the
    remaining answers. The number of answers remaining is added to the total at
    each step to determine the average. The function will then return either a
    list of all guesses with the smallest average result or a dict containing
    the average for every guess.

    Args:
        answers:
            The list of all remaining possible answers
        guesses:
            The list of all valid guesses; if not set, the answer list will be
            used instead (default: None)
        master:
            A boolean value representing whether the game mode is Wordzy Master
            (default: False)
        liar:
            A boolean value representing whether the game mode is Fibble
            (default: False)
        show:
            A boolean value representing whether a progress bar should be shown
            (default: False)
        return_all:
            A boolean value representing whether to return the worst-case count
            for all guesses as a dict (default: False)

    Returns:
        A list of all guesses which minimize the average number of remaining
        answers. If `return_all` is `True`, this will instead return a dict
        where the keys are the guesses and the values are the averages.
    """
    if guesses is None:
        guesses = answers
    average = dict([(x, 0) for x in guesses])
    count = dict([(x, {}) for x in guesses])
    best_avg = len(answers)
    for guess in tqdm(guesses, leave=False, ascii=PROGRESS, disable=not show):
        for answer in answers:
            response = get_response(guess, answer, master)
            if response not in count[guess]:
                count[guess][response] = count_remaining(answers, guess,
                                                         response, None,
                                                         master, liar)
            average[guess] += count[guess][response]
        average[guess] /= len(answers)
        if average[guess] < best_avg:
            best_avg = average[guess]
    if return_all:
        return average
    best = [x for x in guesses if average[x] == best_avg]
    priority = set(best) & set(answers)
    if len(priority) > 0:
        return list(priority)
    return best


def rec_build_best_tree(answers: list[str], guesses: list[str], start: str,
                        master: bool, liar: bool, depth: int, show=True
                        ) -> dict:
    """Recursively builds a minimal decision tree for the given starting guess.

    Args:
        answers:
            The list of all remaining possible answers
        guesses:
            The list of all valid guesses
        start:
            The starting guess to use as the root of the decision tree
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        depth:
            Number of recursive steps remaining until an answer must be reached
        show:
            A boolean value representing whether a progress bar should be shown
            (default: False)

    Returns:
        A dict which maps a str to a dict. The first key will be the starting
        guess, and this will return a dict with a key for every valid response
        at this point in the tree. Using one of those keys will access another
        dict with a key for each of the best guesses given that response. This
        pattern will continue down the tree, alternating guess then response,
        until the only remaining response is that all letters are correct.
    """
    if depth == 0:
        return {}
    tree = {start: {}}
    for answer in tqdm(answers, ascii=PROGRESS, disable=not show):
        response = get_response(start, answer, master)
        if response in tree[start]:
            continue
        # after this point, treat this as a loop through all possible responses
        filtered = filter_remaining(answers, start, response, master, liar)
        if len(filtered) == 1:
            # if there is only one option, then it must be the best guess
            tree[start][response] = {filtered[0]: {}}
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
        tree[start][response] = valid_path
    return tree
