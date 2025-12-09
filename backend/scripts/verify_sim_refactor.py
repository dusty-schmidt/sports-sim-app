import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.sim_engine import TennisMatchSimulator, PlayerProfile, MatchStats
from app.services.fantasy_scoring import calculate_fantasy_points

def main():
    print("Testing Refactored Sim Engine...")
    
    p1 = PlayerProfile(name="Sinner", serve_1_in_pct=0.65, serve_1_won_pct=0.75, serve_2_won_pct=0.55, ace_pct=0.10, df_pct=0.03, return_won_pct=0.30)
    p2 = PlayerProfile(name="Alcaraz", serve_1_in_pct=0.65, serve_1_won_pct=0.74, serve_2_won_pct=0.54, ace_pct=0.08, df_pct=0.04, return_won_pct=0.30)
    
    sim = TennisMatchSimulator(p1, p2, sets_to_win=2)
    
    # Run 10 Sims
    results = sim.run(n_sims=10)
    
    print(f"Generated {len(results)} raw results.")
    
    fp_list = []
    
    for i, res in enumerate(results):
        fp = calculate_fantasy_points(res.p1_stats)
        fp_list.append(fp)
        if i == 0:
            print(f"Sample Result [0] Winner: {res.winner}")
            print(f"Sample Stats P1: {res.p1_stats}")
            print(f"Sample FP P1: {fp}")
            
    avg_fp = sum(fp_list) / len(fp_list)
    print(f"Average P1 Fantasy Points: {avg_fp}")
    print("Verification Successful!")

if __name__ == "__main__":
    main()
