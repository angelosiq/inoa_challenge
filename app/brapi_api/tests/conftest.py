import json
import os

import pytest

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(name="quote_data")
def quote_json_instance():
    with open(os.path.join(PROJECT_PATH, "json", "quote.json"), "r", encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture(name="quote_list_data")
def quote_list_json_instance():
    with open(os.path.join(PROJECT_PATH, "json", "quote_list.json"), "r", encoding="utf-8") as file:
        return json.load(file)
