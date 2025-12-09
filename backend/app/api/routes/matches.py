from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, func

from app.api.deps import CurrentUser, SessionDep
from app.models.tennis import Match
from app.worker import run_tennis_simulation

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("/", response_model=list[Match])
def read_matches(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve matches.
    """
    statement = select(Match).offset(skip).limit(limit).order_by(Match.start_time)
    return session.exec(statement).all()

@router.post("/{match_id}/simulate", response_model=Any)
def trigger_simulation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    match_id: UUID,
) -> Any:
    """
    Trigger a simulation for a specific match.
    """
    match = session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Trigger Celery Task
    task = run_tennis_simulation.delay(str(match_id))
    
    return {"message": "Simulation triggered", "task_id": str(task.id)}
