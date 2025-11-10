"""
Storage service for CS2 betting data.

Provides CRUD operations for matches, teams, tournaments, AI predictions, and betting odds.
Uses mutation framework to convert strongly typed API models to database schema.
"""

from typing import Dict, List, Optional, Any, Type
from uuid import UUID
from datetime import datetime
import logging

from sqlalchemy import create_engine, text, select, update, delete
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

from config import get_database_config
from mutations.base import BaseMutation
from mutations.bo3_mutations import BO3Mutation

logger = logging.getLogger(__name__)


class StorageService:
    """
    Storage service for CS2 betting data.
    
    Provides methods to store and retrieve matches, teams, tournaments,
    AI predictions, and betting odds from PostgreSQL database.
    
    Uses mutation framework to convert strongly typed API models to database schema.
    """
    
    def __init__(
        self,
        database_config: Optional[Any] = None,
        mutation: Optional[BaseMutation] = None
    ) -> None:
        """
        Initialize storage service.
        
        Args:
            database_config: Optional DatabaseConfig instance. If None, loads from environment.
            mutation: Optional mutation instance. If None, defaults to BO3Mutation.
        """
        if database_config is None:
            database_config = get_database_config()
        
        self.config = database_config
        self.engine = create_engine(
            database_config.connection_string,
            pool_pre_ping=True,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        
        # Use provided mutation or default to BO3
        self.mutation = mutation or BO3Mutation()
    
    def _get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    # ============================================================================
    # MATCH OPERATIONS
    # ============================================================================
    
    def save_match(self, match_data: Any) -> UUID:
        """
        Save a match to the database.
        
        Args:
            match_data: Strongly typed match model (e.g., BO3Match)
            
        Returns:
            UUID of the saved match
            
        Raises:
            ValueError: If required fields are missing
            IntegrityError: If match already exists
        """
        with self._get_session() as session:
            try:
                # Convert typed model to database dictionary using mutation
                match_dict = self.mutation.to_match_dict(match_data)
                source_type = match_dict["source_type"]
                source_id = match_dict["source_id"]
                
                # Extract team and tournament data from mutation result
                team1_data = match_dict.pop("_team1", None)
                team2_data = match_dict.pop("_team2", None)
                tournament_data = match_dict.pop("_tournament", None)
                
                if not team1_data or not team2_data:
                    raise ValueError("Match must have team1 and team2 data")
                
                # Create/get teams using mutation
                team1_id = self._get_or_create_team_from_model(team1_data, source_type, session)
                team2_id = self._get_or_create_team_from_model(team2_data, source_type, session)
                
                # Get or create tournament
                tournament_id: Optional[UUID] = None
                if tournament_data:
                    tournament_id = self._get_or_create_tournament_from_model(tournament_data, source_type, session)
                
                # Check if match already exists
                existing = session.execute(
                    text("SELECT id FROM matches WHERE source_type = :source_type AND source_id = :source_id"),
                    {"source_type": source_type, "source_id": source_id}
                ).scalar_one_or_none()
                
                if existing:
                    # Update existing match
                    match_id = UUID(str(existing))
                    self.update_match(match_id, match_dict)
                    return match_id
                
                # Insert new match
                result = session.execute(
                    text("""
                        INSERT INTO matches (
                            source_type, source_id, slug,
                            team1_id, team2_id, tournament_id,
                            status, start_date, bo_type, tier,
                            team1_score, team2_score, winner_team_id, loser_team_id,
                            raw_data, last_fetched_at
                        ) VALUES (
                            :source_type, :source_id, :slug,
                            :team1_id, :team2_id, :tournament_id,
                            :status, :start_date, :bo_type, :tier,
                            :team1_score, :team2_score, :winner_team_id, :loser_team_id,
                            :raw_data, :last_fetched_at
                        ) RETURNING id
                    """),
                    {
                        "source_type": source_type,
                        "source_id": source_id,
                        "slug": match_dict.get("slug"),
                        "team1_id": str(team1_id),
                        "team2_id": str(team2_id),
                        "tournament_id": str(tournament_id) if tournament_id else None,
                        "status": match_dict.get("status", "upcoming"),
                        "start_date": match_dict.get("start_date"),
                        "bo_type": match_dict.get("bo_type"),
                        "tier": match_dict.get("tier"),
                        "team1_score": match_dict.get("team1_score"),
                        "team2_score": match_dict.get("team2_score"),
                        "winner_team_id": str(match_dict.get("winner_team_id")) if match_dict.get("winner_team_id") else None,
                        "loser_team_id": str(match_dict.get("loser_team_id")) if match_dict.get("loser_team_id") else None,
                        "raw_data": match_dict.get("raw_data"),
                        "last_fetched_at": datetime.utcnow(),
                    }
                )
                match_id = UUID(str(result.scalar_one()))
                session.commit()
                logger.info(f"Saved match {match_id} (source: {source_type}, source_id: {source_id})")
                return match_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving match: {e}")
                raise
    
    def get_match(self, match_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get a match by ID.
        
        Args:
            match_id: Match UUID
            
        Returns:
            Match dictionary or None if not found
        """
        with self._get_session() as session:
            result = session.execute(
                text("""
                    SELECT 
                        id, source_type, source_id, slug,
                        team1_id, team2_id, tournament_id,
                        status, start_date, bo_type, tier,
                        team1_score, team2_score, winner_team_id, loser_team_id,
                        raw_data, created_at, updated_at, last_fetched_at
                    FROM matches
                    WHERE id = :match_id
                """),
                {"match_id": str(match_id)}
            ).fetchone()
            
            if not result:
                return None
            
            return {
                "id": str(result[0]),
                "source_type": result[1],
                "source_id": result[2],
                "slug": result[3],
                "team1_id": str(result[4]) if result[4] else None,
                "team2_id": str(result[5]) if result[5] else None,
                "tournament_id": str(result[6]) if result[6] else None,
                "status": result[7],
                "start_date": result[8],
                "bo_type": result[9],
                "tier": result[10],
                "team1_score": result[11],
                "team2_score": result[12],
                "winner_team_id": str(result[13]) if result[13] else None,
                "loser_team_id": str(result[14]) if result[14] else None,
                "raw_data": result[15],
                "created_at": result[16],
                "updated_at": result[17],
                "last_fetched_at": result[18],
            }
    
    def get_matches(
        self,
        status: Optional[str] = None,
        source_type: Optional[str] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get matches with optional filters.
        
        Args:
            status: Filter by match status
            source_type: Filter by source type
            start_date_from: Filter matches starting from this date
            start_date_to: Filter matches starting until this date
            limit: Maximum number of results
            
        Returns:
            List of match dictionaries
        """
        with self._get_session() as session:
            query = """
                SELECT 
                    id, source_type, source_id, slug,
                    team1_id, team2_id, tournament_id,
                    status, start_date, bo_type, tier,
                    team1_score, team2_score, winner_team_id, loser_team_id,
                    raw_data, created_at, updated_at, last_fetched_at
                FROM matches
                WHERE 1=1
            """
            params: Dict[str, Any] = {}
            
            if status:
                query += " AND status = :status"
                params["status"] = status
            
            if source_type:
                query += " AND source_type = :source_type"
                params["source_type"] = source_type
            
            if start_date_from:
                query += " AND start_date >= :start_date_from"
                params["start_date_from"] = start_date_from
            
            if start_date_to:
                query += " AND start_date <= :start_date_to"
                params["start_date_to"] = start_date_to
            
            query += " ORDER BY start_date DESC"
            
            if limit:
                query += " LIMIT :limit"
                params["limit"] = limit
            
            results = session.execute(text(query), params).fetchall()
            
            return [
                {
                    "id": str(r[0]),
                    "source_type": r[1],
                    "source_id": r[2],
                    "slug": r[3],
                    "team1_id": str(r[4]) if r[4] else None,
                    "team2_id": str(r[5]) if r[5] else None,
                    "tournament_id": str(r[6]) if r[6] else None,
                    "status": r[7],
                    "start_date": r[8],
                    "bo_type": r[9],
                    "tier": r[10],
                    "team1_score": r[11],
                    "team2_score": r[12],
                    "winner_team_id": str(r[13]) if r[13] else None,
                    "loser_team_id": str(r[14]) if r[14] else None,
                    "raw_data": r[15],
                    "created_at": r[16],
                    "updated_at": r[17],
                    "last_fetched_at": r[18],
                }
                for r in results
            ]
    
    def update_match(self, match_id: UUID, updates: Dict[str, Any]) -> None:
        """
        Update a match with new data (e.g., after match completion).
        
        Args:
            match_id: Match UUID
            updates: Dictionary of fields to update
        """
        with self._get_session() as session:
            try:
                set_clauses = []
                params: Dict[str, Any] = {"match_id": str(match_id)}
                
                for key, value in updates.items():
                    if key in ["team1_score", "team2_score", "status", "winner_team_id", "loser_team_id"]:
                        set_clauses.append(f"{key} = :{key}")
                        params[key] = value
                    elif key == "raw_data":
                        set_clauses.append("raw_data = :raw_data")
                        params["raw_data"] = value
                
                if not set_clauses:
                    return
                
                set_clauses.append("updated_at = NOW()")
                set_clauses.append("last_fetched_at = NOW()")
                
                query = f"UPDATE matches SET {', '.join(set_clauses)} WHERE id = :match_id"
                session.execute(text(query), params)
                session.commit()
                logger.info(f"Updated match {match_id}")
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating match {match_id}: {e}")
                raise
    
    # ============================================================================
    # TEAM OPERATIONS
    # ============================================================================
    
    def get_or_create_team(self, team_data: Dict[str, Any], source_type: str) -> UUID:
        """
        Get or create a team.
        
        Args:
            team_data: Team data dictionary
            source_type: Source type (e.g., 'bo3')
            
        Returns:
            Team UUID
        """
        with self._get_session() as session:
            return self._get_or_create_team(team_data, source_type, session)
    
    def _get_or_create_team_from_model(
        self,
        team_data: Any,
        source_type: str,
        session: Session
    ) -> UUID:
        """Internal method to get or create team from typed model within a session."""
        # Convert typed model to database dictionary using mutation
        team_dict = self.mutation.to_team_dict(team_data)
        source_id = team_dict["source_id"]
        
        # Check if team exists
        existing = session.execute(
            text("SELECT id FROM teams WHERE source_type = :source_type AND source_id = :source_id"),
            {"source_type": source_type, "source_id": source_id}
        ).scalar_one_or_none()
        
        if existing:
            return UUID(str(existing))
        
        # Create new team
        result = session.execute(
            text("""
                INSERT INTO teams (
                    source_type, source_id, name, slug, country_code, logo_url, metadata
                ) VALUES (
                    :source_type, :source_id, :name, :slug, :country_code, :logo_url, :metadata
                ) RETURNING id
            """),
            team_dict
        )
        team_id = UUID(str(result.scalar_one()))
        session.commit()
        return team_id
    
    def _get_or_create_team(
        self,
        team_data: Dict[str, Any],
        source_type: str,
        session: Session
    ) -> UUID:
        """Internal method to get or create team from dictionary (legacy support)."""
        source_id = team_data.get("id")
        if not source_id:
            raise ValueError("Team data must include 'id' field")
        
        # Check if team exists
        existing = session.execute(
            text("SELECT id FROM teams WHERE source_type = :source_type AND source_id = :source_id"),
            {"source_type": source_type, "source_id": source_id}
        ).scalar_one_or_none()
        
        if existing:
            return UUID(str(existing))
        
        # Create new team
        result = session.execute(
            text("""
                INSERT INTO teams (
                    source_type, source_id, name, slug, country_code, logo_url, metadata
                ) VALUES (
                    :source_type, :source_id, :name, :slug, :country_code, :logo_url, :metadata
                ) RETURNING id
            """),
            {
                "source_type": source_type,
                "source_id": source_id,
                "name": team_data.get("name", ""),
                "slug": team_data.get("slug"),
                "country_code": team_data.get("country_code"),
                "logo_url": team_data.get("logo_url"),
                "metadata": team_data,
            }
        )
        team_id = UUID(str(result.scalar_one()))
        session.commit()
        return team_id
    
    def get_team_by_source(self, source_type: str, source_id: int) -> Optional[UUID]:
        """
        Get team UUID by source type and source ID.
        
        Args:
            source_type: Source type (e.g., 'bo3')
            source_id: Team ID from source
            
        Returns:
            Team UUID or None if not found
        """
        with self._get_session() as session:
            result = session.execute(
                text("SELECT id FROM teams WHERE source_type = :source_type AND source_id = :source_id"),
                {"source_type": source_type, "source_id": source_id}
            ).scalar_one_or_none()
            
            return UUID(str(result)) if result else None
    
    # ============================================================================
    # TOURNAMENT OPERATIONS
    # ============================================================================
    
    def get_or_create_tournament(self, tournament_data: Dict[str, Any], source_type: str) -> UUID:
        """
        Get or create a tournament.
        
        Args:
            tournament_data: Tournament data dictionary
            source_type: Source type (e.g., 'bo3')
            
        Returns:
            Tournament UUID
        """
        with self._get_session() as session:
            return self._get_or_create_tournament(tournament_data, source_type, session)
    
    def _get_or_create_tournament_from_model(
        self,
        tournament_data: Any,
        source_type: str,
        session: Session
    ) -> UUID:
        """Internal method to get or create tournament from typed model within a session."""
        # Convert typed model to database dictionary using mutation
        tournament_dict = self.mutation.to_tournament_dict(tournament_data)
        source_id = tournament_dict["source_id"]
        
        # Check if tournament exists
        existing = session.execute(
            text("SELECT id FROM tournaments WHERE source_type = :source_type AND source_id = :source_id"),
            {"source_type": source_type, "source_id": source_id}
        ).scalar_one_or_none()
        
        if existing:
            return UUID(str(existing))
        
        # Create new tournament
        result = session.execute(
            text("""
                INSERT INTO tournaments (
                    source_type, source_id, name, slug, tier, tier_rank,
                    prize_pool, discipline_id, status, start_date, end_date, metadata
                ) VALUES (
                    :source_type, :source_id, :name, :slug, :tier, :tier_rank,
                    :prize_pool, :discipline_id, :status, :start_date, :end_date, :metadata
                ) RETURNING id
            """),
            tournament_dict
        )
        tournament_id = UUID(str(result.scalar_one()))
        session.commit()
        return tournament_id
    
    def _get_or_create_tournament(
        self,
        tournament_data: Dict[str, Any],
        source_type: str,
        session: Session
    ) -> UUID:
        """Internal method to get or create tournament from dictionary (legacy support)."""
        source_id = tournament_data.get("id")
        if not source_id:
            raise ValueError("Tournament data must include 'id' field")
        
        # Check if tournament exists
        existing = session.execute(
            text("SELECT id FROM tournaments WHERE source_type = :source_type AND source_id = :source_id"),
            {"source_type": source_type, "source_id": source_id}
        ).scalar_one_or_none()
        
        if existing:
            return UUID(str(existing))
        
        # Create new tournament
        result = session.execute(
            text("""
                INSERT INTO tournaments (
                    source_type, source_id, name, slug, tier, tier_rank,
                    prize_pool, discipline_id, status, start_date, end_date, metadata
                ) VALUES (
                    :source_type, :source_id, :name, :slug, :tier, :tier_rank,
                    :prize_pool, :discipline_id, :status, :start_date, :end_date, :metadata
                ) RETURNING id
            """),
            {
                "source_type": source_type,
                "source_id": source_id,
                "name": tournament_data.get("name", ""),
                "slug": tournament_data.get("slug"),
                "tier": tournament_data.get("tier"),
                "tier_rank": tournament_data.get("tier_rank"),
                "prize_pool": tournament_data.get("prize"),
                "discipline_id": tournament_data.get("discipline_id"),
                "status": tournament_data.get("status"),
                "start_date": tournament_data.get("start_date"),
                "end_date": tournament_data.get("end_date"),
                "metadata": tournament_data,
            }
        )
        tournament_id = UUID(str(result.scalar_one()))
        session.commit()
        return tournament_id
    
    # ============================================================================
    # AI PREDICTIONS
    # ============================================================================
    
    def save_ai_prediction(
        self,
        match_id: UUID,
        prediction_data: Any
    ) -> UUID:
        """
        Save AI prediction for a match.
        
        Args:
            match_id: Match UUID
            prediction_data: Strongly typed AI prediction model (e.g., BO3AIPrediction)
            
        Returns:
            Prediction UUID
        """
        with self._get_session() as session:
            try:
                # Convert typed model to database dictionary using mutation
                prediction_dict = self.mutation.to_ai_prediction_dict(prediction_data, match_id)
                source_type = prediction_dict["source_type"]
                source_id = prediction_dict["source_id"]
                
                # Check if prediction already exists
                existing = session.execute(
                    text("SELECT id FROM ai_predictions WHERE match_id = :match_id AND source_type = :source_type"),
                    {"match_id": str(match_id), "source_type": source_type}
                ).scalar_one_or_none()
                
                if existing:
                    # Update existing prediction
                    session.execute(
                        text("""
                            UPDATE ai_predictions
                            SET prediction_data = :prediction_data,
                                source_id = :source_id,
                                updated_at = NOW()
                            WHERE id = :id
                        """),
                        {
                            "id": str(existing),
                            "prediction_data": prediction_dict["prediction_data"],
                            "source_id": source_id,
                        }
                    )
                    session.commit()
                    return UUID(str(existing))
                
                # Insert new prediction
                result = session.execute(
                    text("""
                        INSERT INTO ai_predictions (
                            match_id, source_type, source_id, prediction_data
                        ) VALUES (
                            :match_id, :source_type, :source_id, :prediction_data
                        ) RETURNING id
                    """),
                    prediction_dict
                )
                pred_id = UUID(str(result.scalar_one()))
                session.commit()
                logger.info(f"Saved AI prediction {pred_id} for match {match_id}")
                return pred_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving AI prediction: {e}")
                raise
    
    def get_ai_predictions(self, match_id: UUID) -> List[Dict[str, Any]]:
        """
        Get AI predictions for a match.
        
        Args:
            match_id: Match UUID
            
        Returns:
            List of prediction dictionaries
        """
        with self._get_session() as session:
            results = session.execute(
                text("""
                    SELECT id, source_type, source_id, prediction_data, created_at, updated_at
                    FROM ai_predictions
                    WHERE match_id = :match_id
                """),
                {"match_id": str(match_id)}
            ).fetchall()
            
            return [
                {
                    "id": str(r[0]),
                    "source_type": r[1],
                    "source_id": r[2],
                    "prediction_data": r[3],
                    "created_at": r[4],
                    "updated_at": r[5],
                }
                for r in results
            ]
    
    # ============================================================================
    # BETTING ODDS
    # ============================================================================
    
    def save_betting_odds(
        self,
        match_id: UUID,
        odds_data: Any
    ) -> UUID:
        """
        Save betting odds for a match.
        
        Args:
            match_id: Match UUID
            odds_data: Strongly typed betting odds model (e.g., BO3BettingOdds)
            
        Returns:
            Odds UUID
        """
        with self._get_session() as session:
            try:
                # Convert typed model to database dictionary using mutation
                odds_dict = self.mutation.to_betting_odds_dict(odds_data, match_id)
                source_type = odds_dict["source_type"]
                provider = odds_dict["provider"]
                
                # Check if odds already exist
                existing = session.execute(
                    text("""
                        SELECT id FROM betting_odds
                        WHERE match_id = :match_id AND source_type = :source_type AND provider = :provider
                    """),
                    {"match_id": str(match_id), "source_type": source_type, "provider": provider}
                ).scalar_one_or_none()
                
                if existing:
                    # Update existing odds
                    session.execute(
                        text("""
                            UPDATE betting_odds
                            SET team1_odds = :team1_odds,
                                team2_odds = :team2_odds,
                                team1_implied_prob = :team1_implied_prob,
                                team2_implied_prob = :team2_implied_prob,
                                odds_data = :odds_data,
                                updated_at = NOW(),
                                fetched_at = NOW()
                            WHERE id = :id
                        """),
                        {
                            "id": str(existing),
                            "team1_odds": odds_dict["team1_odds"],
                            "team2_odds": odds_dict["team2_odds"],
                            "team1_implied_prob": odds_dict["team1_implied_prob"],
                            "team2_implied_prob": odds_dict["team2_implied_prob"],
                            "odds_data": odds_dict["odds_data"],
                        }
                    )
                    session.commit()
                    return UUID(str(existing))
                
                # Insert new odds
                result = session.execute(
                    text("""
                        INSERT INTO betting_odds (
                            match_id, source_type, provider,
                            team1_odds, team2_odds,
                            team1_implied_prob, team2_implied_prob,
                            odds_data, fetched_at
                        ) VALUES (
                            :match_id, :source_type, :provider,
                            :team1_odds, :team2_odds,
                            :team1_implied_prob, :team2_implied_prob,
                            :odds_data, NOW()
                        ) RETURNING id
                    """),
                    odds_dict
                )
                odds_id = UUID(str(result.scalar_one()))
                session.commit()
                logger.info(f"Saved betting odds {odds_id} for match {match_id} (provider: {provider})")
                return odds_id
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error saving betting odds: {e}")
                raise
    
    def get_betting_odds(
        self,
        match_id: UUID,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get betting odds for a match.
        
        Args:
            match_id: Match UUID
            provider: Optional provider filter
            
        Returns:
            List of odds dictionaries
        """
        with self._get_session() as session:
            query = """
                SELECT id, source_type, provider,
                       team1_odds, team2_odds,
                       team1_implied_prob, team2_implied_prob,
                       odds_data, created_at, updated_at, fetched_at
                FROM betting_odds
                WHERE match_id = :match_id
            """
            params: Dict[str, Any] = {"match_id": str(match_id)}
            
            if provider:
                query += " AND provider = :provider"
                params["provider"] = provider
            
            results = session.execute(text(query), params).fetchall()
            
            return [
                {
                    "id": str(r[0]),
                    "source_type": r[1],
                    "provider": r[2],
                    "team1_odds": float(r[3]) if r[3] else None,
                    "team2_odds": float(r[4]) if r[4] else None,
                    "team1_implied_prob": float(r[5]) if r[5] else None,
                    "team2_implied_prob": float(r[6]) if r[6] else None,
                    "odds_data": r[7],
                    "created_at": r[8],
                    "updated_at": r[9],
                    "fetched_at": r[10],
                }
                for r in results
            ]

