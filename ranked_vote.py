import argparse
from pathlib import Path
from textwrap import dedent

from utils import run_stv, parse_tokens, parse_google_form, filter_valid

parser = argparse.ArgumentParser(
    description=dedent("""
    Run an STV

    This script assumes that a Google form was created with a question on
    it set up in the following way:

      - Multiple-choice grid
      - Limit to one response per colum
      - Require a response in each row

    The name of that question should be passed to this script as `question`.
    """).strip(),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument("ballots", type=Path, help="The CSV from Google Forms")
parser.add_argument("tokens", type=Path, help="The token file")
parser.add_argument("question", type=str, help="The question name on the form")
parser.add_argument("seats", type=int, help="Number of seats to elect")
parser.add_argument("--token_col", type=str, help="The column in the CSV containing the voting token", default="Voting Token")
args = parser.parse_args()

votes = parse_google_form(args.ballots, token_col=args.token_col)
valid_tokens = parse_tokens(args.tokens)
valid_votes, invalid_votes = filter_valid(votes, valid_tokens)

print(f"Running election for {args.seats} seats")

result = run_stv(valid_votes, "Rank candidates", args.seats)
print(result)
