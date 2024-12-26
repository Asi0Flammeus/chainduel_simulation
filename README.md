# Simulation Model of Chain-Duel

Minimalistic model of chain-duel to analyse several strategies 

# Various notes

- enhance scoring model
    - does removing points to opponent when food is gained for 1st food change something?
    - get scoring system and implement it
- rewrite AI strategy
    - player 1 always goes straight to 1st food
    - player 2 does a hairpin for 1st food
    - strat: minimal avoidance + pure seek food
    - start: adapt behavior if can't get food for sure
        - variant 1: goes to the center 
        - variant 2: goes the opposite of the board (other half)
        - variant 3: goes to the less visited quadrant (based on last 3 food positions)
