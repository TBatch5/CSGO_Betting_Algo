#!/usr/bin/env python3
"""
BO3 Data Ingestion Script

Fetches CS2 match data from BO3 API and stores it in the database.
Includes matches, teams, tournaments, AI predictions, and betting odds.
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import os
from dotenv import load_dotenv

# Add bo3-api to path
bo3_api_path = Path(__file__).parent / 'bo3-api'
sys.path.insert(0, str(bo3_api_path))

# Add data-storage to path
data_storage_path = Path(__file__).parent.parent / 'data-storage'
sys.path.insert(0, str(data_storage_path))

from bo3_client import BO3Client
from storage_service import StorageService
from mutations.bo3_mutations import BO3Mutation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BO3DataIngestion:
    """
    Orchestrates fetching data from BO3 API and storing it in the database.
    """
    
    def __init__(
        self,
        bo3_client: Optional[BO3Client] = None,
        storage_service: Optional[StorageService] = None,
        dry_run: bool = False
    ):
        """
        Initialize the data ingestion pipeline.
        
        Args:
            bo3_client: BO3 API client (creates default if None)
            storage_service: Storage service (creates default if None)
            dry_run: If True, fetch data but don't save to database
        """
        self.bo3_client = bo3_client or BO3Client()
        self.storage_service = storage_service or StorageService(mutation=BO3Mutation())
        self.dry_run = dry_run
        
        self.stats = {
            'matches_fetched': 0,
            'matches_saved': 0,
            'teams_saved': 0,
            'tournaments_saved': 0,
            'predictions_saved': 0,
            'odds_saved': 0,
            'errors': 0
        }
    
    def ingest_upcoming_matches(
        self,
        days_ahead: int = 7,
        tier: Optional[List[str]] = None,
        require_predictions: bool = True,
        require_odds: bool = False
    ) -> None:
        """
        Fetch and store upcoming matches.
        
        Args:
            days_ahead: Number of days ahead to fetch matches
            tier: Tournament tiers to filter (default: ['s', 'a'])
            require_predictions: Only process matches with AI predictions
            require_odds: Only process matches with betting odds
        """
        logger.info(f"Starting data ingestion for next {days_ahead} days")
        logger.info(f"Filters - Tier: {tier}, Require predictions: {require_predictions}, Require odds: {require_odds}")
        
        if self.dry_run:
            logger.info("DRY RUN MODE - No data will be saved to database")
        
        try:
            # Fetch matches from BO3 API
            if require_predictions:
                matches = self.bo3_client.get_matches_with_predictions(
                    days_ahead=days_ahead,
                    tier=tier,
                    require_odds=require_odds
                )
            else:
                matches = self.bo3_client.fetch_upcoming_week_matches(
                    days_ahead=days_ahead,
                    tier=tier
                )
            
            self.stats['matches_fetched'] = len(matches)
            logger.info(f"Fetched {len(matches)} matches from BO3 API")
            
            if not matches:
                logger.warning("No matches found matching the criteria")
                return
            
            # Process each match
            for i, match in enumerate(matches, 1):
                logger.info(f"Processing match {i}/{len(matches)}: {match.slug or match.id}")
                
                try:
                    self._process_match(match)
                except Exception as e:
                    logger.error(f"Error processing match {match.id}: {e}", exc_info=True)
                    self.stats['errors'] += 1
                    continue
            
            # Log final statistics
            self._log_statistics()
            
        except Exception as e:
            logger.error(f"Fatal error during ingestion: {e}", exc_info=True)
            raise
        finally:
            self.bo3_client.close()
    
    def _process_match(self, match) -> None:
        """
        Process a single match and store it in the database.
        
        Args:
            match: BO3Match object
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would save match: {match.slug or match.id}")
            logger.info(f"  - Team 1: {match.team1.name if match.team1 else 'Unknown'}")
            logger.info(f"  - Team 2: {match.team2.name if match.team2 else 'Unknown'}")
            logger.info(f"  - Tournament: {match.tournament.name if match.tournament else 'Unknown'}")
            logger.info(f"  - Has AI Prediction: {match.ai_predictions is not None}")
            logger.info(f"  - Has Betting Odds: {match.bet_updates is not None}")
            self.stats['matches_saved'] += 1
            return
        
        try:
            # Save the match (this will also save teams and tournament via relationships)
            match_id = self.storage_service.save_match(match)
            self.stats['matches_saved'] += 1
            logger.info(f"Saved match {match.id} with UUID {match_id}")
            
            # Save AI predictions if available
            if match.ai_predictions:
                try:
                    prediction_id = self.storage_service.save_ai_prediction(
                        match_id=match_id,
                        prediction_data=match.ai_predictions
                    )
                    self.stats['predictions_saved'] += 1
                    logger.info(f"Saved AI prediction {prediction_id} for match {match_id}")
                except Exception as e:
                    logger.error(f"Error saving AI prediction for match {match.id}: {e}")
                    self.stats['errors'] += 1
            
            # Save betting odds if available
            if match.bet_updates:
                try:
                    odds_id = self.storage_service.save_betting_odds(
                        match_id=match_id,
                        odds_data=match.bet_updates
                    )
                    self.stats['odds_saved'] += 1
                    logger.info(f"Saved betting odds {odds_id} for match {match_id}")
                except Exception as e:
                    logger.error(f"Error saving betting odds for match {match.id}: {e}")
                    self.stats['errors'] += 1
                    
        except Exception as e:
            logger.error(f"Error saving match {match.id}: {e}")
            self.stats['errors'] += 1
            raise
    
    def _log_statistics(self) -> None:
        """Log final ingestion statistics."""
        logger.info("=" * 60)
        logger.info("INGESTION STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Matches fetched:      {self.stats['matches_fetched']}")
        logger.info(f"Matches saved:        {self.stats['matches_saved']}")
        logger.info(f"Predictions saved:    {self.stats['predictions_saved']}")
        logger.info(f"Odds saved:           {self.stats['odds_saved']}")
        logger.info(f"Errors encountered:   {self.stats['errors']}")
        logger.info("=" * 60)


def main():
    """Main entry point for the ingestion script."""
    parser = argparse.ArgumentParser(
        description='Ingest CS2 match data from BO3 API into database'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days ahead to fetch matches (default: 7)'
    )
    
    parser.add_argument(
        '--tier',
        nargs='+',
        default=['s', 'a'],
        help='Tournament tiers to filter (default: s a)'
    )
    
    parser.add_argument(
        '--require-predictions',
        action='store_true',
        default=True,
        help='Only fetch matches with AI predictions (default: True)'
    )
    
    parser.add_argument(
        '--no-require-predictions',
        dest='require_predictions',
        action='store_false',
        help='Fetch all matches regardless of AI predictions'
    )
    
    parser.add_argument(
        '--require-odds',
        action='store_true',
        default=tournament,
        help='Only fetch matches with betting odds (default: False)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch data but do not save to database'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load environment variables
    load_dotenv()
    
    # Verify database connection is configured
    if not args.dry_run:
        required_env_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please set these in your .env file or environment")
            sys.exit(1)
    
    # Create ingestion pipeline
    ingestion = BO3DataIngestion(dry_run=args.dry_run)
    
    # Run ingestion
    try:
        ingestion.ingest_upcoming_matches(
            days_ahead=args.days,
            tier=args.tier,
            require_predictions=args.require_predictions,
            require_odds=args.require_odds
        )
        logger.info("Ingestion completed successfully")
    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
