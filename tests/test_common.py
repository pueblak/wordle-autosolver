from pytest import fixture

import wordle_autosolver.common as common
from wordle_autosolver.data import load_all_data


###############################################################################
#                             TEST EASY RESPONSE                              #
###############################################################################


def test_easy_response__no_match():
    assert(common._get_easy_response("ratio", "mucus") == ".....")
    assert(common._get_easy_response("crate", "wilds") == ".....")
    assert(common._get_easy_response("smile", "jocky") == ".....")


def test_easy_response__green_only():
    assert(common._get_easy_response("ratio", "ratio") == "OOOOO")
    assert(common._get_easy_response("ratio", "patio") == ".OOOO")
    assert(common._get_easy_response("ratio", "rated") == "OOO..")
    assert(common._get_easy_response("ratio", "raced") == "OO...")
    assert(common._get_easy_response("ratio", "macho") == ".O..O")
    assert(common._get_easy_response("ratio", "cumin") == "...O.")


def test_easy_response__yellow_only():
    assert(common._get_easy_response("words", "sword") == "+++++")
    assert(common._get_easy_response("overt", "voter") == "+++++")
    assert(common._get_easy_response("ratio", "irate") == "++++.")
    assert(common._get_easy_response("amber", "rhyme") == ".+.++")
    assert(common._get_easy_response("covet", "ovary") == ".++..")
    assert(common._get_easy_response("music", "cover") == "....+")


def test_easy_response__green_and_yellow():
    assert(common._get_easy_response("dates", "sated") == "+OOO+")
    assert(common._get_easy_response("stark", "steak") == "OO+.O")
    assert(common._get_easy_response("rates", "tears") == "++++O")
    assert(common._get_easy_response("hater", "bathe") == "+OO+.")
    assert(common._get_easy_response("haste", "thine") == "+..+O")
    assert(common._get_easy_response("overt", "fresh") == "..O+.")


def test_easy_response__duplicate_letters():
    assert(common._get_easy_response("mamma", "mamma") == "OOOOO")
    assert(common._get_easy_response("dated", "sated") == ".OOOO")
    assert(common._get_easy_response("dated", "dates") == "OOOO.")
    assert(common._get_easy_response("dated", "adder") == "++.O+")
    assert(common._get_easy_response("added", "diced") == ".+.OO")
    assert(common._get_easy_response("diced", "added") == "+..OO")
    assert(common._get_easy_response("troll", "label") == "...+O")
    assert(common._get_easy_response("sassy", "gross") == "+..O.")


###############################################################################
#                            TEST MASTER RESPONSE                             #
###############################################################################


def test_master_response__no_match():
    assert(common._get_master_response("ratio", "mucus") == ".....")
    assert(common._get_master_response("crate", "wilds") == ".....")
    assert(common._get_master_response("smile", "jocky") == ".....")


def test_master_response__green_only():
    assert(common._get_master_response("ratio", "ratio") == "OOOOO")
    assert(common._get_master_response("ratio", "patio") == "OOOO.")
    assert(common._get_master_response("ratio", "rated") == "OOO..")
    assert(common._get_master_response("ratio", "raced") == "OO...")
    assert(common._get_master_response("ratio", "macho") == "OO...")
    assert(common._get_master_response("ratio", "cumin") == "O....")


def test_master_response__yellow_only():
    assert(common._get_master_response("words", "sword") == "+++++")
    assert(common._get_master_response("overt", "voter") == "+++++")
    assert(common._get_master_response("ratio", "irate") == "++++.")
    assert(common._get_master_response("amber", "rhyme") == "+++..")
    assert(common._get_master_response("covet", "ovary") == "++...")
    assert(common._get_master_response("music", "cover") == "+....")


def test_master_response__green_and_yellow():
    assert(common._get_master_response("dates", "sated") == "OOO++")
    assert(common._get_master_response("stark", "steak") == "OOO+.")
    assert(common._get_master_response("rates", "tears") == "O++++")
    assert(common._get_master_response("hater", "bathe") == "OO++.")
    assert(common._get_master_response("haste", "thine") == "O++..")
    assert(common._get_master_response("overt", "fresh") == "O+...")


def test_master_response__duplicate_letters():
    assert(common._get_master_response("mamma", "mamma") == "OOOOO")
    assert(common._get_master_response("dated", "sated") == "OOOO.")
    assert(common._get_master_response("dated", "dates") == "OOOO.")
    assert(common._get_master_response("dated", "adder") == "O+++.")
    assert(common._get_master_response("added", "diced") == "OO+..")
    assert(common._get_master_response("diced", "added") == "OO+..")
    assert(common._get_master_response("troll", "label") == "O+...")
    assert(common._get_master_response("sassy", "gross") == "O+...")


###############################################################################
#                             TEST GET RESPONSE                               #
###############################################################################


def test_get_response__all_easy():
    assert(common.get_response("ratio", "mucus", False, False) == ".....")
    assert(common.get_response("ratio", "macho", False, False) == ".O..O")
    assert(common.get_response("amber", "rhyme", False, False) == ".+.++")
    assert(common.get_response("hater", "bathe", False, False) == "+OO+.")
    assert(common.get_response("added", "diced", False, False) == ".+.OO")


def test_get_response__all_master():
    assert(common.get_response("ratio", "mucus", True, False) == ".....")
    assert(common.get_response("ratio", "macho", True, False) == "OO...")
    assert(common.get_response("amber", "rhyme", True, False) == "+++..")
    assert(common.get_response("hater", "bathe", True, False) == "OO++.")
    assert(common.get_response("added", "diced", True, False) == "OO+..")


###############################################################################
#                           TEST FILTER REMAINING                             #
###############################################################################


@fixture
def example_guess_remaining():
    guess = "trips"
    remaining = ["which", "their", "there", "would", "about", "could", "other",
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
    return guess, remaining


def test_filter_remaining__easy(example_guess_remaining):
    guess, remaining = example_guess_remaining
    assert(common.filter_remaining(remaining, guess, "OOOOO", False,
                                   use_cache=False) == [guess])
    response = common._get_easy_response(guess, "heart")
    assert(common.filter_remaining(remaining, guess, response, False,
                                   use_cache=False)
           == ['other', 'after', 'water', 'later', 'heart', 'court', 'north',
               'earth'])
    response = common._get_easy_response(guess, "child")
    assert(common.filter_remaining(remaining, guess, response, False,
                                   use_cache=False)
           == ['which', 'being', 'while', 'going', 'child', 'voice', 'doing',
               'china'])
    response = common._get_easy_response(guess, "sound")
    assert(common.filter_remaining(remaining, guess, response, False,
                                   use_cache=False)
           == ['house', 'small', 'shall', 'sense', 'close', 'whose', 'shown',
               'cause', 'sound'])


def test_filter_remaining__master(example_guess_remaining):
    guess, remaining = example_guess_remaining
    response = common._get_master_response(guess, "heart")
    assert(common.filter_remaining(remaining, guess, response, True,
                                   use_cache=False)
           == ['other', 'after', 'might', 'state', 'since', 'power', 'water',
               'until', 'later', 'night', 'study', 'light', 'heart', 'least',
               'court', 'space', 'south', 'stood', 'north', 'earth', 'paper',
               'music', 'speak', 'issue', 'stage', 'basic', 'share', 'river'])
    response = common._get_master_response(guess, "child")
    assert(common.filter_remaining(remaining, guess, response, True,
                                   use_cache=False)
           == ['which', 'being', 'while', 'going', 'order', 'table', 'child',
               'voice', 'taken', 'doing', 'class', 'today', 'total', 'focus',
               'wrong', 'green', 'china', 'happy'])
    response = common._get_master_response(guess, "sound")
    assert(common.filter_remaining(remaining, guess, response, True,
                                   use_cache=False)
           == ['about', 'where', 'world', 'never', 'again', 'under', 'place',
               'every', 'house', 'small', 'often', 'given', 'large', 'shall',
               'early', 'sense', 'death', 'heard', 'close', 'clear', 'field',
               'major', 'force', 'whose', 'bible', 'shown', 'cause', 'sound',
               'lower', 'mouth', 'image', 'range', 'media', 'ready', 'floor',
               'final', 'phone', 'round', 'meant'])


def test_filter_remaining__liar(example_guess_remaining):
    guess, remaining = example_guess_remaining
    response = common._get_easy_response(guess, "heart")
    assert(common.filter_remaining(remaining, guess, response, False, True,
                                   False)
           == ['there', 'about', 'where', 'right', 'world', 'never', 'under',
               'three', 'great', 'every', 'often', 'large', 'early', 'death',
               'heard', 'front', 'party', 'short', 'clear', 'story', 'major',
               'force', 'start', 'lower', 'mouth', 'range', 'ready', 'floor',
               'round', 'meant'])
    response = common._get_easy_response(guess, "child")
    assert(common.filter_remaining(remaining, guess, response, False, True,
                                   use_cache=False)
           == ['would', 'could', 'think', 'again', 'found', 'human', 'women',
               'given', 'using', 'among', 'young', 'thing', 'woman', 'level',
               'white', 'value', 'model', 'black', 'along', 'whole', 'known',
               'above', 'began', 'local', 'money', 'quite', 'blood', 'leave',
               'field', 'alone', 'maybe', 'bible', 'bring', 'image', 'legal',
               'below', 'media', 'smile', 'final'])
    response = common._get_easy_response(guess, "sound")
    assert(common.filter_remaining(remaining, guess, response, False, True,
                                   use_cache=False)
           == ['would', 'could', 'these', 'those', 'state', 'found', 'since',
               'human', 'women', 'using', 'study', 'among', 'young', 'woman',
               'level', 'least', 'value', 'model', 'black', 'along', 'whole',
               'known', 'above', 'began', 'local', 'money', 'space', 'blood',
               'class', 'leave', 'south', 'stood', 'alone', 'maybe', 'music',
               'focus', 'legal', 'below', 'speak', 'smile', 'issue', 'stage',
               'basic', 'share'])


###############################################################################
#                           TEST COUNT REMAINING                              #
###############################################################################


def test_count_remaining__easy(example_guess_remaining):
    guess, remaining = example_guess_remaining
    response = common._get_easy_response(guess, "heart")
    assert(common.count_remaining(remaining, guess, response, master=False,
                                  use_cache=False) == 8)
    response = common._get_easy_response(guess, "child")
    assert(common.count_remaining(remaining, guess, response, master=False,
                                  use_cache=False) == 8)
    response = common._get_easy_response(guess, "sound")
    assert(common.count_remaining(remaining, guess, response, master=False,
                                  use_cache=False) == 9)


def test_count_remaining__master(example_guess_remaining):
    guess, remaining = example_guess_remaining
    response = common._get_master_response(guess, "heart")
    assert(common.count_remaining(remaining, guess, response, master=True,
                                  use_cache=False) == 28)
    response = common._get_master_response(guess, "child")
    assert(common.count_remaining(remaining, guess, response, master=True,
                                  use_cache=False) == 18)
    response = common._get_master_response(guess, "sound")
    assert(common.count_remaining(remaining, guess, response, master=True,
                                  use_cache=False) == 39)


def test_count_remaining__liar(example_guess_remaining):
    guess, remaining = example_guess_remaining
    response = common._get_easy_response(guess, "heart")
    assert(common.count_remaining(remaining, guess, response, liar=True,
                                  use_cache=False) == 30)
    response = common._get_easy_response(guess, "child")
    assert(common.count_remaining(remaining, guess, response, liar=True,
                                  use_cache=False) == 39)
    response = common._get_easy_response(guess, "sound")
    assert(common.count_remaining(remaining, guess, response, liar=True,
                                  use_cache=False) == 44)


###############################################################################
#                              TEST BEST GUESSES                              #
###############################################################################


@fixture
def default_answers():
    return load_all_data(False, False, False, False, False)[0]


@fixture
def default_guesses():
    return load_all_data(False, False, False, False, False)[1]


def test_best_guess__easy(default_guesses):
    # note: everything is converted to a set because the order does not matter
    assert(set(common.best_guesses(['lying', 'click', 'cliff', 'pupil',
                                    'cling', 'flick', 'fling', 'clink'],
                                   default_guesses))
           == set(('flick', 'fling', 'clink')))
    assert(set(common.best_guesses(['crown', 'croup', 'crony', 'croon'],
                                   default_guesses))
           == set(('crown', 'croon')))
    assert(set(common.best_guesses(['bring', 'drink', 'brink', 'grind',
                                    'wring'],
                                   default_guesses))
           == set(('bring',)))
    assert(set(common.best_guesses(['penny', 'venue', 'penne', 'peppy'],
                                   default_guesses))
           == set(('penny', 'venue', 'penne', 'peppy')))
    assert(set(common.best_guesses(['track', 'draft', 'actor', 'craft',
                                    'altar', 'tract', 'graft', 'trawl',
                                    'argot'],
                                   default_guesses))
           == set(('diact',)))


def test_best_guess__master(default_guesses):
    # note: everything is converted to a set because the order does not matter
    assert(set(common.best_guesses(['forth', 'motor', 'forum', 'robot',
                                    'booth', 'broth', 'rotor', 'motto',
                                    'froth'],
                                   default_guesses, master=True))
           == set(('robot', 'booth', 'broth', 'rotor')))
    assert(set(common.best_guesses(['allow', 'cloud', 'cloth', 'flora',
                                    'alloy', 'aloof', 'allay', 'aloha'],
                                   default_guesses, master=True))
           == set(('allow', 'cloth', 'flora', 'alloy', 'allay')))
    assert(set(common.best_guesses(['baker', 'maker', 'wager', 'wafer',
                                    'waver', 'gamer', 'gazer', 'faker',
                                    'waxer'],
                                   default_guesses, master=True))
           == set(('wager',)))
    assert(set(common.best_guesses(['women', 'minor'],
                                   default_guesses, master=True))
           == set(('women', 'minor')))


def test_best_guess__return_all():
    worst_case = common.best_guesses(['croup', 'crony', 'crown', 'croon'],
                                     return_all=True)
    assert(worst_case['crown'] == 1)
    assert(worst_case['croon'] == 1)
    assert(worst_case['crony'] == 2)
    assert(worst_case['croup'] == 3)


# def test_best_guess__using_filter_remaining(default_answers, default_guesses):
#     remaining = common.filter_remaining(default_answers, 'ratio', '.....',
#                                         False, use_cache=False)
#     assert(set(common.best_guesses(remaining, default_guesses))
#            == set(('melds', 'lends')))
#     remaining = common.filter_remaining(default_answers, 'spine', '.....',
#                                         True, use_cache=False)
#     assert(set(common.best_guesses(remaining, default_guesses, master=True))
#            == set(('torch',)))


###############################################################################
#                            TEST AVERAGE GUESSES                             #
###############################################################################


def test_average_guess__easy(default_guesses):
    # note: everything is converted to a set because the order does not matter
    assert(set(common.best_avg_guesses(['lying', 'click', 'cliff', 'pupil',
                                        'cling', 'flick', 'fling', 'clink'],
                                       default_guesses))
           == set(('flick', 'fling', 'clink')))
    assert(set(common.best_avg_guesses(['crown', 'croup', 'crony', 'croon'],
                                       default_guesses))
           == set(('crown', 'croon')))
    assert(set(common.best_avg_guesses(['bring', 'drink', 'brink', 'grind',
                                        'wring'],
                                       default_guesses))
           == set(('bring',)))
    assert(set(common.best_avg_guesses(['penny', 'venue', 'penne', 'peppy'],
                                       default_guesses))
           == set(('penny', 'venue', 'penne', 'peppy')))
    assert(set(common.best_avg_guesses(['track', 'draft', 'actor', 'craft',
                                        'altar', 'tract', 'graft', 'trawl',
                                        'argot'],
                                       default_guesses))
           == set(('diact',)))


def test_average_guess__master(default_guesses):
    # note: everything is converted to a set because the order does not matter
    assert(set(common.best_avg_guesses(['forth', 'motor', 'forum', 'robot',
                                        'booth', 'broth', 'rotor', 'motto',
                                        'froth'],
                                       default_guesses, master=True))
           == set(('robot',)))
    assert(set(common.best_avg_guesses(['allow', 'cloud', 'cloth', 'flora',
                                        'alloy', 'aloof', 'allay', 'aloha'],
                                       default_guesses, master=True))
           == set(('allay',)))
    assert(set(common.best_avg_guesses(['baker', 'maker', 'wager', 'wafer',
                                        'waver', 'gamer', 'gazer', 'faker',
                                        'waxer'],
                                       default_guesses, master=True))
           == set(('gowfs',)))
    assert(set(common.best_avg_guesses(['women', 'minor'],
                                       default_guesses, master=True))
           == set(('women', 'minor')))


def test_average_guess__return_all():
    avg_case = common.best_avg_guesses(['croup', 'crony', 'crown', 'croon'],
                                       return_all=True)
    assert(avg_case['crown'] == 1.0)
    assert(avg_case['croon'] == 1.0)
    assert(avg_case['crony'] == 1.5)
    assert(avg_case['croup'] == 2.5)


###############################################################################
#                         TEST REC BUILD BEST TREE                            #
###############################################################################


def test_rec_build_best_tree__simple(default_guesses):
    answers = ['croup', 'crony', 'crown', 'croon']
    assert(common.rec_build_best_tree(answers, default_guesses, 'crown', False,
                                      False, 1, False)
           == {'crown': {
                'OOO..': {'croup': {}},
                'OOO.+': {'crony': {}},
                'OOOOO': {'crown': {}},
                'OOO.O': {'croon': {}}
                }})


def test_rec_build_best_tree__bad(example_guess_remaining, default_guesses):
    _, answers = example_guess_remaining
    assert(common.rec_build_best_tree(answers, default_guesses, 'roate', False,
                                      False, 1, False)
           == {})


def test_rec_build_best_tree__good(example_guess_remaining, default_guesses):
    _, answers = example_guess_remaining
    assert(common.rec_build_best_tree(answers, default_guesses, 'trips', False,
                                      False, 3, False)
           != {})


def test_rec_build_best_tree__best(example_guess_remaining, default_guesses):
    _, answers = example_guess_remaining
    assert(common.rec_build_best_tree(answers, default_guesses, 'roate', False,
                                      False, 2, False)
           != {})


###############################################################################
#                            TEST MISCELLANEOUS                               #
###############################################################################

def test_best_guess_updated():
    common.set_best_guess_updated(True)
    assert(common.get_best_guess_updated() is True)
    common.set_best_guess_updated(False)
    assert(common.get_best_guess_updated() is False)


def test_response_data_updated():
    common.set_response_data_updated(True)
    assert(common.get_response_data_updated() is True)
    common.set_response_data_updated(False)
    assert(common.get_response_data_updated() is False)


def test_response_data():
    response_data = {'alert': {'olive': '.O+..'}}
    common.set_response_data(response_data)
    assert(common.get_response_data()['alert']['olive'] == '.O+..')


def test_colored_response():
    assert(common.colored_response('trips', 'O.+O.', False)
           == ("\x1b[38;5;102m\x1b[48;5;30mT\x1b[0m"
               "R"
               "\x1b[38;5;103m\x1b[48;5;30mI\x1b[0m"
               "\x1b[38;5;102m\x1b[48;5;30mP\x1b[0m"
               "S"))
    assert(common.colored_response('trips', 'OO+..', True)
           == ("\x1b[38;5;102m\x1b[48;5;30mO\x1b[0m"
               "\x1b[38;5;102m\x1b[48;5;30mO\x1b[0m"
               "\x1b[38;5;103m\x1b[48;5;30m+\x1b[0m"
               "."
               "."))
