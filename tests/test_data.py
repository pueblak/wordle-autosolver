from pytest import fixture
from random import choice, sample, randint

import wordle_autosolver.data as data


sample_words = ["which", "their", "there", "would", "about", "could", "other",
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
                "share", "happy", "river", "phone", "round", "basis", "meant"]


def test_format_bytes():
    assert(data.format_bytes(1023) == '1023 B')
    assert(data.format_bytes(1024) == '1.000 KB')
    assert(data.format_bytes(35845) == '35.005 KB')
    assert(data.format_bytes(845554722) == '806.384 MB')
    assert(data.format_bytes(687524749610) == '640.307 GB')
    assert(data.format_bytes(10000000000000) == '9.095 TB')
    assert(data.format_bytes(12345678987654321) == '10.965 PB')


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
def random_saved_best(random_response):
    def random_word(): return choice(sample_words)
    return {random_word(): {random_response: {random_word(): {}}}}


@fixture
def random_response_data(random_response):
    def random_word(): return choice(sample_words)
    return {random_word(): {random_word(): random_response}}


@fixture
def random_data(random_saved_best, random_response_data):
    def random_words(amount): return sample(sample_words, amount)
    return (random_words(4), random_words(4), random_words(4),
            dict((word, float(randint(1, 9))) for word in random_words(4)),
            random_saved_best, random_response_data)


def test_save_and_load__easy(random_data):
    data.save_all_data(False, False, False,
                       True, random_data[4],
                       True, random_data[5],
                       False)
    loaded_data = data.load_all_data(False, False, False, False)
    assert(loaded_data[4] == random_data[4])
    assert(loaded_data[5] == random_data[5])


def test_save_and_load__hard(random_data):
    data.save_all_data(True, False, False,
                       True, random_data[4],
                       True, random_data[5],
                       False)
    loaded_data = data.load_all_data(True, False, False, False)
    assert(loaded_data[4] == random_data[4])
    assert(loaded_data[5] == random_data[5])


def test_save_and_load__master(random_data):
    data.save_all_data(False, True, False,
                       True, random_data[4],
                       True, random_data[5],
                       False)
    loaded_data = data.load_all_data(False, True, False, False)
    assert(loaded_data[4] == random_data[4])
    assert(loaded_data[5] == random_data[5])


def test_save_and_load__liar(random_data):
    data.save_all_data(False, False, True,
                       True, random_data[4],
                       True, random_data[5],
                       False)
    loaded_data = data.load_all_data(False, False, True, False)
    assert(loaded_data[4] == random_data[4])
    assert(loaded_data[5] == random_data[5])


def test_save_and_load__nyt(random_data):
    data.save_all_data(False, False, False,
                       True, random_data[4],
                       True, random_data[5],
                       True)
    loaded_data = data.load_all_data(False, False, False, True)
    assert(loaded_data[4] == random_data[4])
    assert(loaded_data[5] == random_data[5])


def test_clean_all_data(random_data):
    _, _, _, _, saved_best, response_data = random_data
    data.save_all_data(False, False, False,
                       True, saved_best,
                       True, response_data,
                       False)
    assert(data.clean_all_data())
    assert(not data.clean_all_data())
