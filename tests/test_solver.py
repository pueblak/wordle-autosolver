from pytest import fixture
from io import StringIO

import wordle_autosolver.solver as solver
from wordle_autosolver.data import load_all_data


@fixture
def default_answers():
    return load_all_data(False, False, False, False, False)[0]


@fixture
def default_guesses():
    return load_all_data(False, False, False, False, False)[1]


def test_simulated_guess(default_guesses):
    for guess in default_guesses:
        assert(solver.simulated_guess([[]], [], guess, False, False, False)
               == guess)


def test_simulated_response__easy():
    solver.simulated_answers = ['flour']
    assert(solver.simulated_response('flare', [[]], [], [0], False, False,
                                     False, False)
           == [('OO.+.', 0)])


def test_simulated_response__master():
    solver.simulated_answers = ['flour']
    assert(solver.simulated_response('fluke', [[]], [], [0], False, True,
                                     False, False)
           == [('OO+..', 0)])


def test_manual_guess__easy(monkeypatch, default_guesses):
    input_string = StringIO('ratio\n')
    monkeypatch.setattr('sys.stdin', input_string)
    assert(solver.manual_guess([[]], default_guesses, "", False, False,
                               False, False)
           == "ratio")


def test_manual_guess__invalid_input(monkeypatch, default_guesses):
    input_string = StringIO('xzywp\nchair\n')
    monkeypatch.setattr('sys.stdin', input_string)
    assert(solver.manual_guess([[]], default_guesses, "", False, False,
                               False, False)
           == "chair")


def test_manual_guess__help_command(monkeypatch, default_guesses):
    input_string = StringIO('!help\ncrane\n')
    monkeypatch.setattr('sys.stdin', input_string)
    assert(solver.manual_guess([[]], default_guesses, "crane", False, False,
                               False, False)
           == "crane")


def test_manual_guess__hard(monkeypatch, default_guesses):
    input_string = StringIO('build\nbreak\n')
    monkeypatch.setattr('sys.stdin', input_string)
    assert(solver.manual_guess([["break"]], default_guesses, "", True, False,
                               False, False)
           == "break")


def test_manual_response__easy(monkeypatch, default_answers):
    input_string = StringIO('+oo+.\n')
    monkeypatch.setattr('sys.stdin', input_string)
    response = next(solver.manual_response("hater", [default_answers], [], [0],
                                           False, False, False, False))
    assert(response == ('+OO+.', 0))


def test_manual_response__master(monkeypatch, default_answers):
    input_string = StringIO('OO++.\n')
    monkeypatch.setattr('sys.stdin', input_string)
    response = next(solver.manual_response("swarm", [default_answers], [], [0],
                                           False, True, False, False))
    assert(response == ('OO++.', 0))


def test_manual_response__invalid_input(monkeypatch, default_answers):
    input_string = StringIO('.\n..c..\nOOOO+\n.....\n')
    monkeypatch.setattr('sys.stdin', input_string)
    response = next(solver.manual_response("crazy", [default_answers], [], [0],
                                           False, False, False, False))
    assert(response == ('.....', 0))
