from pytest import fixture
from io import StringIO

import wordle_autosolver.solver as solver
from wordle_autosolver.data import load_all_data
from wordle_autosolver.common import GameMode


@fixture
def default_answers():
    return load_all_data(False, False, False, False, False)[0]


@fixture
def default_guesses():
    return load_all_data(False, False, False, False, False)[1]


@fixture
def default_session():
    answers, guesses, _, freq, saved_best, _ = load_all_data(
        False, False, False, False, False)
    session = solver.SessionInfo(1, answers, guesses, saved_best, freq, [])
    session.actual_best = 'roate'
    return session


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
