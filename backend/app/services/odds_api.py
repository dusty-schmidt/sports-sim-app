from sqlmodel import Session, select
from datetime import datetime, timedelta
import random
from app.models.tennis import Match
from app.services.data import PLAYERS_DB

import structlog

logger = structlog.get_logger()

async def update_live_odds(session: Session):
    """
    Mock implementation that generates realistic test matches.
    """
    logger.info("Fetching/Generating live odds")
    
    # 1. Clean up old matches (optional, for demo)
    
    # 2. Generate new matches if not enough exist
    existing_matches = session.exec(select(Match)).all()
    if len(existing_matches) < 5:
        logger.info("Generating mock matches", existing_count=len(existing_matches))
        player_names = list(PLAYERS_DB.keys())
        
        for i in range(3): # Create 3 matches
            p1 = random.choice(player_names)
            p2 = random.choice(player_names)
            while p1 == p2:
                p2 = random.choice(player_names)
                
            match = Match(
                player1_name=p1,
                player2_name=p2,
                start_time=datetime.now() + timedelta(hours=random.randint(1, 48)),
                surface=random.choice(["hard", "clay", "grass"]),
                p1_odds=random.choice([-150, -110, 110, 150, 200, -200]),
                p2_odds=random.choice([-150, -110, 110, 150, 200, -200]),
            )
            session.add(match)
            logger.info("Created mock match", match_index=i+1, p1=p1, p2=p2)
        
        session.commit()
        logger.info("Mock matches cleanup complete")
    else:
        logger.info("Matches already exist, skipping generation", count=len(existing_matches))
