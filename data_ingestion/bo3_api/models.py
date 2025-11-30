"""
Strongly typed models for BO3 API responses.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BO3Team:
    """BO3 API team model."""
    id: int
    name: str
    slug: Optional[str] = None
    country_code: Optional[str] = None
    logo_url: Optional[str] = None


@dataclass
class BO3Tournament:
    """BO3 API tournament model."""
    id: int
    name: str
    slug: Optional[str] = None
    tier: Optional[str] = None
    tier_rank: Optional[int] = None
    prize: Optional[int] = None
    discipline_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class BO3PredictionScoresData:
    """BO3 API prediction scores data model."""
    predicted_score: float
    proximity_factors: Dict[str, float]  # Keys like "(0, 2)", values are probabilities
    closest_valid_score: List[int]
    overall_proximity_factor: float
    neighbor_proximity_factor: float


@dataclass
class BO3AIPrediction:
    """BO3 API AI prediction model."""
    id: int
    match_id: int
    prediction_team1_score: int
    prediction_team2_score: int
    prediction_winner_team_id: int
    prediction_scores_data: BO3PredictionScoresData


@dataclass
class BO3BettingTeam:
    """BO3 API betting team model."""
    name: str
    coeff: float
    active: bool
    team_id: int
    max_coeff: float
    aggrement_score: float


@dataclass
class BO3BettingOdds:
    """BO3 API betting odds model."""
    provider: str
    team_1: BO3BettingTeam
    team_2: BO3BettingTeam
    path: Optional[str] = None
    markets_count: Optional[int] = None
    additional_markets: Optional[List[Dict[str, Any]]] = None


@dataclass
class BO3Match:
    """BO3 API match model."""
    id: int
    slug: Optional[str] = None
    team1_id: Optional[int] = None
    team2_id: Optional[int] = None
    status: str = "upcoming"
    start_date: Optional[datetime] = None
    bo_type: Optional[int] = None
    tier: Optional[str] = None
    team1_score: Optional[int] = None
    team2_score: Optional[int] = None
    winner_team_id: Optional[int] = None
    loser_team_id: Optional[int] = None
    tournament_id: Optional[int] = None
    
    # Related objects (when included in API response)
    team1: Optional[BO3Team] = None
    team2: Optional[BO3Team] = None
    tournament: Optional[BO3Tournament] = None
    ai_predictions: Optional[BO3AIPrediction] = None
    bet_updates: Optional[BO3BettingOdds] = None
    
    # Raw data for preservation
    raw_data: Optional[Dict[str, Any]] = None

