"""
Database schema models.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime


@dataclass
class Team:
    """Represents a team in the database."""
    source_type: str
    source_id: int
    name: str
    slug: Optional[str] = None
    country_code: Optional[str] = None
    logo_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[UUID] = None


@dataclass
class Tournament:
    """Represents a tournament in the database."""
    source_type: str
    source_id: int
    name: str
    slug: Optional[str] = None
    tier: Optional[str] = None
    tier_rank: Optional[int] = None
    prize_pool: Optional[int] = None
    discipline_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[UUID] = None


@dataclass
class Match:
    """Represents a match in the database."""
    source_type: str
    source_id: int
    slug: Optional[str] = None
    status: str = "upcoming"
    start_date: Optional[datetime] = None
    bo_type: Optional[int] = None
    tier: Optional[str] = None
    team1_score: Optional[int] = None
    team2_score: Optional[int] = None
    winner_team_id: Optional[UUID] = None
    loser_team_id: Optional[UUID] = None
    raw_data: Optional[Dict[str, Any]] = None
    id: Optional[UUID] = None
    
    # Relationships (populated during mutation if available)
    team1: Optional[Team] = None
    team2: Optional[Team] = None
    tournament: Optional[Tournament] = None
    
    # Foreign keys (populated if known)
    team1_id: Optional[UUID] = None
    team2_id: Optional[UUID] = None
    tournament_id: Optional[UUID] = None


@dataclass
class AIPrediction:
    """Represents an AI prediction in the database."""
    match_id: UUID
    source_type: str
    source_id: Optional[int]
    prediction_data: Dict[str, Any]
    id: Optional[UUID] = None


@dataclass
class BettingOdds:
    """Represents betting odds in the database."""
    match_id: UUID
    source_type: str
    provider: str
    team1_odds: Optional[float]
    team2_odds: Optional[float]
    team1_implied_prob: Optional[float]
    team2_implied_prob: Optional[float]
    odds_data: Dict[str, Any]
    id: Optional[UUID] = None
