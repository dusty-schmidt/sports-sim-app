from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.services.odds_api import update_live_odds
import asyncio
import structlog
from app.core.logging import setup_logging

setup_logging()
logger = structlog.get_logger()

celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND

if settings.USE_SQLITE:
    celery.conf.task_always_eager = True
    celery.conf.broker_url = "memory://"
    # We need to ensure we don't try to connect to Redis


# --- 1. THE SCHEDULE (BEAT) ---
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Setting up periodic tasks")
    # Fetch Odds every 15 minutes
    sender.add_periodic_task(
        crontab(minute='*/15'), 
        run_odds_fetch.s(), 
        name='fetch-live-odds'
    )
    # Fetch Stats once a day at 4am (Stub)
    sender.add_periodic_task(
        crontab(hour=4, minute=0), 
        run_stats_fetch.s(), 
        name='fetch-daily-stats'
    )

# --- 2. THE TASKS (WORKERS) ---

@celery.task
def run_odds_fetch():
    logger.info("Starting odds fetch task")
    from sqlmodel import Session
    from app.core.db import engine
    session = Session(engine)
    try:
        asyncio.run(update_live_odds(session))
        logger.info("Odds fetch task completed")
    except Exception as e:
        logger.error("Odds fetch failed", error=str(e))
    finally:
        session.close()

@celery.task
def run_stats_fetch():
    logger.info("Fetching daily stats (Not implemented)")

@celery.task
def run_tennis_simulation(match_id: str, n_sims: int = 2000):
    """
    Run the Monte Carlo simulation for a match.
    """
    from sqlmodel import Session
    from app.core.db import engine
    from app.models.tennis import Match
    from app.services.data import PLAYERS_DB
    from app.services.sim_engine import TennisMatchSimulator, PlayerProfile
    from datetime import datetime
    
    session = Session(engine)
    try:
        logger.info("Starting simulation", match_id=match_id, n_sims=n_sims)
        match = session.get(Match, match_id)
        if not match:
            logger.error("Match not found", match_id=match_id)
            return "Match not found"
        
        # 1. Load Player Profiles
        p1_profile = PLAYERS_DB.get(match.player1_name)
        p2_profile = PLAYERS_DB.get(match.player2_name)
        
        if not p1_profile or not p2_profile:
            logger.error("Missing stats", 
                         p1=match.player1_name, 
                         p2=match.player2_name,
                         p1_found=bool(p1_profile),
                         p2_found=bool(p2_profile)
            )
            return "Missing Player Stats"

        # 2. Run Engine
        # Convert dict stats to PlayerProfile objects
        p1_stats = p1_profile["stats"].get(match.surface, p1_profile["stats"]["hard"])
        p2_stats = p2_profile["stats"].get(match.surface, p2_profile["stats"]["hard"])
        
        p1_obj = PlayerProfile(
            name=p1_profile["name"],
            serve_1_in_pct=p1_stats["serve_1_in"],
            serve_1_won_pct=p1_stats["serve_1_won"],
            serve_2_won_pct=p1_stats["serve_2_won"],
            ace_pct=p1_stats["ace_rate"],
            df_pct=p1_stats["df_rate"],
            return_won_pct=p1_stats["return_won"]
        )
        
        p2_obj = PlayerProfile(
            name=p2_profile["name"],
            serve_1_in_pct=p2_stats["serve_1_in"],
            serve_1_won_pct=p2_stats["serve_1_won"],
            serve_2_won_pct=p2_stats["serve_2_won"],
            ace_pct=p2_stats["ace_rate"],
            df_pct=p2_stats["df_rate"],
            return_won_pct=p2_stats["return_won"]
        )

        sim = TennisMatchSimulator(p1_obj, p2_obj, sets_to_win=2) # Default to 2 sets for now
        results = sim.run(n_sims=n_sims) # Returns List[MatchStats]
        
        # 3. Post-Process (Scoring & Aggregating)
        p1_wins = 0
        from app.services.fantasy_scoring import calculate_fantasy_points
        
        p1_fantasy_points = []
        p2_fantasy_points = []
        
        for res in results:
            if res.winner == p1_obj.name:
                p1_wins += 1
                
            fp1 = calculate_fantasy_points(res.p1_stats)
            fp2 = calculate_fantasy_points(res.p2_stats)
            
            p1_fantasy_points.append(fp1)
            p2_fantasy_points.append(fp2)
            
        p1_win_pct = p1_wins / n_sims
        avg_fp1 = sum(p1_fantasy_points) / n_sims
        avg_fp2 = sum(p2_fantasy_points) / n_sims
        
        # 4. Save Results
        match.sim_win_prob_p1 = p1_win_pct
        match.last_simulated_at = datetime.now()
        session.add(match)
        session.commit()
        
        logger.info("Sim Complete", 
                    match_id=match_id, 
                    p1_win_pct=p1_win_pct,
                    p1_avg_fp=avg_fp1,
                    simulations=n_sims
        )
        return {"p1_win_pct": p1_win_pct, "p1_avg_fp": avg_fp1, "p2_avg_fp": avg_fp2}
    except Exception as e:
        logger.error("Error in simulation", match_id=match_id, error=str(e))
        return f"Error: {e}"
    finally:
        session.close()
