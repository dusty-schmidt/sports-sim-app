import random
from dataclasses import dataclass
from typing import Tuple, Dict, Any, List

@dataclass
class PlayerProfile:
    name: str
    serve_1_in_pct: float      # "1st%"
    serve_1_won_pct: float     # "1st W%" (Points won when 1st serve is IN)
    serve_2_won_pct: float     # "2nd W%" (Points won when 2nd serve is IN)
    ace_pct: float             # "Ace%" (Aces per total service points)
    df_pct: float              # "DF%" (Double faults per total service points)
    return_won_pct: float = 0.30 # Return points won (for opponent adjustment)

@dataclass
class MatchStats:
    winner: str
    p1_stats: Dict[str, int]
    p2_stats: Dict[str, int]

class TennisMatchSimulator:
    def __init__(self, p1: PlayerProfile, p2: PlayerProfile, sets_to_win=2):
        self.p1 = p1
        self.p2 = p2
        self.sets_to_win = sets_to_win
        
        # Reset per match
        self.stats = {
            p1.name: {"aces": 0, "dfs": 0, "games": 0, "sets": 0, "match_win": 0},
            p2.name: {"aces": 0, "dfs": 0, "games": 0, "sets": 0, "match_win": 0}
        }
    
    def _get_conditional_probs(self, server: PlayerProfile) -> Tuple[float, float]:
        """
        Converts raw Tennis Abstract stats into conditional simulation probabilities.
        """
        # 1. Probability of Ace GIVEN 1st serve is in
        # (Assuming nearly all aces happen on 1st serve for simplicity)
        # Avoid division by zero
        if server.serve_1_in_pct > 0:
            prob_ace_if_in = server.ace_pct / server.serve_1_in_pct
        else:
            prob_ace_if_in = 0.0

        # 2. Probability of DF GIVEN 1st serve was a fault
        # Denominator is the % of points that go to a 2nd serve
        first_serve_fault_pct = 1.0 - server.serve_1_in_pct
        if first_serve_fault_pct > 0:
            prob_df_if_2nd = server.df_pct / first_serve_fault_pct
        else:
            prob_df_if_2nd = 0.0

        return prob_ace_if_in, prob_df_if_2nd

    def simulate_point(self, server: PlayerProfile, returner: PlayerProfile) -> str:
        """
        Returns outcome string: 'server_win', 'returner_win', 'ace', 'df'
        Updates stats for aces and double faults.
        """
        ace_prob, df_prob = self._get_conditional_probs(server)
        
        # --- FIRST SERVE ---
        if random.random() < server.serve_1_in_pct:
            # Serve is IN
            if random.random() < ace_prob:
                self.stats[server.name]["aces"] += 1
                return "ace"
            
            # Rally on 1st Serve
            # Adjusted Win % = (Server 1st Won% + (1 - Returner Won%)) / 2
            rally_win_prob = (server.serve_1_won_pct + (1.0 - returner.return_won_pct)) / 2
            
            if random.random() < rally_win_prob:
                return "server_win"
            else:
                return "returner_win"
        
        # --- SECOND SERVE ---
        else:
            # First serve fault. Check for Double Fault.
            if random.random() < df_prob:
                self.stats[server.name]["dfs"] += 1
                return "df"
            
            # Rally on 2nd Serve
            # Adjusted Win % = (Server 2nd Won% + (1 - Returner Won%)) / 2
            rally_win_prob = (server.serve_2_won_pct + (1.0 - returner.return_won_pct)) / 2
            
            if random.random() < rally_win_prob:
                return "server_win"
            else:
                return "returner_win"

    def simulate_game(self, server_idx: int) -> int:
        """
        Simulates a standard game.
        server_idx: 0 for p1, 1 for p2
        Returns: 0 if p1 wins, 1 if p2 wins
        """
        server = self.p1 if server_idx == 0 else self.p2
        returner = self.p2 if server_idx == 0 else self.p1
        
        s_points, r_points = 0, 0
        
        while True:
            result = self.simulate_point(server, returner)
            
            # 'ace' and 'df' mapping to point winner
            if result == "ace" or result == "server_win":
                s_points += 1
            else: # df or returner_win
                r_points += 1
                
            # Win Condition (Standard Game)
            # Must have at least 4 points and be ahead by 2
            if s_points >= 4 and s_points >= r_points + 2:
                self.stats[server.name]["games"] += 1
                return server_idx
            if r_points >= 4 and r_points >= s_points + 2:
                # Returner broke serve
                self.stats[returner.name]["games"] += 1
                return 1 - server_idx

    def simulate_tiebreak(self) -> int:
        """
        Simulates a tiebreak (first to 7, win by 2).
        Returns: 0 if p1 wins, 1 if p2 wins
        """
        p1_points = 0
        p2_points = 0
        
        # Tiebreak rotation: 1st point Server A, then 2 pts Server B, etc.
        # Track total points to determine server
        points_played = 0
        
        while True:
            # Determine current server
            # Pattern: A (0), B(1,2), A(3,4), B(5,6)...
            # Logic: if ((points_played + 1) // 2) % 2 == 0 -> P1 serves (idx 0)
            if ((points_played + 1) // 2) % 2 == 0:
                server_idx = 0
            else:
                server_idx = 1
                
            server = self.p1 if server_idx == 0 else self.p2
            returner = self.p2 if server_idx == 0 else self.p1
            
            result = self.simulate_point(server, returner)
            
            if result == "ace" or result == "server_win":
                if server_idx == 0: p1_points += 1
                else: p2_points += 1
            else: # returner wins point
                if server_idx == 0: p2_points += 1
                else: p1_points += 1
            
            points_played += 1

            if p1_points >= 7 and p1_points >= p2_points + 2:
                self.stats[self.p1.name]["games"] += 1 # TB counts as a game won
                return 0
            if p2_points >= 7 and p2_points >= p1_points + 2:
                self.stats[self.p2.name]["games"] += 1
                return 1

    def simulate_set(self, start_server_idx: int) -> Tuple[int, int]:
        """
        Simulate a set.
        Returns: (winner_idx, next_set_start_server_idx)
        """
        p1_games = 0
        p2_games = 0
        current_server_idx = start_server_idx
        
        while True:
            game_winner = self.simulate_game(current_server_idx)
            
            if game_winner == 0:
                p1_games += 1
            else:
                p2_games += 1
                
            current_server_idx = 1 - current_server_idx # Switch server
            
            # Set Win Conditions
            if p1_games >= 6 and p1_games >= p2_games + 2:
                self.stats[self.p1.name]["sets"] += 1
                return 0, current_server_idx
            if p2_games >= 6 and p2_games >= p1_games + 2:
                self.stats[self.p2.name]["sets"] += 1
                return 1, current_server_idx
            
            # Tiebreak at 6-6
            if p1_games == 6 and p2_games == 6:
                tb_winner = self.simulate_tiebreak()
                if tb_winner == 0:
                    self.stats[self.p1.name]["sets"] += 1
                else:
                    self.stats[self.p2.name]["sets"] += 1
                return tb_winner, current_server_idx

    def simulate_match(self) -> MatchStats:
        """
        Simulates the entire match.
        Returns: MatchStats object with raw results
        """
        p1_sets = 0
        p2_sets = 0
        server_idx = 0 # Assume P1 serves first (randomize in real app if needed)
        
        # Reset stats for the match instance
        self.stats[self.p1.name] = {"aces": 0, "dfs": 0, "games": 0, "sets": 0, "match_win": 0}
        self.stats[self.p2.name] = {"aces": 0, "dfs": 0, "games": 0, "sets": 0, "match_win": 0}

        while p1_sets < self.sets_to_win and p2_sets < self.sets_to_win:
            winner_idx, next_server_idx = self.simulate_set(server_idx)
            if winner_idx == 0:
                p1_sets += 1
            else:
                p2_sets += 1
            server_idx = next_server_idx
            
        match_winner_idx = 0 if p1_sets > p2_sets else 1
        winner_name = self.p1.name if match_winner_idx == 0 else self.p2.name
        self.stats[winner_name]["match_win"] = 1
        
        return MatchStats(
            winner=winner_name,
            p1_stats=self.stats[self.p1.name].copy(),
            p2_stats=self.stats[self.p2.name].copy()
        )

    def run(self, n_sims: int = 1000) -> List[MatchStats]:
        """
        Runs n_sims of the match.
        Returns a list of MatchStats (raw outcomes).
        """
        results = []
        for _ in range(n_sims):
            results.append(self.simulate_match())
        return results
