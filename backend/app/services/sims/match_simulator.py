# app/core/simulation/simulation/match_simulator.py
from datetime import datetime, timezone, UTC
from typing import Dict

from .point_simulator import PointSimulator
from .game_simulator import GameSimulator
from .set_simulator import SetSimulator
from ..scoring.dk_calculator import DKScoringCalculator
from ..models.match_result import DKMatchResult
from ..models.player import Player

class DKMatchSimulator:
    def __init__(self, match_format: str = "BEST_OF_3"):
        self.match_format = match_format
        self.point_simulator = PointSimulator()
        self.game_simulator = GameSimulator(self.point_simulator)
        self.set_simulator = SetSimulator(self.game_simulator)
        self.dk_calculator = DKScoringCalculator(match_format)
    
    def simulate_dk_match(self, player1: Player, player2: Player, walkover: bool = False) -> DKMatchResult:
        """Simulate complete DK tennis match"""
        
        if walkover:
            return self._handle_walkover(player1, player2)
        
        # Reset point history for clean statistics per match
        self.point_simulator.point_history = []
        
        # Initialize match tracking
        sets_played = 0
        match_winner = None
        player1_stats = self._initialize_player_stats(player1.name)
        player2_stats = self._initialize_player_stats(player2.name)
        
        # Determine sets needed to win
        sets_to_win = 2 if self.match_format == "BEST_OF_3" else 3
        current_server = player1.name  # Player 1 serves first
        
        # Play sets
        while True:
            set_result = self.set_simulator.simulate_set(
                player1, player2, sets_played + 1, current_server
            )
            
            sets_played += 1
            
            # Update player statistics
            if set_result["set_winner"] == player1.name:
                player1_stats["sets_won"] += 1
                player2_stats["sets_lost"] += 1
                current_server = player2.name  # Loser serves first next set
            else:
                player2_stats["sets_won"] += 1
                player1_stats["sets_lost"] += 1
                current_server = player1.name  # Loser serves first next set
            
            # Update game statistics
            self._update_game_stats(player1_stats, player2_stats, set_result)
            
            # Check for clean set bonus
            if set_result["clean_set"]:
                winner_player = player1 if set_result["set_winner"] == player1.name else player2
                winner_stats = player1_stats if set_result["set_winner"] == player1.name else player2_stats
                winner_stats["clean_sets"] = winner_stats.get("clean_sets", 0) + 1
            
            # Check if match is over
            if (player1_stats["sets_won"] == sets_to_win or 
                player2_stats["sets_won"] == sets_to_win):
                match_winner = player1.name if player1_stats["sets_won"] == sets_to_win else player2.name
                break
        
        # Final flags
        player1_stats["match_played"] = True
        player2_stats["match_played"] = True
        player1_stats["match_won"] = (match_winner == player1.name)
        player2_stats["match_won"] = (match_winner == player2.name)
        
        # Check for straight sets win
        total_sets_lost = min(player1_stats["sets_lost"], player2_stats["sets_lost"])
        if total_sets_lost == 0:
            if player1_stats["sets_won"] == sets_to_win:
                player1_stats["straight_sets_win"] = True
            else:
                player2_stats["straight_sets_win"] = True
        
        # Calculate DK points
        player1_dk_points = self.dk_calculator.calculate_player_points(player1_stats)
        player2_dk_points = self.dk_calculator.calculate_player_points(player2_stats)
        
        # Build events from point history
        events = self.point_simulator.point_history
        
        return DKMatchResult(
            player1_name=player1.name,
            player2_name=player2.name,
            match_format=self.match_format,
            match_played=True,
            walkover=False,
            player1_dk_points=player1_dk_points,
            player2_dk_points=player2_dk_points,
            player1_events=events,
            player2_events=events,
            player1_aces=player1_stats["aces"],
            player1_double_faults=player1_stats["double_faults"],
            player1_breaks=player1_stats["breaks"],
            player1_games_won=player1_stats["games_won"],
            player1_games_lost=player1_stats["games_lost"],
            player1_sets_won=player1_stats["sets_won"],
            player1_sets_lost=player1_stats["sets_lost"],
            player2_aces=player2_stats["aces"],
            player2_double_faults=player2_stats["double_faults"],
            player2_breaks=player2_stats["breaks"],
            player2_games_won=player2_stats["games_won"],
            player2_games_lost=player2_stats["games_lost"],
            player2_sets_won=player2_stats["sets_won"],
            player2_sets_lost=player2_stats["sets_lost"],
            winner=match_winner,
            total_sets_played=sets_played,
            match_duration_estimate=0,  # Placeholder for future implementation
            timestamp=datetime.now(UTC)
        )
    
    def _initialize_player_stats(self, player_name: str) -> Dict:
        """Initialize player statistics for match"""
        return {
            "player_name": player_name,
            "aces": 0,
            "double_faults": 0,
            "breaks": 0,
            "games_won": 0,
            "games_lost": 0,
            "sets_won": 0,
            "sets_lost": 0,
            "clean_sets": 0,
            "straight_sets_win": False,
            "match_played": False,
            "match_won": False,
            "walkover": False,
            "no_double_faults": True,
            "clean_sets": 0
        }
    
    def _update_game_stats(self, p1_stats: Dict, p2_stats: Dict, set_result: Dict):
        """Update player statistics with set results"""
        # Add game wins/losses
        if set_result["player1_games"] > set_result["player2_games"]:
            p1_stats["games_won"] += set_result["player1_games"]
            p2_stats["games_lost"] += set_result["player2_games"]
        else:
            p2_stats["games_won"] += set_result["player2_games"]
            p1_stats["games_lost"] += set_result["player1_games"]
        
        # Count breaks from game_details
        for game_detail in set_result["game_details"]:
            if game_detail["break_occurred"]:
                if game_detail["winner"] == p1_stats["player_name"]:
                    p1_stats["breaks"] += 1
                else:
                    p2_stats["breaks"] += 1
        
        # Count aces and double faults from point history
        for point in self.point_simulator.point_history:
            if point["type"] == "ACE":
                if point["player"] == p1_stats["player_name"]:
                    p1_stats["aces"] += 1
                else:
                    p2_stats["aces"] += 1
            elif point["type"] == "DOUBLE_FAULT":
                if point["player"] == p1_stats["player_name"]:
                    p1_stats["double_faults"] += 1
                    p1_stats["no_double_faults"] = False
                else:
                    p2_stats["double_faults"] += 1
                    p2_stats["no_double_faults"] = False
    
    def _handle_walkover(self, player1: Player, player2: Player) -> DKMatchResult:
        """Handle walkover scenario"""
        walkover_points = self.dk_calculator.scoring_config["WALKOVER"]
        return DKMatchResult(
            player1_name=player1.name,
            player2_name=player2.name,
            match_format=self.match_format,
            match_played=True,
            walkover=True,
            player1_dk_points=walkover_points,
            player2_dk_points=walkover_points,
            player1_events=[],
            player2_events=[],
            player1_aces=0,
            player2_aces=0,
            player1_double_faults=0,
            player2_double_faults=0,
            player1_breaks=0,
            player2_breaks=0,
            player1_games_won=0,
            player2_games_won=0,
            player1_games_lost=0,
            player2_games_lost=0,
            player1_sets_won=0,
            player2_sets_won=0,
            player1_sets_lost=0,
            player2_sets_lost=0,
            winner="",
            total_sets_played=0,
            match_duration_estimate=0,
            timestamp=datetime.now(UTC)
        )
