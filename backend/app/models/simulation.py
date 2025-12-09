from pydantic import BaseModel
from typing import Dict, Any, Optional

class SimulationRequest(BaseModel):
    player1_name: str
    player2_name: str
    surface: str = "Hard"
    n_sims: int = 1000
    sets_to_win: int = 2
    ruleset: str = "best_of_3"

class SimulationResponse(BaseModel):
    p1_name: str
    p2_name: str
    surface: str
    simulations: int
    
    p1_win_pct: float
    p1_avg_fantasy_points: float
    p1_avg_aces: float
    p1_avg_dfs: float
    
    p2_avg_fantasy_points: float
    p2_avg_aces: float
    p2_avg_dfs: float
