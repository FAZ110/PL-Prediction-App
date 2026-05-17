import os
from collections import defaultdict
from datetime import datetime
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth.service import get_current_user
from ..models.user import User, UserPick
from ..core.database import get_db
from ..core.leagues import LEAGUES

router = APIRouter(prefix="/picks", tags=["picks"])

BASE_URL = "https://api.football-data.org/v4"
FTR_MAP = {"HOME_TEAM": "H", "DRAW": "D", "AWAY_TEAM": "A"}


class PickCreate(BaseModel):
    home_team: str
    away_team: str
    league: str
    match_date: str           # ISO 8601
    user_pick: str            # 'H', 'D', 'A'
    model_prediction: Optional[str] = None
    model_confidence: Optional[float] = None


class PickOut(BaseModel):
    id: int
    home_team: str
    away_team: str
    league: str
    match_date: str
    user_pick: str
    model_prediction: Optional[str]
    model_confidence: Optional[float]
    actual_result: Optional[str]
    is_correct: Optional[bool]
    created_at: str


def _resolve_pending(user_id: int, db: Session) -> None:
    api_key = os.getenv("API_KEY")
    if not api_key:
        return

    pending = (
        db.query(UserPick)
        .filter(
            UserPick.user_id == user_id,
            UserPick.actual_result.is_(None),
            UserPick.match_date < datetime.utcnow(),
        )
        .all()
    )
    if not pending:
        return

    by_league: dict[str, list[UserPick]] = defaultdict(list)
    for p in pending:
        by_league[p.league].append(p)

    for league, picks in by_league.items():
        if league not in LEAGUES:
            continue
        code = LEAGUES[league]["competition_code"]
        try:
            r = requests.get(
                f"{BASE_URL}/competitions/{code}/matches",
                params={"status": "FINISHED"},
                headers={"X-Auth-Token": api_key},
                timeout=10,
            )
        except Exception:
            continue
        if r.status_code != 200:
            continue

        finished = r.json().get("matches", [])
        for match in finished:
            ht = match["homeTeam"]["shortName"]
            at = match["awayTeam"]["shortName"]
            winner = FTR_MAP.get(match["score"].get("winner", ""))
            if not winner:
                continue
            for pick in picks:
                if pick.home_team == ht and pick.away_team == at:
                    pick.actual_result = winner
                    pick.is_correct = pick.user_pick == winner

    db.commit()


class PickStats(BaseModel):
    total: int
    resolved: int
    correct: int
    accuracy: float
    current_streak: int
    best_streak: int


def _pick_to_out(p: UserPick) -> PickOut:
    return PickOut(
        id=p.id,
        home_team=p.home_team,
        away_team=p.away_team,
        league=p.league,
        match_date=p.match_date.isoformat(),
        user_pick=p.user_pick,
        model_prediction=p.model_prediction,
        model_confidence=p.model_confidence,
        actual_result=p.actual_result,
        is_correct=p.is_correct,
        created_at=p.created_at.isoformat(),
    )


@router.get("/stats", response_model=PickStats)
def get_pick_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    picks = (
        db.query(UserPick)
        .filter(UserPick.user_id == current_user.id)
        .order_by(UserPick.created_at.asc())
        .all()
    )
    resolved = [p for p in picks if p.actual_result is not None]
    correct_count = sum(1 for p in resolved if p.is_correct)

    current_streak = 0
    for p in reversed(resolved):
        if p.is_correct:
            current_streak += 1
        else:
            break

    best, run = 0, 0
    for p in resolved:
        run = run + 1 if p.is_correct else 0
        best = max(best, run)

    return PickStats(
        total=len(picks),
        resolved=len(resolved),
        correct=correct_count,
        accuracy=correct_count / len(resolved) if resolved else 0.0,
        current_streak=current_streak,
        best_streak=best,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PickOut)
def submit_pick(
    body: PickCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.user_pick not in ("H", "D", "A"):
        raise HTTPException(status_code=422, detail="user_pick must be H, D, or A")
    if body.league not in LEAGUES:
        raise HTTPException(status_code=400, detail=f"Unknown league: {body.league}")

    try:
        match_dt = datetime.fromisoformat(body.match_date.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid match_date format")

    existing = (
        db.query(UserPick)
        .filter(
            UserPick.user_id == current_user.id,
            UserPick.home_team == body.home_team,
            UserPick.away_team == body.away_team,
            UserPick.league == body.league,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already picked this match")

    pick = UserPick(
        user_id=current_user.id,
        home_team=body.home_team,
        away_team=body.away_team,
        league=body.league,
        match_date=match_dt,
        user_pick=body.user_pick,
        model_prediction=body.model_prediction,
        model_confidence=body.model_confidence,
    )
    db.add(pick)
    db.commit()
    db.refresh(pick)
    return _pick_to_out(pick)


@router.get("", response_model=list[PickOut])
def get_picks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _resolve_pending(current_user.id, db)
    picks = (
        db.query(UserPick)
        .filter(UserPick.user_id == current_user.id)
        .order_by(UserPick.match_date.desc())
        .all()
    )
    return [_pick_to_out(p) for p in picks]
