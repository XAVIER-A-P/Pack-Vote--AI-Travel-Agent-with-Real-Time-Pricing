from collections import Counter

def calculate_ranked_choice_winner(ballots: list[list[str]]) -> dict:
    """
    ballots: List of lists, e.g., [['Paris', 'Tokyo'], ['Tokyo', 'Paris'], ['London']]
    Returns: {'winner': str, 'rounds': list}
    """
    rounds_log = []
    
    while True:
        # Count first choices
        first_choices = [b[0] for b in ballots if b]
        if not first_choices:
            return {"winner": None, "rounds": rounds_log}
            
        counts = Counter(first_choices)
        total_votes = len(ballots)
        rounds_log.append(dict(counts))

        # Check for winner (> 50%)
        for candidate, votes in counts.items():
            if votes > total_votes / 2:
                return {"winner": candidate, "rounds": rounds_log}

        # Eliminate lowest
        min_votes = min(counts.values())
        losers = [c for c, v in counts.items() if v == min_votes]
        
        # Remove losers from all ballots
        new_ballots = []
        for ballot in ballots:
            # Filter out eliminated candidates
            new_ballot = [c for c in ballot if c not in losers]
            if new_ballot:
                new_ballots.append(new_ballot)
        
        ballots = new_ballots
        
        # Safety break for ties
        if not ballots or len(counts) == len(losers):
             return {"winner": list(counts.keys())[0], "rounds": rounds_log} # Tie-breaker