import csv
import os
import sys
import re
import structlog
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.core.db import engine
from app.models import Player, PlayerStats
from app.core.logging import setup_logging

# Setup Logging
setup_logging()
logger = structlog.get_logger(__name__)

SEED_DATA_DIR = Path("C:/Users/JANET/dusty/test-app/DEV-DOCS/SEED-DATA")

def clean_pct(val):
    if not val or val == 'nan' or val == '': return 0.0
    try:
        return float(val.replace('%', '')) / 100.0
    except ValueError:
        return 0.0

def clean_int(val):
    if not val or val == 'nan' or val == '': return None
    try:
        return int(float(val))
    except ValueError:
        return None

def parse_name_stats(raw_name):
    # Raw: "Carlos Alcaraz (http://...) [ESP]"
    # 1. Remove (...) URL stuff
    name = re.sub(r'\s*\(.*?\)', '', raw_name)
    # 2. Remove [...] Country codes
    name = re.sub(r'\s*\[.*?\]', '', name)
    # 3. Strip
    return name.strip()

def get_or_create_player(session, name):
    player = session.exec(select(Player).where(Player.name == name)).first()
    if not player:
        logger.info("creating_new_player", name=name)
        player = Player(name=name)
        session.add(player)
        session.commit()
        session.refresh(player)
    return player

def get_or_create_stats(session, player_id, surface):
    stats = session.exec(select(PlayerStats).where(PlayerStats.player_id == player_id, PlayerStats.surface == surface)).first()
    if not stats:
        stats = PlayerStats(player_id=player_id, surface=surface)
        session.add(stats)
        session.commit()
        session.refresh(stats)
    return stats

def seed_elo(session):
    fpath = SEED_DATA_DIR / "atp-elo.csv"
    if not fpath.exists():
        logger.warning("file_not_found", path=str(fpath))
        return

    logger.info("seeding_elo", file=fpath.name)
    with open(fpath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Player")
            if not name: continue
            
            # Elo CSV name is clean "Jannik Sinner"
            # Verify if we need to clean it? Elo file seemed clean.
            name = name.strip()
            
            player = get_or_create_player(session, name)
            
            # Update Elo fields
            player.elo_overall = clean_int(row.get("Elo"))
            player.elo_hard = clean_int(row.get("hElo"))
            player.elo_clay = clean_int(row.get("cElo"))
            player.elo_grass = clean_int(row.get("gElo"))
            player.age = float(row.get("Age")) if row.get("Age") else None
            player.rank = clean_int(row.get("Elo Rank")) 
            
            session.add(player)
    session.commit()

def seed_serve(session, filename, surface_name):
    fpath = SEED_DATA_DIR / filename
    if not fpath.exists():
        logger.warning("file_not_found", path=str(fpath))
        return
        
    logger.info("seeding_serve_stats", surface=surface_name, file=fpath.name)
    with open(fpath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_name = row.get("Player")
            if not raw_name: continue
            name = parse_name_stats(raw_name)
            
            player = get_or_create_player(session, name)
            stats = get_or_create_stats(session, player.id, surface_name)
            
            # "1st%": serve_1_in_pct
            stats.serve_1_in_pct = clean_pct(row.get("1st%"))
            # "1stW%": serve_1_won_pct
            stats.serve_1_won_pct = clean_pct(row.get("1stW%"))
            # "2ndW%": serve_2_won_pct
            stats.serve_2_won_pct = clean_pct(row.get("2ndW%"))
            # "Ace%": ace_pct
            stats.ace_pct = clean_pct(row.get("Ace%"))
            # "DF%": df_pct
            stats.df_pct = clean_pct(row.get("DF%"))
            
            if "Sinner" in name:
                logger.debug("sinner_stats_update", surface=surface_name, serve_1_in=stats.serve_1_in_pct)
            
            session.add(stats)
    session.commit()

def seed_return(session, filename, surface_name):
    fpath = SEED_DATA_DIR / filename
    if not fpath.exists():
        logger.warning("file_not_found", path=str(fpath))
        return
        
    logger.info("seeding_return_stats", surface=surface_name, file=fpath.name)
    with open(fpath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_name = row.get("Player")
            if not raw_name: continue
            name = parse_name_stats(raw_name)
            
            player = get_or_create_player(session, name)
            stats = get_or_create_stats(session, player.id, surface_name)
            
            # "RPW": return_won_pct
            stats.return_won_pct = clean_pct(row.get("RPW"))
            
            session.add(stats)
    session.commit()

def main():
    try:
        with Session(engine) as session:
            # 1. Seed Elo first (to get base player list and ranks)
            seed_elo(session)
            
            # 2. Seed Surfaces
            seed_serve(session, 'atp-serve-hard.csv', 'Hard')
            seed_return(session, 'atp-return-hard.csv', 'Hard')
            
            seed_serve(session, 'atp-serve-clay.csv', 'Clay')
            seed_return(session, 'atp-return-clay.csv', 'Clay')
            
            seed_serve(session, 'atp-serve-grass.csv', 'Grass')
            seed_return(session, 'atp-return-grass.csv', 'Grass')
            
            seed_serve(session, 'atp-serve-all.csv', 'All')
            seed_return(session, 'atp-return-all.csv', 'All')
            
            logger.info("seeding_complete")
    except Exception as e:
        logger.error("seeding_failed", error=str(e))

if __name__ == "__main__":
    main()
