import argparse

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import tabulate

from matplotlib import ticker

parser = argparse.ArgumentParser(description="Add up votes for resolutions")
parser.add_argument("ballots", type=Path, help="The CSV from Google Forms")
parser.add_argument("tokens", type=Path, help="The token file")

args = parser.parse_args()

with args.tokens.open() as tokens:
    valid_tokens = set(t.strip() for t in tokens.readlines())

# Read in the ballots
votes = pd.read_csv(args.ballots)
votes = votes.set_index("Voting Token").drop(columns=["Timestamp"])
votes.columns = votes.columns.str.replace(r".*\[(.*)\].*", lambda m: m.group(1), regex=True)

# Filter out invalid tokens
#valid_votes = votes.loc[votes.index.intersection(valid_tokens)]
#invalid_votes = votes.loc[votes.index.difference(valid_tokens)]
#print("Invalid votes:")
#print(invalid_votes)
#print("\n")
valid_votes = votes

# Tally up each resolution
resolutions = {}
for resolution in valid_votes.columns:
    this_vote = votes[resolution]
    keep_votes = this_vote[~this_vote.index.duplicated(keep="last")]
    vote_counts = keep_votes.value_counts()
    approve = vote_counts.get("Approve", 0)
    reject = vote_counts.get("Reject", 0)
    abstain = vote_counts.get("Abstain", 0)
    total_ballots = len(valid_votes)
    #print(total_ballots, approve, reject, abstain)
    #assert total_ballots == approve + reject + abstain
    votes_cast = approve + reject
    #resolutions[resolution] = ((approve/votes_cast)*100, (reject/votes_cast)*100, abstain, votes_cast)
    resolutions[resolution] = (approve, reject, abstain, votes_cast)

resolutions = pd.DataFrame(resolutions, index=["approve", "reject", "abstain", "total"]).transpose()
resolutions["total_votes"] = resolutions["approve"] + resolutions["reject"]
resolutions["approve_percent"] = (resolutions["approve"] / resolutions["total_votes"]) * 100
resolutions["reject_percent"] = (resolutions["reject"] / resolutions["total_votes"]) * 100

print(resolutions[["approve", "reject", "abstain"]])
print()

# Print out results
labels = []
for res_vote in resolutions.itertuples():
    res = res_vote.Index
    ap = res_vote.approve_percent
    tot = res_vote.total_votes
    ab = res_vote.abstain
    approved = ap >= 75
    print(f"{res} was {'approved' if approved else 'rejected'} with {ap:.1f}% in favour with {tot} total votes ({ab} abstained)")
    labels.append(f"{res}\n{'✔' if approved else '✘'}")
    #labels.append(res)

# Plot results
sns.set_theme()
sns.set_context("poster")
sns.set_style("white")

fig, ax = plt.subplots(figsize=(10, 10/(4/3)), constrained_layout=True)

palette = sns.color_palette("colorblind")

ax.bar(labels, resolutions["approve_percent"], label="Approve", color=palette[2])
ax.bar(labels, resolutions["reject_percent"], bottom=resolutions["approve_percent"], label="Reject", color=palette[3])
#ax.bar(labels, [0, 0, 0])
sns.despine(left=True, top=True, ax=ax)

ax.axline((0, 75), (2, 75), linestyle="--", linewidth=3, color=palette[0])

ax.set_ylabel("Valid votes cast")
ax.set_ylim((0, 100))
ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=100, decimals=0))
ax.yaxis.set_major_locator(ticker.FixedLocator([0, 25, 50, 75, 100]))

ax.legend(loc="lower right")

fig.savefig("votes.png")
