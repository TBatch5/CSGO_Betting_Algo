"""
Parser for converting BO3 API JSON responses to strongly typed models.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from models import (
    BO3Team,
    BO3Tournament,
    BO3Match,
    BO3AIPrediction,
    BO3PredictionScoresData,
    BO3BettingOdds,
    BO3BettingTeam,
)


def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 datetime string to datetime object."""
    if not date_str:
        return None
    try:
        # Handle both with and without timezone
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None


def parse_team(team_data: Optional[Dict[str, Any]]) -> Optional[BO3Team]:
    """Parse team data from API response to BO3Team model."""
    if not team_data or not isinstance(team_data, dict):
        return None
    
    team_id = team_data.get("id")
    name = team_data.get("name")
    
    if not team_id or not name:
        return None
    
    return BO3Team(
        id=int(team_id),
        name=str(name),
        slug=team_data.get("slug"),
        country_code=team_data.get("country_code"),
        logo_url=team_data.get("logo_url"),
    )


def parse_tournament(tournament_data: Optional[Dict[str, Any]]) -> Optional[BO3Tournament]:
    """Parse tournament data from API response to BO3Tournament model."""
    if not tournament_data or not isinstance(tournament_data, dict):
        return None
    
    tournament_id = tournament_data.get("id")
    name = tournament_data.get("name")
    
    if not tournament_id or not name:
        return None
    
    return BO3Tournament(
        id=int(tournament_id),
        name=str(name),
        slug=tournament_data.get("slug"),
        tier=tournament_data.get("tier"),
        tier_rank=tournament_data.get("tier_rank"),
        prize=tournament_data.get("prize"),
        discipline_id=tournament_data.get("discipline_id"),
        status=tournament_data.get("status"),
        start_date=parse_datetime(tournament_data.get("start_date")),
        end_date=parse_datetime(tournament_data.get("end_date")),
    )


def parse_prediction_scores_data(scores_data: Optional[Dict[str, Any]]) -> Optional[BO3PredictionScoresData]:
    """Parse prediction scores data from API response."""
    if not scores_data or not isinstance(scores_data, dict):
        return None
    
    return BO3PredictionScoresData(
        predicted_score=float(scores_data.get("predicted_score", 0.0)),
        proximity_factors=dict(scores_data.get("proximity_factors", {})),
        closest_valid_score=list(scores_data.get("closest_valid_score", [])),
        overall_proximity_factor=float(scores_data.get("overall_proximity_factor", 0.0)),
        neighbor_proximity_factor=float(scores_data.get("neighbor_proximity_factor", 0.0)),
    )


def parse_ai_prediction(prediction_data: Optional[Dict[str, Any]]) -> Optional[BO3AIPrediction]:
    """Parse AI prediction data from API response to BO3AIPrediction model."""
    if not prediction_data or not isinstance(prediction_data, dict):
        return None
    
    prediction_id = prediction_data.get("id")
    match_id = prediction_data.get("match_id")
    
    if not prediction_id or not match_id:
        return None
    
    scores_data = parse_prediction_scores_data(prediction_data.get("prediction_scores_data"))
    if not scores_data:
        return None
    
    return BO3AIPrediction(
        id=int(prediction_id),
        match_id=int(match_id),
        prediction_team1_score=int(prediction_data.get("prediction_team1_score", 0)),
        prediction_team2_score=int(prediction_data.get("prediction_team2_score", 0)),
        prediction_winner_team_id=int(prediction_data.get("prediction_winner_team_id", 0)),
        prediction_scores_data=scores_data,
    )


def parse_betting_team(team_data: Optional[Dict[str, Any]]) -> Optional[BO3BettingTeam]:
    """Parse betting team data from API response."""
    if not team_data or not isinstance(team_data, dict):
        return None
    
    return BO3BettingTeam(
        name=str(team_data.get("name", "")),
        coeff=float(team_data.get("coeff", 0.0)),
        active=bool(team_data.get("active", False)),
        team_id=int(team_data.get("team_id", 0)),
        max_coeff=float(team_data.get("max_coeff", 0.0)),
        aggrement_score=float(team_data.get("aggrement_score", 0.0)),
    )


def parse_betting_odds(odds_data: Optional[Dict[str, Any]]) -> Optional[BO3BettingOdds]:
    """Parse betting odds data from API response to BO3BettingOdds model."""
    if not odds_data or not isinstance(odds_data, dict):
        return None
    
    provider = odds_data.get("provider")
    team_1_data = odds_data.get("team_1")
    team_2_data = odds_data.get("team_2")
    
    if not provider or not team_1_data or not team_2_data:
        return None
    
    team_1 = parse_betting_team(team_1_data)
    team_2 = parse_betting_team(team_2_data)
    
    if not team_1 or not team_2:
        return None
    
    return BO3BettingOdds(
        provider=str(provider),
        team_1=team_1,
        team_2=team_2,
        path=odds_data.get("path"),
        markets_count=odds_data.get("markets_count"),
        additional_markets=odds_data.get("additional_markets"),
    )


def parse_match(match_data: Dict[str, Any]) -> BO3Match:
    """
    Parse match data from API response to BO3Match model.
    
    Args:
        match_data: Raw match dictionary from API response
        
    Returns:
        BO3Match model instance
    """
    match_id = match_data.get("id")
    if not match_id:
        raise ValueError("Match data must include 'id' field")
    
    # Parse nested objects if present
    team1 = parse_team(match_data.get("team1"))
    team2 = parse_team(match_data.get("team2"))
    tournament = parse_tournament(match_data.get("tournament"))
    ai_predictions = parse_ai_prediction(match_data.get("ai_predictions"))
    bet_updates = parse_betting_odds(match_data.get("bet_updates"))
    
    # Get team IDs from nested objects or direct fields
    team1_id = team1.id if team1 else match_data.get("team1_id")
    team2_id = team2.id if team2 else match_data.get("team2_id")
    tournament_id = tournament.id if tournament else match_data.get("tournament_id")
    
    return BO3Match(
        id=int(match_id),
        slug=match_data.get("slug"),
        team1_id=team1_id,
        team2_id=team2_id,
        status=str(match_data.get("status", "upcoming")),
        start_date=parse_datetime(match_data.get("start_date")),
        bo_type=match_data.get("bo_type"),
        tier=match_data.get("tier"),
        team1_score=match_data.get("team1_score"),
        team2_score=match_data.get("team2_score"),
        winner_team_id=match_data.get("winner_team_id"),
        loser_team_id=match_data.get("loser_team_id"),
        tournament_id=tournament_id,
        team1=team1,
        team2=team2,
        tournament=tournament,
        ai_predictions=ai_predictions,
        bet_updates=bet_updates,
        raw_data=match_data,  # Preserve full raw data
    )

