"""
BO3 API Client for fetching CS2 match data with AI predictions.

This client is designed to fetch match data from the BO3 API, specifically
focusing on upcoming matches with AI predictions and betting odds for
Method 1 implementation.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from urllib.parse import urlencode
import time
import logging

logger = logging.getLogger(__name__)


class BO3Client:
    """
    Client for interacting with the BO3 API.
    
    Handles fetching matches, AI predictions, betting odds, and tournament data.
    """
    
    BASE_URL = "https://api.bo3.gg/api/v1"
    CS2_DISCIPLINE_ID = 1  # CS2 discipline ID
    DEFAULT_PAGE_LIMIT = 50
    DEFAULT_RETRY_DELAY = 1  # seconds
    DEFAULT_MAX_RETRIES = 3
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        rate_limit_delay: float = 0.5,
        max_retries: int = DEFAULT_MAX_RETRIES
    ):
        """
        Initialize the BO3 API client.
        
        Args:
            base_url: Override base URL (defaults to production API)
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests to respect rate limits
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "CS2-Betting-MVP/1.0"
        })
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict:
        """
        Make a request to the BO3 API with retry logic.
        
        Args:
            endpoint: API endpoint (e.g., '/matches')
            params: Query parameters
            retry_count: Current retry attempt
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Rate limiting delay
            if retry_count == 0:
                time.sleep(self.rate_limit_delay)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                if retry_count < self.max_retries:
                    wait_time = self.DEFAULT_RETRY_DELAY * (2 ** retry_count)
                    logger.warning(f"Rate limited. Retrying after {wait_time}s...")
                    time.sleep(wait_time)
                    return self._make_request(endpoint, params, retry_count + 1)
                else:
                    logger.error("Max retries reached for rate limiting")
                    raise
            
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise
            
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                wait_time = self.DEFAULT_RETRY_DELAY * (2 ** retry_count)
                logger.warning(f"Request failed. Retrying after {wait_time}s...")
                time.sleep(wait_time)
                return self._make_request(endpoint, params, retry_count + 1)
            else:
                logger.error(f"Request failed after {self.max_retries} retries: {e}")
                raise
    
    def _build_match_params(
        self,
        status: List[str] = None,
        tier: List[str] = None,
        tournament_ids: Optional[List[int]] = None,
        start_date_gte: Optional[datetime] = None,
        start_date_lte: Optional[datetime] = None,
        include_related: List[str] = None,
        sort: str = "start_date",
        page_offset: int = 0,
        page_limit: int = DEFAULT_PAGE_LIMIT
    ) -> Dict:
        """
        Build query parameters for matches endpoint.
        
        Args:
            status: Match statuses to filter (e.g., ['upcoming', 'current'])
            tier: Tournament tiers to filter (e.g., ['s', 'a'])
            tournament_ids: Whitelist of tournament IDs
            start_date_gte: Matches starting on or after this date
            start_date_lte: Matches starting on or before this date
            include_related: Related resources to include (e.g., ['teams', 'tournament', 'ai_predictions'])
            sort: Field to sort by
            page_offset: Pagination offset
            page_limit: Results per page
            
        Returns:
            Dictionary of query parameters
        """
        params = {
            "page[offset]": page_offset,
            "page[limit]": page_limit,
            "sort": sort,
            "filter[matches.discipline_id][eq]": str(self.CS2_DISCIPLINE_ID),
            "filter[matches.team1_id][not_eq_null]": "",
            "filter[matches.team2_id][not_eq_null]": "",
        }
        
        if status:
            params["filter[matches.status][in]"] = ",".join(status)
        
        if tier:
            params["filter[matches.tier][in]"] = ",".join(tier)
        
        if tournament_ids:
            params["filter[matches.tournament_id][in]"] = ",".join(map(str, tournament_ids))
        
        if start_date_gte:
            params["filter[matches.start_date][gte]"] = start_date_gte.isoformat() + "Z"
        
        if start_date_lte:
            params["filter[matches.start_date][lte]"] = start_date_lte.isoformat() + "Z"
        
        if include_related:
            params["with"] = ",".join(include_related)
        
        return params
    
    def fetch_matches(
        self,
        status: List[str] = None,
        tier: List[str] = None,
        tournament_ids: Optional[List[int]] = None,
        start_date_gte: Optional[datetime] = None,
        start_date_lte: Optional[datetime] = None,
        include_related: List[str] = None,
        fetch_all_pages: bool = True
    ) -> List[Dict]:
        """
        Fetch matches from the BO3 API.
        
        Args:
            status: Match statuses to filter (default: ['upcoming', 'current'])
            tier: Tournament tiers to filter (default: ['s', 'a'])
            tournament_ids: Whitelist of tournament IDs (optional)
            start_date_gte: Matches starting on or after this date
            start_date_lte: Matches starting on or before this date
            include_related: Related resources to include
                (default: ['teams', 'tournament', 'ai_predictions', 'games'])
            fetch_all_pages: Whether to fetch all pages or just the first
            
        Returns:
            List of match dictionaries
        """
        if status is None:
            status = ["upcoming", "current"]
        
        if tier is None:
            tier = ["s", "a"]
        
        if include_related is None:
            include_related = ["teams", "tournament", "ai_predictions", "games"]
        
        all_matches = []
        offset = 0
        
        while True:
            params = self._build_match_params(
                status=status,
                tier=tier,
                tournament_ids=tournament_ids,
                start_date_gte=start_date_gte,
                start_date_lte=start_date_lte,
                include_related=include_related,
                page_offset=offset
            )
            
            response = self._make_request("/matches", params=params)
            
            matches = response.get("results", [])
            all_matches.extend(matches)
            
            # Check if more pages exist
            total = response.get("total", {})
            total_count = total.get("count", 0)
            current_limit = total.get("limit", self.DEFAULT_PAGE_LIMIT)
            
            if not fetch_all_pages or offset + current_limit >= total_count:
                break
            
            offset += current_limit
            
            # Safety check to prevent infinite loops
            if len(matches) == 0:
                break
        
        logger.info(f"Fetched {len(all_matches)} matches")
        return all_matches
    
    def fetch_upcoming_week_matches(
        self,
        days_ahead: int = 7,
        tier: List[str] = None,
        tournament_ids: Optional[List[int]] = None,
        include_related: List[str] = None
    ) -> List[Dict]:
        """
        Fetch all upcoming matches for the next N days.
        
        Args:
            days_ahead: Number of days ahead to fetch (default: 7)
            tier: Tournament tiers to filter (default: ['s', 'a'])
            tournament_ids: Whitelist of tournament IDs (optional)
            include_related: Related resources to include
            
        Returns:
            List of match dictionaries
        """
        now = datetime.utcnow()
        week_end = now + timedelta(days=days_ahead)
        
        logger.info(f"Fetching matches from {now.isoformat()} to {week_end.isoformat()}")
        
        return self.fetch_matches(
            status=["upcoming", "current"],
            tier=tier,
            tournament_ids=tournament_ids,
            start_date_gte=now,
            start_date_lte=week_end,
            include_related=include_related
        )
    
    def fetch_match_by_id(
        self,
        match_id: int,
        include_related: List[str] = None
    ) -> Optional[Dict]:
        """
        Fetch a specific match by ID.
        
        Args:
            match_id: Match ID
            include_related: Related resources to include
            
        Returns:
            Match dictionary or None if not found
        """
        if include_related is None:
            include_related = ["teams", "tournament", "ai_predictions", "games"]
        
        params = {}
        if include_related:
            params["with"] = ",".join(include_related)
        
        try:
            response = self._make_request(f"/matches/{match_id}", params=params)
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Match {match_id} not found")
                return None
            raise
    
    def extract_ai_predictions(self, match: Dict) -> Optional[Dict]:
        """
        Extract AI predictions from a match object.
        
        Args:
            match: Match dictionary from API response
            
        Returns:
            AI predictions dictionary or None if not available
        """
        return match.get("ai_predictions")
    
    def extract_betting_odds(self, match: Dict) -> Optional[Dict]:
        """
        Extract betting odds from a match object.
        
        Args:
            match: Match dictionary from API response
            
        Returns:
            Betting odds dictionary or None if not available
        """
        return match.get("bet_updates")
    
    def extract_tournament_info(self, match: Dict) -> Optional[Dict]:
        """
        Extract tournament information from a match object.
        
        Args:
            match: Match dictionary from API response
            
        Returns:
            Tournament dictionary or None if not available
        """
        return match.get("tournament")
    
    def get_matches_with_predictions(
        self,
        days_ahead: int = 7,
        tier: List[str] = None,
        tournament_ids: Optional[List[int]] = None,
        require_odds: bool = False
    ) -> List[Dict]:
        """
        Fetch upcoming matches that have AI predictions (and optionally odds).
        
        This is a convenience method for Method 1 implementation.
        
        Args:
            days_ahead: Number of days ahead to fetch
            tier: Tournament tiers to filter
            tournament_ids: Whitelist of tournament IDs
            require_odds: Whether to only return matches with betting odds
            
        Returns:
            List of matches with AI predictions
        """
        matches = self.fetch_upcoming_week_matches(
            days_ahead=days_ahead,
            tier=tier,
            tournament_ids=tournament_ids
        )
        
        filtered = []
        for match in matches:
            if match.get("ai_predictions") is None:
                continue
            
            if require_odds and match.get("bet_updates") is None:
                continue
            
            filtered.append(match)
        
        logger.info(f"Found {len(filtered)} matches with AI predictions (odds required: {require_odds})")
        return filtered
    
    def get_unique_tournaments(self, matches: List[Dict]) -> Set[int]:
        """
        Extract unique tournament IDs from a list of matches.
        
        Args:
            matches: List of match dictionaries
            
        Returns:
            Set of tournament IDs
        """
        tournament_ids = set()
        for match in matches:
            tournament = match.get("tournament")
            if tournament and tournament.get("id"):
                tournament_ids.add(tournament["id"])
        return tournament_ids
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()

