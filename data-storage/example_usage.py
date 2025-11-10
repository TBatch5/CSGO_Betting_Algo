"""
Example usage of the storage service.

This demonstrates how to use the StorageService to save and retrieve
BO3 API data including matches, AI predictions, and betting odds.
"""

from storage_service import StorageService
from uuid import UUID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_save_match_with_predictions() -> None:
    """Example: Save a match with AI predictions and betting odds."""
    storage = StorageService()
    
    # Example match data from BO3 API
    match_data = {
        "id": 103084,
        "slug": "example-match",
        "status": "upcoming",
        "start_date": "2025-01-28T10:00:00Z",
        "bo_type": 3,
        "tier": "s",
        "team1": {
            "id": 736,
            "name": "The MongolZ",
            "slug": "the-mongolz"
        },
        "team2": {
            "id": 7631,
            "name": "Passion UA",
            "slug": "passion-ua"
        },
        "tournament": {
            "id": 3578,
            "name": "BLAST Rivals Fall 2025",
            "slug": "blast-rivals-fall-2025",
            "tier": "s"
        }
    }
    
    try:
        # Save match
        match_id = storage.save_match(match_data, source_type="bo3")
        logger.info(f"Saved match with ID: {match_id}")
        
        # Example AI prediction data
        ai_prediction = {
            "id": 110222,
            "prediction_team1_score": 2,
            "prediction_team2_score": 0,
            "prediction_winner_team_id": 736,
            "prediction_scores_data": {
                "predicted_score": 2.39,
                "proximity_factors": {
                    "(0, 2)": 0.933490527805698,
                    "(1, 2)": 0.898718600319035,
                    "(2, 0)": 0.457145095905913,
                    "(2, 1)": 0.710645775969354
                },
                "closest_valid_score": [2, 0],
                "overall_proximity_factor": 0.510284162196592,
                "neighbor_proximity_factor": 0.289354224030646
            },
            "match_id": 103084
        }
        
        # Save AI prediction
        prediction_id = storage.save_ai_prediction(match_id, ai_prediction, source_type="bo3")
        logger.info(f"Saved AI prediction with ID: {prediction_id}")
        
        # Example betting odds data
        odds_data = {
            "provider": "1xbit",
            "team_1": {
                "name": "The MongolZ",
                "coeff": 1.3,
                "active": True,
                "team_id": 736,
                "max_coeff": 1.3,
                "aggrement_score": 0.74
            },
            "team_2": {
                "name": "Passion UA",
                "coeff": 3.52,
                "active": True,
                "team_id": 7631,
                "max_coeff": 3.52,
                "aggrement_score": 0.26
            },
            "markets_count": 36
        }
        
        # Save betting odds
        odds_id = storage.save_betting_odds(
            match_id, 
            odds_data, 
            source_type="bo3", 
            provider="1xbit"
        )
        logger.info(f"Saved betting odds with ID: {odds_id}")
        
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise


def example_query_matches() -> None:
    """Example: Query matches with different filters."""
    storage = StorageService()
    
    try:
        # Get upcoming matches
        upcoming = storage.get_matches(status="upcoming", limit=10)
        logger.info(f"Found {len(upcoming)} upcoming matches")
        
        # Get finished matches
        finished = storage.get_matches(status="finished", limit=10)
        logger.info(f"Found {len(finished)} finished matches")
        
        # Get a specific match
        if upcoming:
            match_id = UUID(upcoming[0]["id"])
            match = storage.get_match(match_id)
            if match:
                logger.info(f"Match details: {match['status']} - {match['start_date']}")
                
                # Get AI predictions for this match
                predictions = storage.get_ai_predictions(match_id)
                logger.info(f"Found {len(predictions)} AI predictions")
                
                # Get betting odds for this match
                odds = storage.get_betting_odds(match_id)
                logger.info(f"Found {len(odds)} betting odds entries")
        
    except Exception as e:
        logger.error(f"Error querying matches: {e}")
        raise


def example_update_match_results() -> None:
    """Example: Update match with results after completion."""
    storage = StorageService()
    
    try:
        # Get a finished match (or use a known match ID)
        finished_matches = storage.get_matches(status="finished", limit=1)
        
        if not finished_matches:
            logger.info("No finished matches found to update")
            return
        
        match_id = UUID(finished_matches[0]["id"])
        
        # Update match with results
        storage.update_match(match_id, {
            "status": "finished",
            "team1_score": 2,
            "team2_score": 0,
            # winner_team_id would be the UUID of the winning team
        })
        
        logger.info(f"Updated match {match_id} with results")
        
    except Exception as e:
        logger.error(f"Error updating match: {e}")
        raise


if __name__ == "__main__":
    print("=== Example 1: Save Match with Predictions ===")
    example_save_match_with_predictions()
    
    print("\n=== Example 2: Query Matches ===")
    example_query_matches()
    
    print("\n=== Example 3: Update Match Results ===")
    example_update_match_results()

