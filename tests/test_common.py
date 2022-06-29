import wordle_autosolver.common as common


def test_easy_response():
    assert(common._get_easy_response("ratio", "patio") == ".OOOO")


def test_master_response():
    assert(common._get_master_response("ratio", "patio") == "OOOO.")
