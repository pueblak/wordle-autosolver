from pytest import fixture

import wordle_autosolver.common as common
from wordle_autosolver.data import load_all_data


###############################################################################
#                             TEST GAME MODE ENUM                             #
###############################################################################


def test_game_mode_enum__default():
    mode = common.GameMode()
    assert(mode.default)
    assert(not mode.hard)
    assert(not mode.master)
    assert(not mode.liar)
    assert(not mode.play)
    assert(not mode.endless)
    assert(str(mode) == 'DEFAULT')
    mode.default = False
    assert(not mode.default)


def test_game_mode_enum__hard():
    mode = common.GameMode()
    mode.hard = True
    assert(not mode.default)
    assert(mode.hard)
    assert(not mode.master)
    assert(not mode.liar)
    assert(not mode.play)
    assert(not mode.endless)
    assert(str(mode) == 'HARD')
    mode.hard = False
    assert(not mode.hard)


def test_game_mode_enum__master():
    mode = common.GameMode()
    mode.master = True
    assert(not mode.default)
    assert(not mode.hard)
    assert(mode.master)
    assert(not mode.liar)
    assert(not mode.play)
    assert(not mode.endless)
    assert(str(mode) == 'MASTER')
    mode.master = False
    assert(not mode.master)


def test_game_mode_enum__liar():
    mode = common.GameMode()
    mode.liar = True
    assert(not mode.default)
    assert(not mode.hard)
    assert(not mode.master)
    assert(mode.liar)
    assert(not mode.play)
    assert(not mode.endless)
    assert(str(mode) == 'LIAR')
    mode.liar = False
    assert(not mode.liar)


def test_game_mode_enum__endless():
    mode = common.GameMode()
    mode.endless = True
    assert(mode.default)
    assert(not mode.hard)
    assert(not mode.master)
    assert(not mode.liar)
    assert(not mode.play)
    assert(mode.endless)
    assert(str(mode) == 'DEFAULT_ENDLESS')
    mode.endless = False
    assert(not mode.endless)


def test_game_mode_enum__play():
    mode = common.GameMode()
    mode.play = True
    assert(mode.default)
    assert(not mode.hard)
    assert(not mode.master)
    assert(not mode.liar)
    assert(mode.play)
    assert(not mode.endless)
    assert(str(mode) == 'PLAY_DEFAULT')
    mode.play = False
    assert(not mode.play)


def test_game_mode_enum__complex():
    mode = common.GameMode(common.GameMode.PLAY_HARD_ENDLESS)
    assert(not mode.default)
    assert(mode.hard)
    assert(not mode.master)
    assert(not mode.liar)
    assert(mode.play)
    assert(mode.endless)
    assert(repr(mode) == 'GameMode.PLAY_HARD_ENDLESS')
    mode = common.GameMode(common.GameMode.MASTER_ENDLESS)
    assert(not mode.default)
    assert(not mode.hard)
    assert(mode.master)
    assert(not mode.liar)
    assert(not mode.play)
    assert(mode.endless)
    mode = common.GameMode(common.GameMode.PLAY_LIAR)
    assert(not mode.default)
    assert(not mode.hard)
    assert(not mode.master)
    assert(mode.liar)
    assert(mode.play)
    assert(not mode.endless)
    assert(mode == common.GameMode(common.GameMode.PLAY_LIAR))


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
    mode = common.GameMode()
    assert(common.get_response("ratio", "mucus", mode, use_cache=False)
           == ".....")
    assert(common.get_response("ratio", "macho", mode, use_cache=False)
           == ".O..O")
    assert(common.get_response("amber", "rhyme", mode, use_cache=False)
           == ".+.++")
    assert(common.get_response("hater", "bathe", mode, use_cache=False)
           == "+OO+.")
    assert(common.get_response("added", "diced", mode, use_cache=False)
           == ".+.OO")


def test_get_response__all_master():
    mode = common.GameMode(common.GameMode.MASTER)
    assert(common.get_response("ratio", "mucus", mode, use_cache=False)
           == ".....")
    assert(common.get_response("ratio", "macho", mode, use_cache=False)
           == "OO...")
    assert(common.get_response("amber", "rhyme", mode, use_cache=False)
           == "+++..")
    assert(common.get_response("hater", "bathe", mode, use_cache=False)
           == "OO++.")
    assert(common.get_response("added", "diced", mode, use_cache=False)
           == "OO+..")


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
    mode = common.GameMode()
    guess, remaining = example_guess_remaining
    assert(common.filter_remaining(remaining, guess, "OOOOO", mode,
                                   use_cache=False) == [guess])
    response = common._get_easy_response(guess, "heart")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['other', 'after', 'water', 'later', 'heart', 'court', 'north',
               'earth'])
    response = common._get_easy_response(guess, "child")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['which', 'being', 'while', 'going', 'child', 'voice', 'doing',
               'china'])
    response = common._get_easy_response(guess, "sound")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['house', 'small', 'shall', 'sense', 'close', 'whose', 'shown',
               'cause', 'sound'])


def test_filter_remaining__master(example_guess_remaining):
    mode = common.GameMode(common.GameMode.MASTER)
    guess, remaining = example_guess_remaining
    response = common._get_master_response(guess, "heart")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['other', 'after', 'might', 'state', 'since', 'power', 'water',
               'until', 'later', 'night', 'study', 'light', 'heart', 'least',
               'court', 'space', 'south', 'stood', 'north', 'earth', 'paper',
               'music', 'speak', 'issue', 'stage', 'basic', 'share', 'river'])
    response = common._get_master_response(guess, "child")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['which', 'being', 'while', 'going', 'order', 'table', 'child',
               'voice', 'taken', 'doing', 'class', 'today', 'total', 'focus',
               'wrong', 'green', 'china', 'happy'])
    response = common._get_master_response(guess, "sound")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['about', 'where', 'world', 'never', 'again', 'under', 'place',
               'every', 'house', 'small', 'often', 'given', 'large', 'shall',
               'early', 'sense', 'death', 'heard', 'close', 'clear', 'field',
               'major', 'force', 'whose', 'bible', 'shown', 'cause', 'sound',
               'lower', 'mouth', 'image', 'range', 'media', 'ready', 'floor',
               'final', 'phone', 'round', 'meant'])


def test_filter_remaining__liar(example_guess_remaining):
    mode = common.GameMode(common.GameMode.LIAR)
    guess, remaining = example_guess_remaining
    response = common._get_easy_response(guess, "heart")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['there', 'about', 'where', 'right', 'world', 'never', 'under',
               'three', 'great', 'every', 'often', 'large', 'early', 'death',
               'heard', 'front', 'party', 'short', 'clear', 'story', 'major',
               'force', 'start', 'lower', 'mouth', 'range', 'ready', 'floor',
               'round', 'meant'])
    response = common._get_easy_response(guess, "child")
    assert(common.filter_remaining(remaining, guess, response, mode,
                                   use_cache=False)
           == ['would', 'could', 'think', 'again', 'found', 'human', 'women',
               'given', 'using', 'among', 'young', 'thing', 'woman', 'level',
               'white', 'value', 'model', 'black', 'along', 'whole', 'known',
               'above', 'began', 'local', 'money', 'quite', 'blood', 'leave',
               'field', 'alone', 'maybe', 'bible', 'bring', 'image', 'legal',
               'below', 'media', 'smile', 'final'])
    response = common._get_easy_response(guess, "sound")
    assert(common.filter_remaining(remaining, guess, response, mode,
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
    mode = common.GameMode()
    guess, remaining = example_guess_remaining
    response = common._get_easy_response(guess, "heart")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 8)
    response = common._get_easy_response(guess, "child")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 8)
    response = common._get_easy_response(guess, "sound")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 9)


def test_count_remaining__master(example_guess_remaining):
    mode = common.GameMode(common.GameMode.MASTER)
    guess, remaining = example_guess_remaining
    response = common._get_master_response(guess, "heart")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 28)
    response = common._get_master_response(guess, "child")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 18)
    response = common._get_master_response(guess, "sound")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 39)


def test_count_remaining__liar(example_guess_remaining):
    mode = common.GameMode(common.GameMode.LIAR)
    guess, remaining = example_guess_remaining
    response = common._get_easy_response(guess, "heart")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 30)
    response = common._get_easy_response(guess, "child")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 39)
    response = common._get_easy_response(guess, "sound")
    assert(common.count_remaining(remaining, guess, response, mode,
                                  use_cache=False)
           == 44)


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
                                   default_guesses, use_cache=False))
           == set(['flick', 'fling', 'clink']))
    assert(set(common.best_guesses(['crown', 'croup', 'crony', 'croon'],
                                   default_guesses, use_cache=False))
           == set(['crown', 'croon']))
    assert(set(common.best_guesses(['bring', 'drink', 'brink', 'grind',
                                    'wring'],
                                   default_guesses, use_cache=False))
           == set(['bring']))
    assert(set(common.best_guesses(['penny', 'venue', 'penne', 'peppy'],
                                   default_guesses, use_cache=False))
           == set(['penny', 'venue', 'penne', 'peppy']))
    assert(set(common.best_guesses(['track', 'draft', 'actor', 'craft',
                                    'altar', 'tract', 'graft', 'trawl',
                                    'argot'],
                                   default_guesses, use_cache=False))
           == set(['diact']))


def test_best_guess__master(default_guesses):
    mode = common.GameMode(common.GameMode.MASTER)
    # note: everything is converted to a set because the order does not matter
    assert(set(common.best_guesses(['forth', 'motor', 'forum', 'robot',
                                    'booth', 'broth', 'rotor', 'motto',
                                    'froth'],
                                   default_guesses, mode, use_cache=False))
           == set(['booth', 'broth', 'robot', 'rotor']))
    assert(set(common.best_guesses(['allow', 'cloud', 'cloth', 'flora',
                                    'alloy', 'aloof', 'allay', 'aloha'],
                                   default_guesses, mode, use_cache=False))
           == set(['allow', 'alloy', 'allay', 'flora', 'cloth']))
    assert(set(common.best_guesses(['baker', 'maker', 'wager', 'wafer',
                                    'waver', 'gamer', 'gazer', 'faker',
                                    'waxer'],
                                   default_guesses, mode, use_cache=False))
           == set(['wager']))
    assert(set(common.best_guesses(['women', 'minor'],
                                   default_guesses, mode, use_cache=False))
           == set(['women', 'minor']))


def test_best_guess__return_all():
    worst_case = common.best_guesses(['croup', 'crony', 'crown', 'croon'],
                                     return_all=True, use_cache=False)
    assert(worst_case['crown'] == 1)
    assert(worst_case['croon'] == 1)
    assert(worst_case['crony'] == 2)
    assert(worst_case['croup'] == 3)


# def test_best_guess__using_filter_remaining(default_answers, default_guesses)
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
                                       default_guesses, use_cache=False))
           == set(['flick', 'fling', 'clink']))
    assert(set(common.best_avg_guesses(['crown', 'croup', 'crony', 'croon'],
                                       default_guesses, use_cache=False))
           == set(['crown', 'croon']))
    assert(set(common.best_avg_guesses(['bring', 'drink', 'brink', 'grind',
                                        'wring'],
                                       default_guesses, use_cache=False))
           == set(['bring']))
    assert(set(common.best_avg_guesses(['penny', 'venue', 'penne', 'peppy'],
                                       default_guesses, use_cache=False))
           == set(['penny', 'venue', 'penne', 'peppy']))
    assert(set(common.best_avg_guesses(['track', 'draft', 'actor', 'craft',
                                        'altar', 'tract', 'graft', 'trawl',
                                        'argot'],
                                       default_guesses, use_cache=False))
           == set(['diact']))


def test_average_guess__master(default_guesses):
    mode = common.GameMode(common.GameMode.MASTER)
    # note: everything is converted to a set because the order does not matter
    assert(set(common.best_avg_guesses(['baker', 'maker', 'wager', 'wafer',
                                        'waver', 'gamer', 'gazer', 'faker',
                                        'waxer'],
                                       default_guesses, mode, use_cache=False))
           == set(['gowfs']))


def test_average_guess__return_all():
    avg_case = common.best_avg_guesses(['croup', 'crony', 'crown', 'croon'],
                                       return_all=True, use_cache=False)
    assert(avg_case['crown'] == 1.0)
    assert(avg_case['croon'] == 1.0)
    assert(avg_case['crony'] == 1.5)
    assert(avg_case['croup'] == 2.5)


###############################################################################
#                         TEST REC BUILD BEST TREE                            #
###############################################################################


def test_rec_build_best_tree__empty(example_guess_remaining, default_guesses):
    _, answers = example_guess_remaining
    assert(common.rec_build_best_tree(answers, default_guesses, 'roate',
                                      show=False)
           == {})


def test_rec_build_best_tree__simple(default_guesses):
    answers = ['croup', 'crony', 'crown', 'croon']
    assert(common.rec_build_best_tree(answers, default_guesses, 'crown',
                                      depth=1, show=False)
           == {'crown': {
                'OOO..': {'croup': {}},
                'OOO.+': {'crony': {}},
                'OOOOO': {'crown': {}},
                'OOO.O': {'croon': {}}
                }})


def test_rec_build_best_tree__bad(example_guess_remaining, default_guesses):
    _, answers = example_guess_remaining
    assert(common.rec_build_best_tree(answers, default_guesses, 'roate',
                                      depth=1, show=False)
           == {})


def test_rec_build_best_tree__good(example_guess_remaining, default_guesses):
    _, answers = example_guess_remaining
    assert(common.rec_build_best_tree(answers, default_guesses, 'trips',
                                      depth=3, show=False)
           != {})


def test_rec_build_best_tree__best(example_guess_remaining, default_guesses):
    _, answers = example_guess_remaining
    assert(common.rec_build_best_tree(answers, default_guesses, 'roate',
                                      depth=2, show=False)
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
    assert(common.colored_response('trips', 'O.+O.', common.GameMode())
           == ("\x1b[38;5;102m\x1b[48;5;30mT\x1b[0m"
               "R"
               "\x1b[38;5;103m\x1b[48;5;30mI\x1b[0m"
               "\x1b[38;5;102m\x1b[48;5;30mP\x1b[0m"
               "S"))
    assert(common.colored_response('trips', 'OO+..',
                                   common.GameMode(common.GameMode.MASTER))
           == ("\x1b[38;5;102m\x1b[48;5;30mO\x1b[0m"
               "\x1b[38;5;102m\x1b[48;5;30mO\x1b[0m"
               "\x1b[38;5;103m\x1b[48;5;30m+\x1b[0m"
               "."
               "."))
