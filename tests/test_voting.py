from pathlib import Path

import pytest
import pandas as pd

from utils import parse_google_form, run_stv, count_votes_simple


@pytest.fixture(scope="module")
def simple_file():
    test_dir = Path(__file__).resolve().parent
    return parse_google_form(test_dir / "votes.csv", "Token")


def test_parse_csv(simple_file):
    assert pd.api.types.is_string_dtype(simple_file.index)
    assert simple_file.index.is_unique
    assert all(pd.api.types.is_string_dtype(c) for _, c in simple_file.items())
    assert "Resolutions" in simple_file.columns
    assert "Resolution 1" in simple_file["Resolutions"]


def test_stv(simple_file):
    res = run_stv(simple_file, "Rank candidates required", 1)
    winners = res.get_winners()
    assert len(winners) == 1
    assert winners[0].name == "Person 1"


def test_simple(simple_file):
    res = count_votes_simple(simple_file["Resolutions"]["Resolution 1"])
    assert res == (2, 3, 2, 5)
