# Voting scripts

The two scripts `count_votes.py` and `ranked_vote.py` are used to perform voting.

## Trustee elections

The process to run this code for the 2023 elections should be as follows.

```bash
# Install code
conda create -n socrse2023 python
conda activate socrse2023
pip install -r requirements.txt

# Run voting
python ranked_vote.py --token_col="Please insert your voting token here" ~/Downloads/SocRSE\ Trustee\ elections\ 2023.csv tokens.txt "Candidate ranking" 7
```

### Token mapping

In the 2026 election multiple sets of tokens were generated accidentally.
A new `--token_map` argument has been created for such situations.
It allows you to provide a 2-column CSV file, with column headings 'old' and 'new', mapping between valid tokens for each voter.
For instance, you can run:

```bash
python ranked_vote.py --token_col="Please insert your voting token here" --token_map token_map.csv SocRSE\ Trustee\ elections\ 2026.csv tokens.txt "Candidate ranking" 5
```
