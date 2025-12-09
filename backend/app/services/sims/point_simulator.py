# app/core/simulation/simulation/point_simulator.py
import random
from enum import Enum
from typing import Dict, Tuple
from ..models.player import Player

class PointEvent(Enum):
    ACE = "ACE"
    DOUBLE_FAULT = "DOUBLE_FAULT"
    RALLY_WIN = "RALLY_WIN"  # Point won after serve
    RALLY_LOSS = "RALLY_LOSS"  # Point lost after serve

class PointSimulator:
    def __init__(self):
        self.point_history = []
    
    def simulate_point(self, server: Player, returner: Player) -> Tuple[str, PointEvent]:
        """Simulate a single tennis point"""
        
        # First serve attempt
        if random.random() < server.first_serve_in_pct:
            # First serve is in
            if random.random() < server.ace_rate_per_serve:
                # Ace
                self._record_event(PointEvent.ACE, server.name)
                return server.name, PointEvent.ACE
            elif random.random() < server.first_serve_points_won_pct:
                # Server wins point on first serve
                self._record_event(PointEvent.RALLY_WIN, server.name)
                return server.name, PointEvent.RALLY_WIN
            else:
                # Returner wins on first serve
                self._record_event(PointEvent.RALLY_LOSS, returner.name)
                return returner.name, PointEvent.RALLY_LOSS
        else:
            # First serve fault - second serve
            if random.random() < server.df_rate_per_serve:
                # Double fault
                self._record_event(PointEvent.DOUBLE_FAULT, server.name)
                return returner.name, PointEvent.DOUBLE_FAULT
            elif random.random() < server.second_serve_points_won_pct:
                # Server wins point on second serve
                self._record_event(PointEvent.RALLY_WIN, server.name)
                return server.name, PointEvent.RALLY_WIN
            else:
                # Returner wins on second serve
                self._record_event(PointEvent.RALLY_LOSS, returner.name)
                return returner.name, PointEvent.RALLY_LOSS
    
    def _record_event(self, event_type: PointEvent, player_name: str):
        """Record point event for later analysis"""
        self.point_history.append({
            "type": event_type.value,
            "player": player_name,
            "timestamp": len(self.point_history)
        })
