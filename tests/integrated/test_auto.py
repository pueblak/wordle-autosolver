import wordle_autosolver.driver as driver
import wordle_autosolver.auto as auto
from wordle_autosolver.common import GameMode
from wordle_autosolver.solver import solve_wordle


def test_driver(monkeypatch):
    monkeypatch.setattr('sys.argv', ['wordle_autosolver', '--auto', 'wordle'])
    driver.parse_command_line_args()
    auto.open_website(auto.SITE_INFO['wordle'][0], 1, quiet=False)
    assert(auto.get_driver() == auto._driver)
    auto.quit_driver()


def test_auto_solver__wordle(default_session):
    mode = GameMode()
    (addr, num_boards, _, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['wordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr)
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__wordle__hard(default_session):
    mode = GameMode(GameMode.HARD)
    (addr, num_boards, _, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['wordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr)
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__dordle(default_session):
    mode = GameMode()
    (addr, num_boards, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['dordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr)
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__quordle(default_session):
    mode = GameMode()
    (addr, num_boards, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['quordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr)
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__octordle(default_session):
    mode = GameMode()
    (addr, num_boards, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['octordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode,
                                     quiet=True, dark=False)
    )
    assert(auto.get_driver().current_url == addr + 'daily')
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__sedecordle(default_session):
    mode = GameMode()
    (addr, num_boards, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['sedecordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr + '?mode=daily')
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__duotrigordle(default_session):
    mode = GameMode()
    (addr, num_boards, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['duotrigordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr)
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__64ordle(default_session):
    mode = GameMode()
    (addr, num_boards, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['64ordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr + '?mode=daily')
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__nordle(default_session):
    NUM_BOARDS = 71
    mode = GameMode()
    (addr, _, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['nordle']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, NUM_BOARDS, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr + str(NUM_BOARDS))
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 5)
    auto.quit_driver()


def test_auto_solver__fibble(default_session):
    mode = GameMode(GameMode.LIAR)
    (addr, num_boards, mode.hard, mode.master, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['fibble']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, num_boards, mode, quiet=True)
    )
    assert(auto.get_driver().current_url == addr)
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 8)
    auto.quit_driver()


def test_auto_solver__wordzy__one_easy(default_session):
    NUM_BOARDS = 1
    mode = GameMode()
    (addr, _, mode.hard, _, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['wordzy']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, NUM_BOARDS, mode, quiet=True)
    )
    assert(auto.get_driver().current_url.startswith(addr))
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 4)
    auto.quit_driver()


def test_auto_solver__wordzy__two_easy(default_session):
    NUM_BOARDS = 2
    mode = GameMode()
    (addr, _, mode.hard, _, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['wordzy']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, NUM_BOARDS, mode, quiet=True)
    )
    assert(auto.get_driver().current_url.startswith(addr))
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 4)
    auto.quit_driver()


def test_auto_solver__wordzy__one_master(default_session):
    NUM_BOARDS = 1
    mode = GameMode(GameMode.MASTER)
    (addr, _, mode.hard, _, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['wordzy']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, NUM_BOARDS, mode, quiet=True)
    )
    assert(auto.get_driver().current_url.startswith(addr))
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 9)
    auto.quit_driver()


def test_auto_solver__wordzy__two_master(default_session):
    NUM_BOARDS = 2
    mode = GameMode(GameMode.MASTER)
    (addr, _, mode.hard, _, mode.liar,
        auto_guess, auto_response) = auto.SITE_INFO['wordzy']
    session = default_session.copy(
        mode=mode,
        num_boards=auto.open_website(addr, NUM_BOARDS, mode, quiet=True)
    )
    assert(auto.get_driver().current_url.startswith(addr))
    session = solve_wordle(session, auto_guess, auto_response)
    assert(len(session.entered) <= session.num_boards + 9)
    auto.quit_driver()
