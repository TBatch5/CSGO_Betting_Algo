"""
Base mutation interface for converting API responses to database schema.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID


class BaseMutation(ABC):
    """
    Base class for data mutations.
    
    Mutations convert strongly typed API response models into database-ready
    dictionaries that match the database schema.
    """
    
    @abstractmethod
    def to_team_dict(self, team_data: Any) -> Dict[str, Any]:
        """
        Convert API team model to database team dictionary.
        
        Args:
            team_data: Strongly typed team model from API
            
        Returns:
            Dictionary ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_tournament_dict(self, tournament_data: Any) -> Dict[str, Any]:
        """
        Convert API tournament model to database tournament dictionary.
        
        Args:
            tournament_data: Strongly typed tournament model from API
            
        Returns:
            Dictionary ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_match_dict(self, match_data: Any) -> Dict[str, Any]:
        """
        Convert API match model to database match dictionary.
        
        Args:
            match_data: Strongly typed match model from API
            
        Returns:
            Dictionary ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_ai_prediction_dict(self, prediction_data: Any, match_id: UUID) -> Dict[str, Any]:
        """
        Convert API AI prediction model to database prediction dictionary.
        
        Args:
            prediction_data: Strongly typed AI prediction model from API
            match_id: UUID of the match this prediction is for
            
        Returns:
            Dictionary ready for database insertion
        """
        pass
    
    @abstractmethod
    def to_betting_odds_dict(self, odds_data: Any, match_id: UUID) -> Dict[str, Any]:
        """
        Convert API betting odds model to database odds dictionary.
        
        Args:
            odds_data: Strongly typed betting odds model from API
            match_id: UUID of the match these odds are for
            
        Returns:
            Dictionary ready for database insertion
        """
        pass

