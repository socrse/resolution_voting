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
python ranked_vote.py --token_col="Please insert your voting token here" ~/Downloads/SocRSE\ Trustee\ elections\ 2023.csv tokens.txt "Please rank the candidates (displayed in random order)" $num_places
```
