from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

# --- Models ---

class Player(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    slug: Optional[str] = None # For URL matching if needed
    
    # Bio / Current Rank
    rank: Optional[int] = None
    age: Optional[float] = None
    country: Optional[str] = None
    
    # Elo Ratings (Current) - Extracted from Elo Tables
    elo_overall: Optional[int] = None
    elo_hard: Optional[int] = None
    elo_clay: Optional[int] = None
    elo_grass: Optional[int] = None
    
    # Relationships
    stats: List["PlayerStats"] = Relationship(back_populates="player")


class PlayerStats(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    player_id: uuid.UUID = Field(foreign_key="player.id", ondelete="CASCADE")
    
    surface: str = Field(index=True) # All, Hard, Clay, Grass
    
    # Serve Stats
    serve_1_in_pct: float = 0.0
    serve_1_won_pct: float = 0.0
    serve_2_won_pct: float = 0.0
    ace_pct: float = 0.0
    df_pct: float = 0.0
    
    # Return Stats
    return_won_pct: float = 0.0
    
    player: Player = Relationship(back_populates="stats")


class Match(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    player1_name: str
    player2_name: str
    start_time: datetime
    surface: str = "Hard"
    
    # Betting Market Data (Live Updates)
    p1_odds: int = -110 # American Odds
    p2_odds: int = -110
    market_vig: float = 0.045 # Calculated House Edge
    
    # Simulator Link
    last_simulated_at: Optional[datetime] = None
    sim_win_prob_p1: Optional[float] = None
