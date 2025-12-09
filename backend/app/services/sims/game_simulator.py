# app/core/simulation/simulation/game_simulator.py
from .point_simulator import PointSimulator, PointEvent
from ..models.player import Player

class GameSimulator:
    def __init__(self, point_simulator: PointSimulator):
        self.point_simulator = point_simulator
    
    def simulate_game(self, server: Player, returner: Player, game_score: dict = None) -> dict:
        """Simulate a single service game"""
        if game_score is None:
            game_score = {"server": 0, "returner": 0}
        
        server_points = game_score["server"]
        returner_points = game_score["returner"]
        
        # Game continues until one player reaches 4 points with 2-point lead
        while True:
            # Win condition: 4+ pts with 2-pt lead
            if (server_points >= 4 or returner_points >= 4) and abs(server_points - returner_points) >= 2:
                break
                
            # Simulate next point
            winner, event = self.point_simulator.simulate_point(server, returner)
            
            # Update game score
            if winner == server.name:
                server_points += 1
            else:
                returner_points += 1
                
            # Check for break point (returner has advantage)
            # Break detection logic: if returner has advantage and wins the point
            # This is simplified - in reality, break points are at specific scores
                
        # Determine game winner
        game_winner = server.name if server_points > returner_points else returner.name
        
        return {
            "winner": game_winner,
            "server_points": server_points,
            "returner_points": returner_points,
            "break_occurred": self._check_break_occurred(server_points, returner_points)
        }
    
    def _check_break_occurred(self, server_points: int, returner_points: int) -> bool:
        """Check if serve was broken in this game"""
        return returner_points > server_points and returner_points >= 4
