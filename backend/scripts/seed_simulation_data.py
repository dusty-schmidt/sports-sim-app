import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from sqlmodel import Session, select, create_engine
from app.models.tennis import Player, PlayerStats, Match
from app.core.config import settings

# Force SQLite
settings.USE_SQLITE = True
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

DATA_DIR = Path(__file__).parent.parent / "app" / "services" / "sims"
SERVE_STATS_FILE = DATA_DIR / "atp-serve-stats.csv"

def clean_pct(val: str) -> float:
    """Convert '12.3%' to 0.123"""
    if not val or val == "":
        return 0.0
    return float(val.replace("%", "")) / 100.0

def seed_players():
    print(f"Reading data from {SERVE_STATS_FILE}...")
    
    if not SERVE_STATS_FILE.exists():
        print(f"ERROR: File not found at {SERVE_STATS_FILE}")
        return

    players_created = 0
    stats_created = 0

    with Session(engine) as session:
        with open(SERVE_STATS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_name_raw = row["Player"]
                if not player_name_raw or player_name_raw == "Average":
                    continue
                
                # Cleanup name - remove [ITA] etc
                # "Jannik Sinner [ITA]" -> "Jannik Sinner"
                player_name = player_name_raw.split("[")[0].strip()

                # Check if player exists
                statement = select(Player).where(Player.name == player_name)
                player = session.exec(statement).first()

                if not player:
                    player = Player(
                        name=player_name,
                        rank=int(row["Rk"]) if row["Rk"] else None,
                        country=player_name_raw.split("[")[1].replace("]", "") if "[" in player_name_raw else None
                    )
                    session.add(player)
                    session.commit()
                    session.refresh(player)
                    players_created += 1
                
                # Check/Update Stats
                stat_statement = select(PlayerStats).where(
                    PlayerStats.player_id == player.id,
                    PlayerStats.surface == "All"
                )
                stats = session.exec(stat_statement).first()

                if not stats:
                    stats = PlayerStats(
                        player_id=player.id,
                        surface="All",
                        serve_1_in_pct=clean_pct(row["1stIn"]),
                        serve_1_won_pct=clean_pct(row["1st%"]),
                        serve_2_won_pct=clean_pct(row["2nd%"]),
                        ace_pct=clean_pct(row["Ace%"]),
                        df_pct=clean_pct(row["DF%"])
                    )
                    session.add(stats)
                    stats_created += 1
                else:
                    # Update existing? Skip for now.
                    pass
        
        session.commit()
        print(f"Created {players_created} players and {stats_created} stats records.")

def seed_matches():
    print("Generating sample matches...")
    with Session(engine) as session:
        # Get top 20 players
        players = session.exec(select(Player).limit(20)).all()
        if len(players) < 2:
            print("Not enough players to seed matches.")
            return

        # Create 5 matches
        matches_created = 0
        current_time = datetime.utcnow()

        for i in range(5):
            p1 = random.choice(players)
            p2 = random.choice(players)
            while p2.id == p1.id:
                p2 = random.choice(players)

            match = Match(
                player1_name=p1.name,
                player2_name=p2.name,
                start_time=current_time + timedelta(hours=i*2),
                surface="Hard",
                p1_odds=random.randint(-200, -110) if random.random() > 0.5 else random.randint(100, 150),
                p2_odds=random.randint(-200, -110) if random.random() > 0.5 else random.randint(100, 150)
            )
            session.add(match)
            matches_created += 1
        
        session.commit()
        print(f"Created {matches_created} sample matches.")

if __name__ == "__main__":
    seed_players()
    seed_matches()
