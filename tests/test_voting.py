from pathlib import Path

import pytest
import pandas as pd

from utils import parse_google_form


@pytest.fixture(scope="module")
def simple_file():
    test_dir = Path(__file__).resolve().parent
    return parse_google_form(test_dir / "votes.csv", "Token")


def test_parse_csv(simple_file):
    assert pd.api.types.is_string_dtype(simple_file.index)
    assert simple_file.index.is_unique
    assert all(pd.api.types.is_string_dtype(c) for _, c in simple_file.items())
