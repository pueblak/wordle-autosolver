from pytest import raises
from io import StringIO

import wordle_autosolver.solver as solver
from wordle_autosolver.common import GameMode


def test_session_info_to_str(default_session):
    default_session.starters = ['ratio', 'lends', 'bumpy', 'lucky', 'words']
    assert(str(default_session) == (
        '================SESSION_INFO================\n'
        '            # of games: 1\n'
        '             game mode: DEFAULT\n'
        ' # of possible answers: 4208\n'
        '    # of valid guesses: 12959\n'
        '              starters: RATIO, LENDS, BUMPY,\n'
        '                        LUCKY, WORDS\n'
        '         entered words: None\n'
        '             solutions: *****\n'
        '     unentered answers: None\n'
        ' # of unfinished games: 1\n'
        ' # of matching answers: 4208\n'
        ' best guesses [GAME 1]: None\n'
        '    best overall guess: ROATE'
    ))


###############################################################################
#                      TEST SIMULATED GUESS AND RESPONSE                      #
###############################################################################


def test_simulated_guess(default_session):
    for guess in default_session.guesses:
        default_session.actual_best = guess
        assert(solver.simulated_guess(default_session) == guess)


def test_simulated_response__easy(default_session):
    solver.simulated_answers = ['flour']
    default_session.entered = ['flare']
    assert(solver.simulated_response(default_session) == [('OO.+.', 0)])


def test_simulated_response__master(default_session):
    solver.simulated_answers = ['flour']
    default_session.entered = ['fluke']
    default_session.mode = GameMode(GameMode.MASTER)
    assert(solver.simulated_response(default_session) == [('OO+..', 0)])


###############################################################################
#                       TEST MANUAL GUESS AND RESPONSE                        #
###############################################################################


def test_manual_guess__easy(monkeypatch, default_session):
    input_string = StringIO('ratio\n')
    monkeypatch.setattr('sys.stdin', input_string)
    assert(solver.manual_guess(default_session) == "ratio")


def test_manual_guess__invalid_input(monkeypatch, default_session):
    input_string = StringIO('xzywp\nchair\n')
    monkeypatch.setattr('sys.stdin', input_string)
    assert(solver.manual_guess(default_session) == "chair")


def test_manual_guess__help_command(monkeypatch, default_session):
    input_string = StringIO('!help\ncrane\n')
    monkeypatch.setattr('sys.stdin', input_string)
    assert(solver.manual_guess(default_session) == "crane")


def test_manual_guess__hard(monkeypatch, default_session):
    input_string = StringIO('build\nbreak\n')
    monkeypatch.setattr('sys.stdin', input_string)
    default_session.mode = GameMode(GameMode.HARD)
    default_session.remaining[0] = ['break']
    default_session.solved[0] = 'break'
    assert(solver.manual_guess(default_session) == "break")


def test_manual_response__easy(monkeypatch, default_session):
    input_string = StringIO('+oo+.\n')
    monkeypatch.setattr('sys.stdin', input_string)
    default_session.entered = ['hater']
    response = next(solver.manual_response(default_session))
    assert(response == ('+OO+.', 0))


def test_manual_response__master(monkeypatch, default_session):
    input_string = StringIO('OO++.\n')
    monkeypatch.setattr('sys.stdin', input_string)
    default_session.mode = GameMode(GameMode.MASTER)
    default_session.entered = ['swarm']
    response = next(solver.manual_response(default_session))
    assert(response == ('OO++.', 0))


def test_manual_response__invalid_input(monkeypatch, default_session):
    input_string = StringIO('..\n<Mc@:\nOOOO+\n.....\n')
    monkeypatch.setattr('sys.stdin', input_string)
    default_session.entered = ['crazy']
    response = next(solver.manual_response(default_session))
    assert(response == ('.....', 0))


###############################################################################
#                              TEST SOLVE WORDLE                              #
###############################################################################


def test_solve_wordle__bad_response(micro_session):
    micro_session.entered = ['false', 'guess']
    with raises(SystemExit) as e:
        solver._parse_response('XXXXX', 0, solver.simulated_response,
                               micro_session, True)
    assert(e.type == SystemExit)
    assert(e.value.code == 'ERROR: BAD RESPONSE ON BOARD 1: XXXXX')


def test_solve_wordle__easy(tiny_session):
    solver.simulated_answers = ['value']
    result = solver.solve_wordle(
        tiny_session,
        solver.simulated_guess,
        solver.simulated_response,
        True
    )
    assert(result.solved == ['value'])
    assert(result.entered == ['roate', 'value'])


def test_solve_wordle__hard(medium_session):
    solver.simulated_answers = ['short']
    result = solver.solve_wordle(
        medium_session.copy(mode=GameMode(GameMode.HARD)),
        solver.simulated_guess,
        solver.simulated_response,
        True
    )
    assert(result.solved == ['short'])
    assert(result.entered == ['roate', 'front', 'short'])


def test_solve_wordle__simulate_multi(medium_session):
    solver.simulated_answers = ["water", "light", "white", "class"]
    result = solver.solve_wordle(
        medium_session.copy(num_boards=4),
        solver.simulated_guess,
        solver.simulated_response,
        True
    )
    assert(result.solved == ["water", "light", "white", "class"])
    assert(result.entered == ['roate', 'flung', 'water', 'light', 'white',
                              'black', 'class'])


def test_solve_wordle__play_multi(monkeypatch, small_session):
    solver.simulated_answers = ["water", "light", "white", "black", "value"]
    input_str = StringIO('roate\nflung\nwater\nlight\nwhite\nblack\nvalue\n')
    monkeypatch.setattr('sys.stdin', input_str)
    result = solver.solve_wordle(
        small_session.copy(num_boards=5, mode=GameMode(GameMode.PLAY_DEFAULT)),
        solver.manual_guess,
        solver.simulated_response,
        True
    )
    assert(result.solved == ["water", "light", "white", "black", "value"])
    assert(result.entered == ['roate', 'flung', 'water', 'light', 'white',
                              'black', 'value'])


###############################################################################
#                                TEST SIMULATE                                #
###############################################################################


def test_simulate__one_game(mini_session):
    avg, worst = solver.simulate(mini_session)
    assert(round(avg, 2) == 3.94)
    assert(worst == 3)


def test_simulate__two_games(micro_session):
    avg, worst = solver.simulate(micro_session.copy(num_boards=2))
    assert(round(avg, 2) == 3.79)
    assert(worst == 3)


def test_simulate__four_games(micro_session):
    avg, worst = solver.simulate(micro_session.copy(
        num_boards=4,
        answers=["heart", "white", "least", "value", "model", "black"]
    ))
    assert(round(avg, 2) == 4.0)
    assert(worst == 4)


def test_simulate__less_than_max__single(tiny_session):
    avg, worst = solver.simulate(tiny_session.copy(), 16)
    assert(round(avg, 2) >= 3.5)
    assert(worst == 3)


def test_simulate__less_than_max__multi(mini_session):
    avg, worst = solver.simulate(mini_session.copy(num_boards=2), 32)
    assert(round(avg, 2) >= 3.75)
    assert(worst >= 3)


def test_simulate__failure(medium_session):
    _, worst = solver.simulate(medium_session.copy(starters=[
        'these', 'seven', 'words', 'prove', 'fails', 'still', 'occur'
    ]))
    assert(worst < 0)


def test_simulate__return_early(medium_session):
    BEST = 2
    avg, worst = solver.simulate(medium_session.copy(starters=[
        'these', 'seven', 'words', 'prove', 'fails', 'still', 'occur'
    ]), best=BEST, return_if_worse=True)
    assert(avg < BEST)
    assert(worst < BEST)
