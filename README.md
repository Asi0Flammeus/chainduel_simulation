# Simulation Model of Chain-Duel

Minimalistic model of chain-duel to analyse several strategies 

# Various notes

- illegal move: up/down oscillation observed for AI 
- enhance scoring model
    - does removing points to opponent when food is gained for 1st food change something?
    - add the multiplication factor dependant of snake's length
    - set a maximum score to end game and declare winner
- add simulation mode
    - no grid displayed
    - only score recorded in txt file 
        - each line is a game like `(1,0);(2,0);(2,1)`
    - run it for 1000 simulations
    - add progress bar in cli
