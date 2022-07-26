import wordle_autosolver.data as data


def test_format_bytes():
    assert(data.format_bytes(1023) == '1023 B')
    assert(data.format_bytes(1024) == '1.000 KB')
    assert(data.format_bytes(35845) == '35.005 KB')
    assert(data.format_bytes(845554722) == '806.384 MB')
    assert(data.format_bytes(687524749610) == '640.307 GB')
    assert(data.format_bytes(10000000000000) == '9.095 TB')
    assert(data.format_bytes(12345678987654321) == '10.965 PB')


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
