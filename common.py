import os

from tqdm import tqdm


RIGHT = 'O'
CLOSE = '+'
WRONG = '.'

response_data = {}
response_data_updated = False
best_guess_updated = False
is_ms_os = os.name == 'nt'
progress = '__...:::!!|' if is_ms_os else None


def set_best_guess_updated(value=True):
    global best_guess_updated
    best_guess_updated = value


def get_best_guess_updated():
    return best_guess_updated


def set_response_data_updated(value=True):
    global response_data_updated
    response_data_updated = value


def get_response_data_updated():
    return response_data_updated


def set_response_data(value):
    global response_data
    response_data = value


def get_response_data():
    return response_data


def _get_easy_response(guess, answer):
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


def _get_master_response(guess, answer):
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
        response = _get_master_response(guess, answer)
    else:
        response = _get_easy_response(guess, answer)
    if guess not in response_data:
        response_data[guess] = {}
    response_data[guess][answer] = response
    response_data_updated = True
    return response


def filter_remaining(remaining, guess, response, master, liar=False):
    filtered = []
    if response == ''.join(RIGHT for _ in guess):
        return [guess]
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
    print('Precalculating all possible responses...')
    response_data = dict([(guess, {}) for guess in guesses])
    for guess in tqdm(guesses, ascii=progress):
        for answer in answers:
            response_data[guess][answer] = get_response(guess, answer, master)
    response_data_updated = True
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
