import argparse

from pathlib import Path
from textwrap import dedent

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from matplotlib import ticker

from utils import parse_tokens, parse_google_form, filter_valid, count_votes_simple

parser = argparse.ArgumentParser(
    description=dedent("""
    Add up votes for resolutions

    This script assumes that a Google form was created with a question
    on it set up in the following way:

      - Multiple-choice grid
      - Require a response in each row

    The name of that question should be passed to this script as `question`.
    """).strip(),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument("ballots", type=Path, help="The CSV from Google Forms")
parser.add_argument("tokens", type=Path, help="The token file")
parser.add_argument("question", type=str, help="The question name on the form")
parser.add_argument("--token_col", type=str, help="The column in the CSV containing the voting token", default="Voting Token")
args = parser.parse_args()

votes = parse_google_form(args.ballots, token_col=args.token_col)
valid_tokens = parse_tokens(args.tokens)

votes = votes.loc[:, votes.columns.str.startswith(f"{args.question} [")]
votes.columns = votes.columns.str.replace(r".*\[(.*)\].*", lambda m: m.group(1), regex=True)


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
