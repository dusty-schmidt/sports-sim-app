"""
Tennis Match Simulation Engine
Enhanced with DK Fantasy Scoring Capabilities
Main simulation logic for the Simulation Service
"""
import random
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json

# Import new DK capabilities
from .simulation.match_simulator import DKMatchSimulator
from .simulation.point_simulator import PointSimulator, PointEvent
from .models.player import Player as DKPlayer
from .models.match_result import DKMatchResult
from .scoring.dk_calculator import DKScoringCalculator

logger = logging.getLogger(__name__)

# Keep original data structures for compatibility
@dataclass
class Player:
    """Player statistics for simulation - Enhanced"""
    name: str
    first_serve_in_pct: float
    ace_rate_per_serve: float
    first_serve_points_won_pct: float
    df_rate_per_serve: float
    second_serve_points_won_pct: float


class PointEventType:
    """Types of point events"""
    ACE = "ACE"
    DOUBLE_FAULT = "DOUBLE_FAULT"
    RALLY_WIN = "RALLY_WIN"
    RALLY_LOSS = "RALLY_LOSS"


class SimulationEngine:
    """
    Enhanced simulation engine with DK capabilities
    Maintains backward compatibility while adding complete DK fantasy functionality
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize enhanced simulation engine
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Initialize DK simulation engines
        self.dk_simulator_bo3 = DKMatchSimulator("BEST_OF_3")
        self.dk_simulator_bo5 = DKMatchSimulator("BEST_OF_5")
        self.point_simulator = PointSimulator()
        
        # Legacy event tracking
        self.event_counts = {
            PointEventType.ACE: 0,
            PointEventType.DOUBLE_FAULT: 0,
            PointEventType.RALLY_WIN: 0,
            PointEventType.RALLY_LOSS: 0
        }
    
    # ==================== NEW DK METHODS ====================
    
    def simulate_dk_match(
        self,
        player1: Player,
        player2: Player,
        match_format: str = "BEST_OF_3",
        walkover: bool = False
    ) -> DKMatchResult:
        """
        NEW: Complete DK match simulation with all 15 scoring events
        
        Args:
            player1: First player
            player2: Second player
            match_format: "BEST_OF_3" or "BEST_OF_5"
            walkover: Whether this is a walkover
            
        Returns:
            DKMatchResult with complete fantasy scoring
        """
        # Convert to DK player format
        dk_player1 = self._convert_to_dk_player(player1)
        dk_player2 = self._convert_to_dk_player(player2)
        
        # Select appropriate simulator
        simulator = (self.dk_simulator_bo3 if match_format == "BEST_OF_3" 
                    else self.dk_simulator_bo5)
        
        # Run DK simulation
        return simulator.simulate_dk_match(dk_player1, dk_player2, walkover)
    
    def get_dk_projection(
        self,
        player1: Player,
        player2: Player,
        match_format: str = "BEST_OF_3",
        num_simulations: int = 1000
    ) -> Dict[str, Any]:
        """
        NEW: Monte Carlo analysis with DK point projections
        
        Args:
            player1: First player
            player2: Second player
            match_format: Match format
            num_simulations: Number of simulations to run
            
        Returns:
            Dictionary with DK projection statistics
        """
        player1_dk_points = []
        player2_dk_points = []
        player1_win_rate = []
        player2_win_rate = []
        
        dk_player1 = self._convert_to_dk_player(player1)
        dk_player2 = self._convert_to_dk_player(player2)
        
        simulator = (self.dk_simulator_bo3 if match_format == "BEST_OF_3" 
                    else self.dk_simulator_bo5)
        
        for _ in range(num_simulations):
            result = simulator.simulate_dk_match(dk_player1, dk_player2)
            player1_dk_points.append(result.player1_dk_points)
            player2_dk_points.append(result.player2_dk_points)
            player1_win_rate.append(1.0 if result.winner == player1.name else 0.0)
            player2_win_rate.append(1.0 if result.winner == player2.name else 0.0)
        
        return {
            "player1_name": player1.name,
            "player2_name": player2.name,
            "match_format": match_format,
            "player1_avg_dk_points": np.mean(player1_dk_points),
            "player1_dk_std": np.std(player1_dk_points),
            "player2_avg_dk_points": np.mean(player2_dk_points),
            "player2_dk_std": np.std(player2_dk_points),
            "player1_win_rate": np.mean(player1_win_rate),
            "player2_win_rate": np.mean(player2_win_rate),
            "total_simulations": num_simulations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ==================== LEGACY COMPATIBILITY METHODS ====================
    
    def simulate_point(self, server: Player, returner: Player) -> Tuple[str, PointEventType]:
        """
        Simulate a single tennis point - Enhanced
        
        Args:
            server: Player serving
            returner: Player returning
            
        Returns:
            Tuple of (winner_name, event_type)
        """
        # Reset event counts
        self.event_counts = {k: 0 for k in self.event_counts.keys()}
        
        # First serve attempt
        if random.random() < server.first_serve_in_pct:
            # First serve in
            if random.random() < server.ace_rate_per_serve:
                # Ace
                self.event_counts[PointEventType.ACE] += 1
                return server.name, PointEventType.ACE
            elif random.random() < server.first_serve_points_won_pct:
                # Server wins point on first serve
                self.event_counts[PointEventType.RALLY_WIN] += 1
                return server.name, PointEventType.RALLY_WIN
            else:
                # Returner wins on first serve
                self.event_counts[PointEventType.RALLY_LOSS] += 1
                return returner.name, PointEventType.RALLY_LOSS
        else:
            # First serve fault - second serve
            if random.random() < server.df_rate_per_serve:
                # Double fault
                self.event_counts[PointEventType.DOUBLE_FAULT] += 1
                return returner.name, PointEventType.DOUBLE_FAULT
            elif random.random() < server.second_serve_points_won_pct:
                # Server wins point on second serve
                self.event_counts[PointEventType.RALLY_WIN] += 1
                return server.name, PointEventType.RALLY_WIN
            else:
                # Returner wins on second serve
                self.event_counts[PointEventType.RALLY_LOSS] += 1
                return returner.name, PointEventType.RALLY_LOSS
    
    def simulate_match(
        self,
        player1: Player,
        player2: Player,
        num_games: int = 12,
        points_per_game: int = 4,
        use_dk_scoring: bool = False
    ) -> Dict[str, Any]:
        """
        Simulate a match - Enhanced with DK support
        
        Args:
            player1: First player
            player2: Second player
            num_games: Number of games to simulate (legacy parameter)
            points_per_game: Points needed to win a game
            use_dk_scoring: Whether to use DK fantasy scoring
            
        Returns:
            Dictionary with match results
        """
        if use_dk_scoring:
            # Use new DK simulation
            match_format = "BEST_OF_3" if num_games <= 12 else "BEST_OF_5"
            dk_result = self.simulate_dk_match(player1, player2, match_format)
            return self._convert_dk_to_legacy_format(dk_result, num_games)
        else:
            # Use legacy simulation
            return self._simulate_legacy_match(player1, player2, num_games, points_per_game)
    
    def _simulate_legacy_match(
        self,
        player1: Player,
        player2: Player,
        num_games: int,
        points_per_game: int = 4
    ) -> Dict[str, Any]:
        """Legacy match simulation for backward compatibility"""
        player1_games_won = 0
        player2_games_won = 0
        game_details = []
        
        for game_num in range(num_games):
            # Alternate server (player1 serves first)
            if game_num % 2 == 0:
                server = player1
                returner = player2
            else:
                server = player2
                returner = player1
            
            # Simulate the game
            game_winner = self._simulate_game(server, returner, points_per_game)
            
            if game_winner == player1.name:
                player1_games_won += 1
            else:
                player2_games_won += 1
            
            game_details.append({
                "game_number": game_num + 1,
                "server": server.name,
                "winner": game_winner
            })
        
        # Calculate percentages
        player1_win_pct = (player1_games_won / num_games) * 100
        player2_win_pct = (player2_games_won / num_games) * 100
        
        return {
            "player1_name": player1.name,
            "player2_name": player2.name,
            "total_games": num_games,
            "player1_games_won": player1_games_won,
            "player2_games_won": player2_games_won,
            "player1_win_pct": round(player1_win_pct, 2),
            "player2_win_pct": round(player2_win_pct, 2),
            "game_details": game_details,
            "event_breakdown": {"games_simulated": num_games, "points_per_game": points_per_game},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _simulate_game(self, server: Player, returner: Player, points_per_game: int = 4) -> str:
        """Simulate a single service game"""
        server_points = 0
        returner_points = 0
        
        while server_points < points_per_game and returner_points < points_per_game:
            winner, _ = self.simulate_point(server, returner)
            if winner == server.name:
                server_points += 1
            else:
                returner_points += 1
        
        return server.name if server_points > returner_points else returner.name
    
    def generate_projections(
        self,
        player1: Player,
        player2: Player,
        num_runs: int = 1000,
        use_dk_scoring: bool = False
    ) -> Dict[str, Any]:
        """
        Generate player projections - Enhanced with DK support
        
        Args:
            player1: First player
            player2: Second player
            num_runs: Number of simulation runs
            use_dk_scoring: Whether to include DK projections
            
        Returns:
            Dictionary with projection statistics
        """
        if use_dk_scoring:
            return self.get_dk_projection(player1, player2, "BEST_OF_3", num_runs)
        else:
            # Legacy Monte Carlo analysis
            player1_results = []
            player2_results = []
            
            event_counts = {
                PointEventType.ACE: {"player1": 0, "player2": 0},
                PointEventType.DOUBLE_FAULT: {"player1": 0, "player2": 0},
                PointEventType.RALLY_WIN: {"player1": 0, "player2": 0},
                PointEventType.RALLY_LOSS: {"player1": 0, "player2": 0}
            }
            
            for i in range(num_runs):
                # Simulate point with player1 serving
                winner1, event1 = self.simulate_point(player1, player2)
                
                if winner1 == player1.name:
                    player1_results.append(1)
                else:
                    player1_results.append(0)
                
                event_counts[event1]["player1" if winner1 == player1.name else "player2"] += 1
                
                # Simulate point with player2 serving
                winner2, event2 = self.simulate_point(player2, player1)
                
                if winner2 == player2.name:
                    player2_results.append(1)
                else:
                    player2_results.append(0)
                
                event_counts[event2]["player2" if winner2 == player2.name else "player1"] += 1
            
            # Calculate statistics
            player1_stats = {
                "points_won": np.mean(player1_results),
                "std": np.std(player1_results),
                "min": np.min(player1_results),
                "max": np.max(player1_results),
                "aces": event_counts[PointEventType.ACE]["player1"] / (num_runs * 2),
                "double_faults": event_counts[PointEventType.DOUBLE_FAULT]["player1"] / (num_runs * 2),
                "rally_wins": event_counts[PointEventType.RALLY_WIN]["player1"] / (num_runs * 2)
            }
            
            player2_stats = {
                "points_won": np.mean(player2_results),
                "std": np.std(player2_results),
                "min": np.min(player2_results),
                "max": np.max(player2_results),
                "aces": event_counts[PointEventType.ACE]["player2"] / (num_runs * 2),
                "double_faults": event_counts[PointEventType.DOUBLE_FAULT]["player2"] / (num_runs * 2),
                "rally_wins": event_counts[PointEventType.RALLY_WIN]["player2"] / (num_runs * 2)
            }
            
            return {
                "player1_stats": player1_stats,
                "player2_stats": player2_stats,
                "total_simulations": num_runs,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def simulate_points(
        self,
        player1: Player,
        player2: Player,
        num_points: int
    ) -> Dict[str, Any]:
        """Simulate multiple points for statistical analysis"""
        player1_wins = 0
        player2_wins = 0
        
        event_counts = {
            PointEventType.ACE: 0,
            PointEventType.DOUBLE_FAULT: 0,
            PointEventType.RALLY_WIN: 0,
            PointEventType.RALLY_LOSS: 0
        }
        
        point_details = []
        
        for i in range(num_points):
            winner, event = self.simulate_point(player1, player2)
            
            if winner == player1.name:
                player1_wins += 1
            else:
                player2_wins += 1
            
            event_counts[event] += 1
            
            point_details.append({
                "point_number": i + 1,
                "winner": winner,
                "event": event
            })
        
        # Calculate percentages
        player1_win_pct = (player1_wins / num_points) * 100
        player2_win_pct = (player2_wins / num_points) * 100
        
        return {
            "player1_name": player1.name,
            "player2_name": player2.name,
            "total_points": num_points,
            "player1_wins": player1_wins,
            "player2_wins": player2_wins,
            "player1_win_pct": round(player1_win_pct, 2),
            "player2_win_pct": round(player2_win_pct, 2),
            "event_breakdown": event_counts,
            "point_details": point_details,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ==================== UTILITY METHODS ====================
    
    def _convert_to_dk_player(self, player: Player) -> DKPlayer:
        """Convert legacy Player to DK Player format"""
        return DKPlayer(
            name=player.name,
            first_serve_in_pct=player.first_serve_in_pct,
            ace_rate_per_serve=player.ace_rate_per_serve,
            first_serve_points_won_pct=player.first_serve_points_won_pct,
            df_rate_per_serve=player.df_rate_per_serve,
            second_serve_points_won_pct=player.second_serve_points_won_pct
        )
    
    def _convert_dk_to_legacy_format(self, dk_result: DKMatchResult, num_games: int) -> Dict[str, Any]:
        """Convert DK result to legacy format for backward compatibility"""
        return {
            "player1_name": dk_result.player1_name,
            "player2_name": dk_result.player2_name,
            "total_games": dk_result.player1_games_won + dk_result.player1_games_lost,
            "player1_games_won": dk_result.player1_games_won,
            "player2_games_won": dk_result.player2_games_won,
            "player1_win_pct": (dk_result.player1_games_won / 
                               (dk_result.player1_games_won + dk_result.player1_games_lost)) * 100,
            "player2_win_pct": (dk_result.player2_games_won / 
                               (dk_result.player2_games_won + dk_result.player2_games_lost)) * 100,
            # NEW DK fields
            "player1_dk_points": dk_result.player1_dk_points,
            "player2_dk_points": dk_result.player2_dk_points,
            "player1_aces": dk_result.player1_aces,
            "player2_aces": dk_result.player2_aces,
            "player1_double_faults": dk_result.player1_double_faults,
            "player2_double_faults": dk_result.player2_double_faults,
            "player1_breaks": dk_result.player1_breaks,
            "player2_breaks": dk_result.player2_breaks,
            "player1_sets_won": dk_result.player1_sets_won,
            "player2_sets_won": dk_result.player2_sets_won,
            "match_winner": dk_result.winner,
            "total_sets_played": dk_result.total_sets_played,
            "dk_format": dk_result.match_format,
            "game_details": [],  # Not tracked in legacy format
            "event_breakdown": {"dk_format": dk_result.match_format, "sets_played": dk_result.total_sets_played},
            "timestamp": datetime.utcnow().isoformat()
        }