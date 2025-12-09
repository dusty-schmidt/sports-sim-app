from fastapi import APIRouter, HTTPException
from app.models.simulation import SimulationRequest, SimulationResponse
from app.services.data import PLAYERS_DB
from app.services.sim_engine import TennisMatchSimulator, PlayerProfile
from app.services.fantasy_scoring import calculate_fantasy_points

router = APIRouter(prefix="/simulation", tags=["simulation"])

@router.post("/ad-hoc", response_model=SimulationResponse)
def run_ad_hoc_simulation(request: SimulationRequest):
    """
    Run an ad-hoc simulation between two players without saving to DB.
    """
    # 1. Fetch Request Data
    p1_profile = PLAYERS_DB.get(request.player1_name)
    p2_profile = PLAYERS_DB.get(request.player2_name)
    
    if not p1_profile:
        raise HTTPException(status_code=404, detail=f"Player {request.player1_name} not found in DB")
    if not p2_profile:
        raise HTTPException(status_code=404, detail=f"Player {request.player2_name} not found in DB")
        
    # 2. Setup Profiles
    p1_stats = p1_profile["stats"].get(request.surface, p1_profile["stats"]["hard"])
    p2_stats = p2_profile["stats"].get(request.surface, p2_profile["stats"]["hard"])
    
    p1_obj = PlayerProfile(
        name=p1_profile["name"],
        serve_1_in_pct=p1_stats["serve_1_in"],
        serve_1_won_pct=p1_stats["serve_1_won"],
        serve_2_won_pct=p1_stats["serve_2_won"],
        ace_pct=p1_stats["ace_rate"],
        df_pct=p1_stats["df_rate"],
        return_won_pct=p1_stats["return_won"]
    )
    
    p2_obj = PlayerProfile(
        name=p2_profile["name"],
        serve_1_in_pct=p2_stats["serve_1_in"],
        serve_1_won_pct=p2_stats["serve_1_won"],
        serve_2_won_pct=p2_stats["serve_2_won"],
        ace_pct=p2_stats["ace_rate"],
        df_pct=p2_stats["df_rate"],
        return_won_pct=p2_stats["return_won"]
    )
    
    # 3. Run Simulation
    sim = TennisMatchSimulator(p1_obj, p2_obj, sets_to_win=request.sets_to_win)
    results = sim.run(n_sims=request.n_sims)
    
    # 4. Aggregation & Scoring
    p1_wins = 0
    p1_fp_list = []
    p2_fp_list = []
    p1_aces = 0
    p1_dfs = 0
    p2_aces = 0
    p2_dfs = 0
    
    for res in results:
        if res.winner == p1_obj.name:
            p1_wins += 1
            
        fp1 = calculate_fantasy_points(res.p1_stats, request.ruleset)
        fp2 = calculate_fantasy_points(res.p2_stats, request.ruleset)
        
        p1_fp_list.append(fp1)
        p2_fp_list.append(fp2)
        
        p1_aces += res.p1_stats["aces"]
        p1_dfs += res.p1_stats["dfs"]
        p2_aces += res.p2_stats["aces"]
        p2_dfs += res.p2_stats["dfs"]
        
    n = request.n_sims
    return SimulationResponse(
        p1_name=p1_obj.name,
        p2_name=p2_obj.name,
        surface=request.surface,
        simulations=n,
        p1_win_pct=p1_wins / n,
        p1_avg_fantasy_points=sum(p1_fp_list) / n,
        p1_avg_aces=p1_aces / n,
        p1_avg_dfs=p1_dfs / n,
        p2_avg_fantasy_points=sum(p2_fp_list) / n,
        p2_avg_aces=p2_aces / n,
        p2_avg_dfs=p2_dfs / n
    )
