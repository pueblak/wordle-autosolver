from pytest import fixture
from random import choice, sample, randint

from wordle_autosolver.data import load_all_data
from wordle_autosolver.solver import SessionInfo, solve_wordle
from wordle_autosolver.auto import open_website, quit_driver


@fixture
def default_answers():
    return load_all_data(False, False, False, False, False)[0]


@fixture
def default_guesses():
    return load_all_data(False, False, False, False, False)[1]


@fixture
def small_sample_words():
    return [
        'flick', 'fling', 'clink', 'crown', 'croon', 'bring', 'diact', 'penny',
        'venue', 'penne', 'peppy', 'booth', 'broth', 'robot', 'rotor', 'wager',
        'allow', 'alloy', 'allay', 'flora', 'cloth', 'women', 'minor', 'gowfs',
        'three', 'great', 'every', 'often', 'large', 'early', 'death', 'round',
        'lower', 'mouth', 'image', 'range', 'media', 'ready', 'floor', 'steal'
    ]


@fixture
def sample_words():
    return [
        "which", "their", "there", "would", "about", "could", "other",
        "these", "first", "after", "where", "those", "being", "while",
        "right", "world", "still", "think", "never", "again", "might",
        "under", "three", "state", "going", "place", "found", "great",
        "every", "since", "power", "human", "water", "house", "women",
        "small", "often", "order", "point", "given", "until", "using",
        "table", "group", "press", "large", "later", "night", "study",
        "among", "young", "shall", "early", "thing", "woman", "level",
        "light", "heart", "white", "least", "value", "model", "black",
        "along", "whole", "known", "child", "voice", "sense", "death",
        "above", "taken", "began", "local", "heard", "doing", "front",
        "money", "close", "court", "party", "space", "short", "quite",
        "clear", "blood", "story", "class", "leave", "field", "third",
        "today", "south", "major", "force", "stood", "alone", "whose",
        "maybe", "start", "bible", "shown", "total", "cause", "north",
        "sound", "tried", "earth", "bring", "lower", "truth", "paper",
        "music", "focus", "mouth", "image", "range", "legal", "below",
        "trade", "media", "ready", "wrong", "speak", "green", "floor",
        "china", "smile", "issue", "stage", "basic", "final", "cross",
        "share", "happy", "river", "phone", "round", "basis", "meant"
    ]


@fixture
def example_guess_remaining(sample_words):
    return "trips", sample_words


@fixture
def random_response():
    valid = False
    response = ''
    while not valid:
        response = ''.join(sample(['O', '+', '.'] * 5, 5))
        a, b, c = 0, 0, 0
        for sym in response:
            if sym == 'O':
                a += 1
            elif sym == '+':
                b += 1
            elif sym == '.':
                c += 1
        valid = not (a == 4 and b == 1)
    return response


@fixture
def random_saved_best(random_response, sample_words):
    def random_word(): return choice(sample_words)
    return {random_word(): {random_response: {random_word(): {}}}}


@fixture
def random_response_data(random_response, sample_words):
    def random_word(): return choice(sample_words)
    return {random_word(): {random_word(): random_response}}


@fixture
def random_data(random_saved_best, random_response_data, sample_words):
    def random_words(amount): return sample(sample_words, amount)
    return (random_words(4), random_words(4), random_words(4),
            dict((word, float(randint(1, 9))) for word in random_words(4)),
            random_saved_best, random_response_data)


@fixture
def default_session():
    answers, guesses, _, freq, saved_best, _ = load_all_data(
        False, False, False, False, False)
    session = SessionInfo(1, answers, guesses, saved_best, freq, ['roate'])
    return session


@fixture
def medium_session():
    answers = [
        "which", "their", "there", "would", "about", "could", "other", "these",
        "first", "after", "where", "those", "being", "while", "right", "world",
        "still", "think", "never", "again", "might", "under", "three", "state",
        "going", "place", "found", "great", "every", "since", "power", "human",
        "water", "house", "women", "small", "often", "order", "point", "given",
        "until", "using", "table", "seven", "press", "large", "later", "night",
        "study", "among", "young", "shall", "early", "thing", "woman", "level",
        "light", "heart", "white", "least", "value", "model", "black", "along",
        "whole", "known", "child", "voice", "sense", "death", "above", "taken",
        "began", "local", "heard", "doing", "front", "money", "close", "court",
        "party", "space", "short", "quite", "clear", "blood", "story", "class",
        "leave", "field", "third", "today", "south", "major", "force", "stood",
        "alone", "whose", "maybe", "start", "bible", "shown", "total", "cause",
        "north", "sound", "tried", "earth", "bring", "lower", "truth", "paper",
        "music", "focus", "mouth", "image", "range", "legal", "below", "trade",
        "media", "ready", "wrong", "speak", "green", "floor", "china", "smile",
        "issue", "stage", "basic", "final", "cross", "share", "happy", "river",
        "phone", "round", "basis", "meant", "occur", "group", "words", "fails"
    ]
    _, guesses, _, freq, saved_best, _ = load_all_data(
        False, False, False, False, False)
    session = SessionInfo(1, answers, guesses, saved_best, freq, ['roate'])
    return session


@fixture
def small_session():
    answers = [
        "which", "their", "there", "would", "about", "could", "other", "music",
        "these", "first", "after", "where", "those", "being", "while", "focus",
        "right", "world", "still", "think", "never", "again", "might", "paper",
        "every", "since", "power", "human", "water", "house", "women", "truth",
        "table", "group", "press", "large", "later", "night", "study", "lower",
        "light", "heart", "white", "least", "value", "model", "black", "earth",
        "today", "south", "major", "force", "stood", "alone", "whose", "sound",
        "maybe", "start", "bible", "shown", "total", "cause", "north", "mouth"
    ]
    _, guesses, _, freq, saved_best, _ = load_all_data(
        False, False, False, False, False)
    session = SessionInfo(1, answers, guesses, saved_best, freq, ['roate'])
    return session


@fixture
def tiny_session():
    answers = [
        "right", "world", "still", "think", "never", "again", "might", "paper",
        "every", "since", "power", "human", "water", "house", "women", "truth",
        "light", "heart", "white", "least", "value", "model", "black", "earth",
        "maybe", "start", "bible", "shown", "total", "cause", "north", "mouth"
    ]
    _, guesses, _, freq, saved_best, _ = load_all_data(
        False, False, False, False, False)
    session = SessionInfo(1, answers, guesses, saved_best, freq, ['roate'])
    return session


@fixture
def mini_session():
    answers = [
        "every", "since", "power", "human", "water", "house", "women", "truth",
        "light", "heart", "white", "least", "value", "model", "black", "earth"
    ]
    _, guesses, _, freq, saved_best, _ = load_all_data(
        False, False, False, False, False)
    session = SessionInfo(1, answers, guesses, saved_best, freq, ['roate'])
    return session


@fixture
def micro_session():
    answers = [
        "leant", "heart", "white", "least", "value", "model", "black", "earth"
    ]
    _, guesses, _, freq, saved_best, _ = load_all_data(
        False, False, False, False, False)
    session = SessionInfo(1, answers, guesses, saved_best, freq, ['roate'])
    return session
