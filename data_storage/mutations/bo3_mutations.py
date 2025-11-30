"""
BO3 API mutation converters.

Converts strongly typed BO3 API models to database-ready dataclasses.
"""

from typing import Dict, Any, Optional
from uuid import UUID
import sys
from pathlib import Path

from mutations.base import BaseMutation
from models import Team, Tournament, Match, AIPrediction, BettingOdds

# Import BO3 models from data-ingestion
# Note: This assumes data-ingestion is in the parent directory structure
# In production, you may want to install data-ingestion as a package
data_ingestion_path = Path(__file__).parent.parent.parent.parent / 'data-ingestion' / 'bo3-api'
if data_ingestion_path.exists():
    sys.path.insert(0, str(data_ingestion_path))
    try:
        from models import (  # type: ignore
            BO3Team,
            BO3Tournament,
            BO3Match,
            BO3AIPrediction,
            BO3BettingOdds,
        )
    except ImportError:
        # Fallback if models can't be imported
        BO3Team = Any  # type: ignore
        BO3Tournament = Any  # type: ignore
        BO3Match = Any  # type: ignore
        BO3AIPrediction = Any  # type: ignore
        BO3BettingOdds = Any  # type: ignore
else:
    # Fallback for when models aren't available
    BO3Team = Any  # type: ignore
    BO3Tournament = Any  # type: ignore
    BO3Match = Any  # type: ignore
    BO3AIPrediction = Any  # type: ignore
    BO3BettingOdds = Any  # type: ignore


class BO3Mutation(BaseMutation):
    """
    Mutation converter for BO3 API responses.
    
    Converts strongly typed BO3 models to database schema format.
    """
    
    SOURCE_TYPE = "bo3"
    
    def to_team(self, team_data: BO3Team) -> Team:
        """
        Convert BO3Team to database Team object.
        
        Args:
            team_data: BO3Team model
            
        Returns:
            Team object for database insertion
        """
        return Team(
            source_type=self.SOURCE_TYPE,
            source_id=team_data.id,
            name=team_data.name,
            slug=team_data.slug,
            country_code=team_data.country_code,
            logo_url=team_data.logo_url,
            metadata={
                "id": team_data.id,
                "name": team_data.name,
                "slug": team_data.slug,
                "country_code": team_data.country_code,
                "logo_url": team_data.logo_url,
            }
        )
    
    def to_tournament(self, tournament_data: BO3Tournament) -> Tournament:
        """
        Convert BO3Tournament to database Tournament object.
        
        Args:
            tournament_data: BO3Tournament model
            
        Returns:
            Tournament object for database insertion
        """
        return Tournament(
            source_type=self.SOURCE_TYPE,
            source_id=tournament_data.id,
            name=tournament_data.name,
            slug=tournament_data.slug,
            tier=tournament_data.tier,
            tier_rank=tournament_data.tier_rank,
            prize_pool=tournament_data.prize,
            discipline_id=tournament_data.discipline_id,
            status=tournament_data.status,
            start_date=tournament_data.start_date,
            end_date=tournament_data.end_date,
            metadata={
                "id": tournament_data.id,
                "name": tournament_data.name,
                "slug": tournament_data.slug,
                "tier": tournament_data.tier,
                "tier_rank": tournament_data.tier_rank,
                "prize": tournament_data.prize,
                "discipline_id": tournament_data.discipline_id,
                "status": tournament_data.status,
                "start_date": tournament_data.start_date.isoformat() if tournament_data.start_date else None,
                "end_date": tournament_data.end_date.isoformat() if tournament_data.end_date else None,
            }
        )
    
    def to_match(self, match_data: BO3Match) -> Match:
        """
        Convert BO3Match to database Match object.
        
        Args:
            match_data: BO3Match model
            
        Returns:
            Match object for database insertion
        """
        # Get team IDs from nested objects or direct fields
        team1_id = match_data.team1.id if match_data.team1 else match_data.team1_id
        team2_id = match_data.team2.id if match_data.team2 else match_data.team2_id
        tournament_id = match_data.tournament.id if match_data.tournament else match_data.tournament_id
        
        match = Match(
            source_type=self.SOURCE_TYPE,
            source_id=match_data.id,
            slug=match_data.slug,
            status=match_data.status,
            start_date=match_data.start_date,
            bo_type=match_data.bo_type,
            tier=match_data.tier,
            team1_score=match_data.team1_score,
            team2_score=match_data.team2_score,
            winner_team_id=match_data.winner_team_id,
            loser_team_id=match_data.loser_team_id,
            raw_data=match_data.raw_data or self._match_to_raw_dict(match_data)
        )
        
        # Populate relationships if available
        if match_data.team1:
            match.team1 = self.to_team(match_data.team1)
        
        if match_data.team2:
            match.team2 = self.to_team(match_data.team2)
            
        if match_data.tournament:
            match.tournament = self.to_tournament(match_data.tournament)
            
        return match
    
    def to_ai_prediction(
        self,
        prediction_data: BO3AIPrediction,
        match_id: UUID
    ) -> AIPrediction:
        """
        Convert BO3AIPrediction to database AIPrediction object.
        
        Args:
            prediction_data: BO3AIPrediction model
            match_id: UUID of the match
            
        Returns:
            AIPrediction object for database insertion
        """
        return AIPrediction(
            match_id=match_id,
            source_type=self.SOURCE_TYPE,
            source_id=prediction_data.id,
            prediction_data={
                "id": prediction_data.id,
                "match_id": prediction_data.match_id,
                "prediction_team1_score": prediction_data.prediction_team1_score,
                "prediction_team2_score": prediction_data.prediction_team2_score,
                "prediction_winner_team_id": prediction_data.prediction_winner_team_id,
                "prediction_scores_data": {
                    "predicted_score": prediction_data.prediction_scores_data.predicted_score,
                    "proximity_factors": prediction_data.prediction_scores_data.proximity_factors,
                    "closest_valid_score": prediction_data.prediction_scores_data.closest_valid_score,
                    "overall_proximity_factor": prediction_data.prediction_scores_data.overall_proximity_factor,
                    "neighbor_proximity_factor": prediction_data.prediction_scores_data.neighbor_proximity_factor,
                },
            }
        )
    
    def to_betting_odds(
        self,
        odds_data: BO3BettingOdds,
        match_id: UUID
    ) -> BettingOdds:
        """
        Convert BO3BettingOdds to database BettingOdds object.
        
        Args:
            odds_data: BO3BettingOdds model
            match_id: UUID of the match
            
        Returns:
            BettingOdds object for database insertion
        """
        team1_implied_prob = 1.0 / odds_data.team_1.coeff if odds_data.team_1.coeff else None
        team2_implied_prob = 1.0 / odds_data.team_2.coeff if odds_data.team_2.coeff else None
        
        return BettingOdds(
            match_id=match_id,
            source_type=self.SOURCE_TYPE,
            provider=odds_data.provider,
            team1_odds=odds_data.team_1.coeff,
            team2_odds=odds_data.team_2.coeff,
            team1_implied_prob=team1_implied_prob,
            team2_implied_prob=team2_implied_prob,
            odds_data={
                "path": odds_data.path,
                "provider": odds_data.provider,
                "team_1": {
                    "name": odds_data.team_1.name,
                    "coeff": odds_data.team_1.coeff,
                    "active": odds_data.team_1.active,
                    "team_id": odds_data.team_1.team_id,
                    "max_coeff": odds_data.team_1.max_coeff,
                    "aggrement_score": odds_data.team_1.aggrement_score,
                },
                "team_2": {
                    "name": odds_data.team_2.name,
                    "coeff": odds_data.team_2.coeff,
                    "active": odds_data.team_2.active,
                    "team_id": odds_data.team_2.team_id,
                    "max_coeff": odds_data.team_2.max_coeff,
                    "aggrement_score": odds_data.team_2.aggrement_score,
                },
                "markets_count": odds_data.markets_count,
                "additional_markets": odds_data.additional_markets,
            }
        )
    
    def _match_to_raw_dict(self, match_data: BO3Match) -> Dict[str, Any]:
        """Convert BO3Match to raw dictionary for storage."""
        return {
            "id": match_data.id,
            "slug": match_data.slug,
            "team1_id": match_data.team1_id,
            "team2_id": match_data.team2_id,
            "status": match_data.status,
            "start_date": match_data.start_date.isoformat() if match_data.start_date else None,
            "bo_type": match_data.bo_type,
            "tier": match_data.tier,
            "team1_score": match_data.team1_score,
            "team2_score": match_data.team2_score,
            "winner_team_id": match_data.winner_team_id,
            "loser_team_id": match_data.loser_team_id,
            "tournament_id": match_data.tournament_id,
        }
