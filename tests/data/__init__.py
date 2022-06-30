import os
from json import load, dump


data_path = os.path.relpath(__file__)
data_path = '/'.join(data_path.split('/' if '/' in data_path else '\\')[:-1])
data_path += '/'


def format_bytes(num_bytes: int) -> str:
    """Generates a human readable str version of the given number of bytes.

    Args:
        num_bytes:
            The number of bytes to convert to a str

    Returns:
        A human readable str giving the number of bytes.
    """
    value = num_bytes
    suffix = ' B'
    if num_bytes > 2**50:
        value = num_bytes / 2**50
        suffix = ' PB'
    elif num_bytes > 2**40:
        value = num_bytes / 2**40
        suffix = ' TB'
    elif num_bytes > 2**30:
        value = num_bytes / 2**30
        suffix = ' GB'
    elif num_bytes > 2**20:
        value = num_bytes / 2**20
        suffix = ' MB'
    elif num_bytes > 2**10:
        value = num_bytes / 2**10
        suffix = ' KB'
    if num_bytes > 2**10:
        value = '{:.3f}'.format(value)
    return str(value) + suffix


def load_all_data(hard: bool, master: bool, liar: bool, nyt=False,
                  allow_print=True
                  ) -> tuple[list[str], list[str], list[str],
                             dict[str, float], dict, dict[str, str]]:
    """Loads all data related to the current game mode.

    Args:
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        nyt:
            A boolean value representing whether to use the New York Times word
            list or the extended word list which works on all sites (default:
            False)
        allow_print:
            A boolean value representing whether to allow print statements

    Returns:
        A 6-tuple containing the following items, in order: list of all
        possible answers, list of all valid guesses, list of all valid guesses
        specifically for nordle, dict mapping all valid guesses to their
        frequency of use, dict representing the tree of best guesses, and dict
        holding all precalculated response data.
    """
    if allow_print:
        print('Loading precalculated data...')
    freq_data = {}
    with open(data_path + 'freq_map.json', 'r') as data:
        freq_data = load(data)
    ans_file = 'nyt_answers.json' if nyt else 'curated_answers.json'
    answers = []
    with open(data_path + ans_file, 'r') as curated:
        answers = load(curated)
    guesses = []
    with open(data_path + 'allowed_guesses.json', 'r') as allowed:
        guesses = load(allowed)
    nordle_guesses = []
    with open(data_path + 'allowed_nordle.json', 'r') as allowed:
        nordle_guesses = load(allowed)
    resp_file = 'responses' + ('_master' if master else '') + '.json'
    resp_data = {}
    with open(data_path + resp_file, 'r') as responses:
        resp_data = load(responses)
    best_guess_file = 'best_guess.json'
    if nyt:
        best_guess_file = 'best_guess_nyt.json'
    elif hard:
        best_guess_file = 'best_guess_hard.json'
    elif master:
        best_guess_file = 'best_guess_master.json'
    elif liar:
        best_guess_file = 'best_guess_liar.json'
    saved_best = {}
    with open(data_path + best_guess_file, 'r') as bestf:
        saved_best = load(bestf)
    if allow_print:
        print('Finished loading.')
    return answers, guesses, nordle_guesses, freq_data, saved_best, resp_data


def save_all_data(hard: bool, master: bool, liar: bool,
                  best_guess_updated: bool, saved_best: dict,
                  response_data_updated: bool, response_data: dict,
                  nyt=False, allow_print=True) -> None:
    """Saves all data related to the current game mode.

    Args:
        hard:
            A boolean value representing whether the game mode is Hard
        master:
            A boolean value representing whether the game mode is Wordzy Master
        liar:
            A boolean value representing whether the game mode is Fibble
        best_guess_updated:
            A boolean value representing whether `saved_best` contains new
            information
        saved_best:
            A dict representing the decision tree used to find best guesses
        response_data_updated:
            A boolean value representing whether `response_data` contains new
            information
        response_data:
            A dict holding all precalculated responses
        nyt:
            A boolean value representing whether to use the New York Times word
            list or the extended word list which works on all sites (default:
            False)
        allow_print:
            A boolean value representing whether to allow print statements"""
    if allow_print:
        print('Saving all newly discovered data...')
    filename = 'best_guess.json'
    if nyt:
        filename = 'best_guess_nyt.json'
    elif hard:
        filename = 'best_guess_hard.json'
    elif master:
        filename = 'best_guess_master.json'
    elif liar:
        filename = 'best_guess_liar.json'
    if best_guess_updated:
        before = format_bytes(os.path.getsize(data_path + filename))
        with open(data_path + filename, 'w') as bestf:
            dump(saved_best, bestf, sort_keys=True, indent=2)
        after = format_bytes(os.path.getsize(data_path + filename))
        if allow_print:
            print('  "{}"  {:>8} > {:<8}'.format(filename, before, after))
    resp_file = 'responses' + ('_master' if master else '') + '.json'
    if response_data_updated:
        before = format_bytes(os.path.getsize(data_path + resp_file))
        with open(data_path + resp_file, 'w') as responses:
            dump(response_data, responses, sort_keys=True)
        after = format_bytes(os.path.getsize(data_path + resp_file))
        if allow_print:
            print('  "{}"  {:>8} > {:<8}'.format(resp_file, before, after))
    if allow_print:
        print('Save complete.')


def clean_all_data() -> bool:
    """Empties the contents of local files written by the program.

    Will replace all files named "data/best_guess.json", "data/responses.json",
    and each of their variants to relieve some storage space. Additionally, if
    any of the expected files do not exist, this will create the file and write
    an empty dict to that file.

    Returns:
        True if any data was added or deleted successfully, else False.
    """
    filenames = [
        'best_guess.json', 'best_guess_nyt.json', 'best_guess_hard.json',
        'best_guess_master.json', 'best_guess_liar.json', 'responses.json',
        'responses_master.json'
    ]
    deleted = 0
    added = 0
    for filename in filenames:
        try:
            deleted += os.path.getsize(data_path + filename)
        except FileNotFoundError as e:
            pass  # same as adding 0 to deleted
        with open(data_path + filename, 'w') as file:
            dump({}, file)
        added += os.path.getsize(data_path + filename)
    if deleted - added == 0:
        print('Nothing to clean.')
        return False
    print('Data cleaned. {} deleted.'.format(format_bytes(deleted - added)))
    return True
