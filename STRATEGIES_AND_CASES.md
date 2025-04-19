# AI Strategies

- **AggressiveAnticipationStrategy**: An aggressive strategy that actively challenges for food position.
- **NoisyAdaptiveAggressiveStrategy**: An aggressive strategy that adapts to the situation with random noise for unpredictability.
- **SafeFoodSeekingStrategy**: A balanced strategy that considers both food and safety.
- **SuperiorAdaptiveStrategy**: Advanced strategy using pathfinding, territory control, and dynamic adaptation.

# Initial Cases

1. **Classic Start**: Both snakes start at opposite edges (length=2), first food at center.
2. **First Food Eaten; P2 at (26,13)**: P1 has eaten first food, head at (25,12) length=3; P2 head at (26,13) length=2; next food spawned randomly.
3. **First Food Eaten; P2 at (27,14)**: P1 as above; P2 head at (27,14) length=2; next food spawned randomly.
4. **First Food Eaten; P2 at (27,12)**: P1 as above; P2 head at (27,12) length=2; next food spawned randomly.
