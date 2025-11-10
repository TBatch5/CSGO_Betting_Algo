"""
Example usage of the BO3 API client.

This demonstrates how to use the BO3Client to fetch matches with AI predictions
for Method 1 implementation.
"""

from bo3_client import BO3Client
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


def example_fetch_upcoming_week() -> None:
    """Example: Fetch all upcoming matches for the next week."""
    client = BO3Client()
    
    try:
        # Fetch upcoming matches for the next 7 days
        matches = client.fetch_upcoming_week_matches(days_ahead=7)
        
        print(f"Found {len(matches)} upcoming matches")
        
        # Display first match details
        if matches:
            match = matches[0]
            print(f"\nFirst match: {match.get('id')}")
            print(f"Teams: {match.get('team1', {}).get('name')} vs {match.get('team2', {}).get('name')}")
            print(f"Start date: {match.get('start_date')}")
            
            # Check for AI predictions
            ai_pred = client.extract_ai_predictions(match)
            if ai_pred:
                print(f"AI Prediction: {ai_pred.get('prediction_team1_score')}-{ai_pred.get('prediction_team2_score')}")
                print(f"Predicted winner: Team ID {ai_pred.get('prediction_winner_team_id')}")
            
            # Check for betting odds
            odds = client.extract_betting_odds(match)
            if odds:
                print(f"Betting odds available from {odds.get('provider')}")
                print(f"Team 1 odds: {odds.get('team_1', {}).get('coeff')}")
                print(f"Team 2 odds: {odds.get('team_2', {}).get('coeff')}")
    
    finally:
        client.close()


def example_fetch_with_tournament_whitelist() -> None:
    """Example: Fetch matches from specific tournaments only."""
    client = BO3Client()
    
    try:
        # Whitelist specific tournament IDs
        tournament_ids = [3578, 4473]  # Example tournament IDs
        
        matches = client.fetch_upcoming_week_matches(
            days_ahead=7,
            tournament_ids=tournament_ids
        )
        
        print(f"Found {len(matches)} matches from whitelisted tournaments")
        
        # Get unique tournaments
        tournaments = client.get_unique_tournaments(matches)
        print(f"Tournaments: {tournaments}")
    
    finally:
        client.close()


def example_fetch_matches_with_predictions() -> None:
    """Example: Fetch only matches that have AI predictions (and optionally odds)."""
    client = BO3Client()
    
    try:
        # Fetch matches with AI predictions (odds optional)
        matches = client.get_matches_with_predictions(
            days_ahead=7,
            require_odds=False  # Set to True to require betting odds
        )
        
        print(f"Found {len(matches)} matches with AI predictions")
        
        # Process matches for Method 1
        for match in matches[:5]:  # Show first 5
            ai_pred = match.get("ai_predictions")
            odds = match.get("bet_updates")
            
            if ai_pred and odds:
                team1_name = match.get("team1", {}).get("name")
                team2_name = match.get("team2", {}).get("name")
                
                predicted_winner_id = ai_pred.get("prediction_winner_team_id")
                predicted_team1_score = ai_pred.get("prediction_team1_score")
                predicted_team2_score = ai_pred.get("prediction_team2_score")
                
                team1_odds = odds.get("team_1", {}).get("coeff")
                team2_odds = odds.get("team_2", {}).get("coeff")
                
                # Calculate implied probabilities from odds
                team1_implied_prob = 1 / team1_odds if team1_odds else None
                team2_implied_prob = 1 / team2_odds if team2_odds else None
                
                print(f"\n{team1_name} vs {team2_name}")
                print(f"  AI Prediction: {predicted_team1_score}-{predicted_team2_score}")
                print(f"  Odds: {team1_odds} vs {team2_odds}")
                print(f"  Implied probabilities: {team1_implied_prob:.2%} vs {team2_implied_prob:.2%}")
    
    finally:
        client.close()


def example_custom_filters() -> None:
    """Example: Using custom filters for more specific queries."""
    client = BO3Client()
    
    try:
        # Custom date range
        start_date = datetime(2025, 11, 12)
        end_date = datetime(2025, 11, 19)
        
        matches = client.fetch_matches(
            status=["upcoming"],
            tier=["s"],  # Only S-tier tournaments
            start_date_gte=start_date,
            start_date_lte=end_date,
            include_related=["teams", "tournament", "ai_predictions", "games"]
        )
        
        print(f"Found {len(matches)} S-tier upcoming matches in date range")
    
    finally:
        client.close()


if __name__ == "__main__":
    print("=== Example 1: Fetch Upcoming Week ===")
    example_fetch_upcoming_week()
    
    print("\n=== Example 2: Tournament Whitelist ===")
    example_fetch_with_tournament_whitelist()
    
    print("\n=== Example 3: Matches with Predictions ===")
    example_fetch_matches_with_predictions()
    
    print("\n=== Example 4: Custom Filters ===")
    example_custom_filters()

