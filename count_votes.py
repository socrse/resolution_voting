import argparse

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from matplotlib import ticker


def parse_tokens(token_file: Path):
    with token_file.open() as tokens:
        return set(t.strip() for t in tokens.readlines())


def parse_google_form(csv_file: Path, token_col: str = "Voting Token"):
    """
    This function assumes a certain format for the CSV file where
    there is a column containing the voting token used, and then a
    column for each independent vote held.

    The resolution columns must contain the short name for the
    resolution in square brackets.
    """
    votes = pd.read_csv(csv_file)
    votes = votes.set_index(token_col).drop(columns=["Timestamp"])
    votes.columns = votes.columns.str.replace(r".*\[(.*)\].*", lambda m: m.group(1), regex=True)
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


parser = argparse.ArgumentParser(description="Add up votes for resolutions")
parser.add_argument("ballots", type=Path, help="The CSV from Google Forms")
parser.add_argument("tokens", type=Path, help="The token file")
args = parser.parse_args()

votes = parse_google_form(args.ballots)
valid_tokens = parse_tokens(args.tokens)

valid_votes, invalid_votes = filter_valid(votes, valid_tokens)

# Tally up each resolution
resolutions = {}
for resolution in valid_votes.columns:
    this_vote = valid_votes[resolution]
    resolutions[resolution] = count_votes_simple(this_vote)

resolutions = pd.DataFrame(resolutions, index=["approve", "reject", "abstain", "total"]).transpose()
resolutions["total_votes"] = resolutions["approve"] + resolutions["reject"]
resolutions["approve_percent"] = (resolutions["approve"] / resolutions["total_votes"]) * 100
resolutions["reject_percent"] = (resolutions["reject"] / resolutions["total_votes"]) * 100

resolutions["approved"] = resolutions["approve_percent"] >= 75

print(resolutions[["approve", "reject", "abstain", "approved"]])
print()

# Print out results
labels = []
for res_vote in resolutions.itertuples():
    res = res_vote.Index
    ap = res_vote.approve_percent
    tot = res_vote.total_votes
    ab = res_vote.abstain
    approved = res_vote.approved
    print(f"{res} was {'approved' if approved else 'rejected'} with {ap:.1f}% in favour with {tot} total votes ({ab} abstained)")
    labels.append(f"{res}\n{'✔' if approved else '✘'}")

# Plot results
sns.set_theme()
sns.set_context("poster")
sns.set_style("white")

fig, ax = plt.subplots(figsize=(10, 10 / (4 / 3)), constrained_layout=True)

palette = sns.color_palette("colorblind")

ax.bar(labels, resolutions["approve_percent"], label="Approve", color=palette[2])
ax.bar(labels, resolutions["reject_percent"], bottom=resolutions["approve_percent"], label="Reject", color=palette[3])
# ax.bar(labels, [0, 0, 0])
sns.despine(left=True, top=True, ax=ax)

ax.axline((0, 75), (2, 75), linestyle="--", linewidth=3, color=palette[0])

ax.set_ylabel("Valid votes cast")
ax.set_ylim((0, 100))
ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100, decimals=0))
ax.yaxis.set_major_locator(ticker.FixedLocator([0, 25, 50, 75, 100]))

ax.legend(loc="lower right")

fig.savefig("votes.png")
