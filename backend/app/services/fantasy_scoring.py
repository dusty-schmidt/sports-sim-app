from typing import Dict, Any

def calculate_fantasy_points(stats: Dict[str, Any], ruleset: str = "best_of_3") -> float:
    """
    Calculates DraftKings fantasy points based on match stats.
    
    stats input format:
    {
        "match_win": 0/1,
        "sets": int,
        "games": int,
        "aces": int,
        "dfs": int
    }
    """
    # Tuning based on DRAFTKINGS-SCORING.xml
    SCORING = {
        "best_of_3": {
            "match_played": 30,
            "match_won": 6,
            "set_won": 6,
            "game_won": 2.5,
            "game_lost": -2.0,
            "ace": 0.4,
            "double_fault": -1.0,
            "bonus_no_df": 2.5,
            "bonus_10_aces": 2.0
        },
        # Simplified for now, can expand later
    }
    
    rules = SCORING.get(ruleset, SCORING["best_of_3"])
    
    fp = 0.0
    fp += rules["match_played"]
    
    if stats["match_win"]:
        fp += rules["match_won"]
        
    fp += stats["sets"] * rules["set_won"]
    fp += stats["games"] * rules["game_won"]
    fp += stats["aces"] * rules["ace"]
    fp += stats["dfs"] * rules["double_fault"]
    
    # Bonuses
    if stats["dfs"] == 0:
        fp += rules["bonus_no_df"]
    
    if stats["aces"] >= 10:
        fp += rules["bonus_10_aces"]
        
    return fp
