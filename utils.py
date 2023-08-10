from pathlib import Path

import pandas as pd
import pyrankvote as rv


def run_stv(votes: pd.DataFrame, question, seats):
    votes = votes.loc[:, votes.columns.str.startswith(f"{question} [")]
    votes.columns = votes.columns.str.replace(r".*\[(.*)\].*", lambda m: m.group(1), regex=True)

    candidates = {c: rv.Candidate(c) for c in votes.columns}

    ballots = [rv.Ballot(ranked_candidates=[candidates[c] for c in b[1].sort_values().index]) for b in votes.iterrows()]

    r = rv.single_transferable_vote(candidates.values(), ballots, number_of_seats=seats)
    return r


def parse_tokens(token_file: Path):
    with token_file.open() as tokens:
        return set(t.strip() for t in tokens.readlines())


def parse_google_form(csv_file: Path, token_col: str):
    votes = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
    votes = votes.drop_duplicates(subset=[token_col], keep="last")
    votes = votes.set_index(token_col).drop(columns=["Timestamp"])
    return votes


def filter_valid(df: pd.DataFrame, tokens: set[str]):
    """Filter out invalid tokens"""
    valid = df.loc[df.index.intersection(tokens)]
    invalid = df.loc[df.index.difference(tokens)]
    return valid, invalid


def count_votes_simple(this_vote: pd.Series):
    # If a person voted more than once, only the last vote is counted
    keep_votes = this_vote[~this_vote.index.duplicated(keep="last")]
    vote_counts = keep_votes.value_counts()
    approve = vote_counts.get("Approve", 0)
    reject = vote_counts.get("Reject", 0)
    abstain = vote_counts.get("Abstain", 0)
    votes_cast = approve + reject
    return approve, reject, abstain, votes_cast
