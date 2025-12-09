# app/core/simulation/simulation/set_simulator.py
from .game_simulator import GameSimulator
from ..models.player import Player

class SetSimulator:
    def __init__(self, game_simulator: GameSimulator):
        self.game_simulator = game_simulator
    
    def simulate_set(self, player1: Player, player2: Player, 
                    set_number: int, server: str) -> dict:
        """Simulate a single set (first to 6 games)"""
        player1_games = 0
        player2_games = 0
        game_details = []
        current_server = server
        
        # Play games until one player wins 6 games (with 2-game lead)
        while True:
            # Tiebreak condition
            if player1_games == 6 and player2_games == 6:
                # Play tiebreak as a single game
                winner = self._simulate_tiebreak(current_server, player1, player2)
                if winner == player1.name:
                    player1_games += 1
                else:
                    player2_games += 1
                game_details.append({
                    "game_number": len(game_details) + 1,
                    "server": current_server,
                    "winner": winner,
                    "score": f"{player1_games}-{player2_games}",
                    "break_occurred": False
                })
                break
                
            # Normal game
            server_player = player1 if current_server == player1.name else player2
            returner_player = player2 if current_server == player1.name else player1
            
            # Simulate game
            game_result = self.game_simulator.simulate_game(server_player, returner_player)
            
            # Update game count
            if game_result["winner"] == player1.name:
                player1_games += 1
            else:
                player2_games += 1
            
            # Store game details
            game_details.append({
                "game_number": len(game_details) + 1,
                "server": current_server,
                "winner": game_result["winner"],
                "score": f"{player1_games}-{player2_games}",
                "break_occurred": game_result["break_occurred"]
            })
            
            # Switch server for next game
            current_server = player2.name if current_server == player1.name else player1.name
            
            # Win condition for set
            if (player1_games >= 6 or player2_games >= 6) and abs(player1_games - player2_games) >= 2:
                break
        
        # Determine set winner
        set_winner = player1.name if player1_games > player2_games else player2.name
        
        # Check if this was a clean set (won without losing significant games)
        clean_set = self._check_clean_set(set_winner, player1_games, player2_games, player1.name, player2.name)
        
        return {
            "set_winner": set_winner,
            "set_score": f"{player1_games}-{player2_games}",
            "player1_games": player1_games,
            "player2_games": player2_games,
            "game_details": game_details,
            "clean_set": clean_set,
            "set_number": set_number,
            "total_games": len(game_details)
        }
    
    def _simulate_tiebreak(self, server_name: str, player1: Player, player2: Player) -> str:
        """Simulate single tiebreak point (simplified)"""
        server_player = player1 if server_name == player1.name else player2
        returner_player = player2 if server_name == player1.name else player1
        
        # Simulate tiebreak as a single point (simplified)
        winner, _ = self.game_simulator.point_simulator.simulate_point(server_player, returner_player)
        return winner
    
    def _check_clean_set(self, winner: str, player1_games: int, player2_games: int, player1_name: str, player2_name: str) -> bool:
        """Check if set was won without losing many games (clean set)"""
        return (winner == player1_name and player2_games <= 3) or (winner == player2_name and player1_games <= 3)
