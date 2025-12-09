import pytest
from app.services.sim_engine import TennisMatchSimulator, PlayerProfile, MatchStats
from app.services.fantasy_scoring import calculate_fantasy_points

# Mock Player Profiles
P1_PROFILE = PlayerProfile(
    name="Strong Server",
    serve_1_in_pct=0.70,
    serve_1_won_pct=0.80,
    serve_2_won_pct=0.60,
    ace_pct=0.10,   # High ace rate
    df_pct=0.02,
    return_won_pct=0.30
)

P2_PROFILE = PlayerProfile(
    name="Weak Server",
    serve_1_in_pct=0.50,
    serve_1_won_pct=0.50,
    serve_2_won_pct=0.40,
    ace_pct=0.01,
    df_pct=0.10,    # High double fault rate
    return_won_pct=0.20
)

def test_initialization():
    sim = TennisMatchSimulator(P1_PROFILE, P2_PROFILE, sets_to_win=2)
    assert sim.p1.name == "Strong Server"
    assert sim.sets_to_win == 2
    assert "Strong Server" in sim.stats

def test_conditional_probs():
    sim = TennisMatchSimulator(P1_PROFILE, P2_PROFILE)
    
    # 1. Check Ace Probability Normalization
    # ace_prob_if_in = ace_pct / serve_1_in_pct
    # 0.10 / 0.70 = 0.142857
    ace_prob, df_prob = sim._get_conditional_probs(P1_PROFILE)
    assert abs(ace_prob - (0.10 / 0.70)) < 0.0001
    
    # 2. Check DF Probability Normalization
    # df_prob_if_2nd = df_pct / (1 - serve_1_in_pct)
    # 0.02 / 0.30 = 0.06666
    assert abs(df_prob - (0.02 / 0.30)) < 0.0001

def test_simulate_point_returns_valid_outcome():
    sim = TennisMatchSimulator(P1_PROFILE, P2_PROFILE)
    outcomes = set()
    for _ in range(100):
        res = sim.simulate_point(P1_PROFILE, P2_PROFILE)
        outcomes.add(res)
        assert res in ["ace", "df", "server_win", "returner_win"]
    
    # We expect at least some aces and normal wins
    assert "ace" in outcomes or "server_win" in outcomes

def test_ace_tracking():
    # Force high ace rate to verify tracking
    ace_bot = PlayerProfile("AceBot", 1.0, 1.0, 0.5, 0.99, 0.0, 0.0)
    dummy = PlayerProfile("Dummy", 0.5, 0.5, 0.5, 0.0, 0.0, 0.0)
    
    sim = TennisMatchSimulator(ace_bot, dummy)
    
    # Run 100 points
    for _ in range(100):
        sim.simulate_point(ace_bot, dummy)
        
    # Should have ~99 aces in stats
    assert sim.stats["AceBot"]["aces"] > 90

def test_df_tracking():
    # Force high DF rate
    df_bot = PlayerProfile("DFBot", 0.0, 0.5, 0.5, 0.0, 0.99, 0.0)
    dummy = PlayerProfile("Dummy", 0.5, 0.5, 0.5, 0.0, 0.0, 0.0)
    
    sim = TennisMatchSimulator(df_bot, dummy)
    
    for _ in range(100):
        sim.simulate_point(df_bot, dummy)
        
    assert sim.stats["DFBot"]["dfs"] > 90

def test_game_simulation():
    sim = TennisMatchSimulator(P1_PROFILE, P2_PROFILE)
    winner = sim.simulate_game(server_idx=0) # P1 serves
    assert winner in [0, 1]
    
    p1_games = sim.stats[P1_PROFILE.name]["games"]
    p2_games = sim.stats[P2_PROFILE.name]["games"]
    assert p1_games + p2_games >= 1

def test_run_returns_list_of_stats():
    sim = TennisMatchSimulator(P1_PROFILE, P2_PROFILE)
    results = sim.run(n_sims=50)
    
    assert isinstance(results, list)
    assert len(results) == 50
    assert isinstance(results[0], MatchStats)
    
    # Check structure of a result
    res = results[0]
    assert res.winner in [P1_PROFILE.name, P2_PROFILE.name]
    assert "aces" in res.p1_stats
    assert "fantasy_points" not in res.p1_stats # Raw stats only

def test_calculate_fantasy_points():
    # Case 1: Simple win
    stats = {
        "aces": 5,
        "dfs": 1,
        "games": 12,
        "sets": 2,
        "match_win": 1
    }
    # Expected: 79.0
    points = calculate_fantasy_points(stats, ruleset="best_of_3")
    assert abs(points - 79.0) < 0.001
    
    # Case 2: Bonus check
    stats_bonus = {
        "aces": 10,
        "dfs": 0,
        "games": 12,
        "sets": 2,
        "match_win": 1
    }
    # Expected: 86.5
    points_bonus = calculate_fantasy_points(stats_bonus, ruleset="best_of_3")
    assert abs(points_bonus - 86.5) < 0.001
