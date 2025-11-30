"""
Base mutation interface for converting API responses to database schema.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID
from mutations.models import Team, Tournament, Match, AIPrediction, BettingOdds


class BaseMutation(ABC):
    """
    Base class for data mutations.
    
    Mutations convert strongly typed API response models into database-ready
    dataclasses that match the database schema.
    """
    
    @abstractmethod
    def to_team(self, team_data: Any) -> Team:
        """
        Convert API team model to database Team object.
        
        Args:
            team_data: Strongly typed team model from API
            
        Returns:
            Team object ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_tournament(self, tournament_data: Any) -> Tournament:
        """
        Convert API tournament model to database Tournament object.
        
        Args:
            tournament_data: Strongly typed tournament model from API
            
        Returns:
            Tournament object ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_match(self, match_data: Any) -> Match:
        """
        Convert API match model to database Match object.
        
        Args:
            match_data: Strongly typed match model from API
            
        Returns:
            Match object ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_ai_prediction(self, prediction_data: Any, match_id: UUID) -> AIPrediction:
        """
        Convert API AI prediction model to database AIPrediction object.
        
        Args:
            prediction_data: Strongly typed AI prediction model from API
            match_id: UUID of the match this prediction is for
            
        Returns:
            AIPrediction object ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_betting_odds(self, odds_data: Any, match_id: UUID) -> BettingOdds:
        """
        Convert API betting odds model to database BettingOdds object.
        
        Args:
            odds_data: Strongly typed betting odds model from API
            match_id: UUID of the match these odds are for
            
        Returns:
            BettingOdds object ready for database insertion
        """
        pass
