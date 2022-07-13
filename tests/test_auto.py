from pytest import fixture

import wordle_autosolver.driver as driver
import wordle_autosolver.auto as auto


def test_driver(monkeypatch):
    monkeypatch.setattr('sys.argv', ['test'])
    driver.parse_command_line_args()
    assert(auto.get_driver() == auto._driver)
    auto.quit_driver()
