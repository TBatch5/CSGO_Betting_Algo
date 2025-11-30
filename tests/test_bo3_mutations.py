import unittest
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID
from datetime import datetime
from dataclasses import asdict

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'data-storage'))

# Mock dependencies before importing storage_service
from unittest.mock import MagicMock
import sys

# Mock sqlalchemy
mock_sqlalchemy = MagicMock()
sys.modules["sqlalchemy"] = mock_sqlalchemy
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["sqlalchemy.exc"] = MagicMock()

# Mock config
sys.modules["config"] = MagicMock()

from models import Team, Tournament, Match, AIPrediction, BettingOdds
from mutations.bo3_mutations import BO3Mutation
from storage_service import StorageService

# Mock BO3 models
class MockBO3Team:
    def __init__(self, id, name, slug, country_code, logo_url):
        self.id = id
        self.name = name
        self.slug = slug
        self.country_code = country_code
        self.logo_url = logo_url

class MockBO3Tournament:
    def __init__(self, id, name, slug, tier, tier_rank, prize, discipline_id, status, start_date, end_date):
        self.id = id
        self.name = name
        self.slug = slug
        self.tier = tier
        self.tier_rank = tier_rank
        self.prize = prize
        self.discipline_id = discipline_id
        self.status = status
        self.start_date = start_date
        self.end_date = end_date

class MockBO3Match:
    def __init__(self, id, slug, team1, team2, tournament, status, start_date, bo_type, tier, team1_score, team2_score, winner_team_id, loser_team_id, raw_data=None):
        self.id = id
        self.slug = slug
        self.team1 = team1
        self.team2 = team2
        self.tournament = tournament
        self.status = status
        self.start_date = start_date
        self.bo_type = bo_type
        self.tier = tier
        self.team1_score = team1_score
        self.team2_score = team2_score
        self.winner_team_id = winner_team_id
        self.loser_team_id = loser_team_id
        self.raw_data = raw_data
        
        # Fallback IDs
        self.team1_id = team1.id if team1 else None
        self.team2_id = team2.id if team2 else None
        self.tournament_id = tournament.id if tournament else None

class TestBO3Mutations(unittest.TestCase):
    def setUp(self):
        self.bo3_mutation = BO3Mutation()
        self.mock_team_data = MockBO3Team(1, "Team A", "team-a", "US", "http://logo.url")
        self.mock_tournament_data = MockBO3Tournament(10, "Tourney X", "tourney-x", "S", 1, 100000, 1, "upcoming", datetime.now(), datetime.now())
        
        team2 = MockBO3Team(2, "Team B", "team-b", "CA", "http://logo2.url")
        self.mock_match_data = MockBO3Match(
            100, "match-slug", self.mock_team_data, team2, self.mock_tournament_data,
            "upcoming", datetime.now(), 3, "S", 0, 0, None, None
        )

    def test_to_team(self):
        team = self.bo3_mutation.to_team(self.mock_team_data)
        self.assertIsInstance(team, Team)
        self.assertEqual(team.source_id, 1)
        self.assertEqual(team.name, "Team A")
        self.assertEqual(team.slug, "team-a")
        self.assertEqual(team.country_code, "US")
        self.assertEqual(team.logo_url, "http://logo.url")
        self.assertEqual(team.metadata["id"], 1)

    def test_to_tournament(self):
        tournament = self.bo3_mutation.to_tournament(self.mock_tournament_data)
        self.assertIsInstance(tournament, Tournament)
        self.assertEqual(tournament.source_id, 10)
        self.assertEqual(tournament.name, "Tourney X")
        self.assertEqual(tournament.tier, "S")
        self.assertEqual(tournament.prize_pool, 100000)

    def test_to_match(self):
        match = self.bo3_mutation.to_match(self.mock_match_data)
        self.assertIsInstance(match, Match)
        self.assertEqual(match.source_id, 100)
        self.assertEqual(match.slug, "match-slug")
        self.assertIsInstance(match.team1, Team)
        self.assertEqual(match.team1.name, "Team A")
        self.assertIsInstance(match.team2, Team)
        self.assertEqual(match.team2.name, "Team B")
        self.assertIsInstance(match.tournament, Tournament)
        self.assertEqual(match.tournament.name, "Tourney X")

if __name__ == '__main__':
    unittest.main()
