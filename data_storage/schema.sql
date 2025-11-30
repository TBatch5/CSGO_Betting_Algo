-- CS2 Betting Data Storage Schema
-- PostgreSQL schema for storing BO3 API data: matches, teams, tournaments, AI predictions, and betting odds

-- ============================================================================
-- DATA SOURCES
-- ============================================================================

COMMENT ON SCHEMA public IS 'CS2 Betting data storage schema for tracking matches, predictions, and odds from BO3 API';

-- Tracks different data ingestion sources (BO3, HLTV, etc.)
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,  -- 'bo3', 'hltv', 'esl', etc.
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    base_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE data_sources IS 'Tracks different data ingestion sources (BO3, HLTV, etc.)';
COMMENT ON COLUMN data_sources.name IS 'Unique identifier for the data source (e.g., ''bo3'', ''hltv'')';
COMMENT ON COLUMN data_sources.display_name IS 'Human-readable name for the data source';
COMMENT ON COLUMN data_sources.base_url IS 'Base URL of the data source API';
COMMENT ON COLUMN data_sources.is_active IS 'Whether this data source is currently active';

-- ============================================================================
-- TEAMS
-- ============================================================================

-- Normalized team information (can come from multiple sources)
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL,  -- 'bo3', 'hltv', etc.
    source_id INTEGER NOT NULL,       -- ID from the source system
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255),
    country_code CHAR(2),
    logo_url VARCHAR(500),
    metadata JSONB,                    -- Additional source-specific data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_type, source_id)
);

COMMENT ON TABLE teams IS 'Normalized team information (can come from multiple sources)';
COMMENT ON COLUMN teams.source_type IS 'Data source type (e.g., ''bo3'', ''hltv'')';
COMMENT ON COLUMN teams.source_id IS 'Team ID from the source system';
COMMENT ON COLUMN teams.metadata IS 'Additional source-specific team data stored as JSONB';

CREATE INDEX idx_teams_source ON teams(source_type, source_id);
CREATE INDEX idx_teams_name ON teams(name);

-- ============================================================================
-- TOURNAMENTS
-- ============================================================================

-- Normalized tournament information
CREATE TABLE IF NOT EXISTS tournaments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL,
    source_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255),
    tier VARCHAR(10),                   -- 's', 'a', 'b', etc.
    tier_rank INTEGER,
    prize_pool INTEGER,
    discipline_id INTEGER,
    status VARCHAR(50),                 -- 'upcoming', 'current', 'finished'
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_type, source_id)
);

COMMENT ON TABLE tournaments IS 'Normalized tournament information';
COMMENT ON COLUMN tournaments.source_type IS 'Data source type (e.g., ''bo3'', ''hltv'')';
COMMENT ON COLUMN tournaments.source_id IS 'Tournament ID from the source system';
COMMENT ON COLUMN tournaments.tier IS 'Tournament tier: ''s'' (S-tier), ''a'' (A-tier), ''b'' (B-tier), etc.';
COMMENT ON COLUMN tournaments.status IS 'Tournament status: ''upcoming'', ''current'', ''finished''';
COMMENT ON COLUMN tournaments.metadata IS 'Additional source-specific tournament data stored as JSONB';

CREATE INDEX idx_tournaments_source ON tournaments(source_type, source_id);
CREATE INDEX idx_tournaments_tier ON tournaments(tier);
CREATE INDEX idx_tournaments_dates ON tournaments(start_date, end_date);

-- ============================================================================
-- MATCHES
-- ============================================================================

-- Core match data (supports multiple sources for same match)
CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL,   -- 'bo3', 'hltv', etc.
    source_id INTEGER NOT NULL,         -- Match ID from source
    slug VARCHAR(255),
    
    -- Team references
    team1_id UUID REFERENCES teams(id),
    team2_id UUID REFERENCES teams(id),
    
    -- Tournament reference
    tournament_id UUID REFERENCES tournaments(id),
    
    -- Match details
    status VARCHAR(50) NOT NULL,        -- 'upcoming', 'current', 'finished'
    start_date TIMESTAMP,
    bo_type INTEGER,                    -- Best-of format (1, 3, 5)
    tier VARCHAR(10),
    
    -- Scores (null for upcoming matches)
    team1_score INTEGER,
    team2_score INTEGER,
    winner_team_id UUID REFERENCES teams(id),
    loser_team_id UUID REFERENCES teams(id),
    
    -- Source-specific raw data (preserve full API response)
    raw_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_fetched_at TIMESTAMP,          -- Track when data was last updated from source
    
    UNIQUE(source_type, source_id)
);

COMMENT ON TABLE matches IS 'Core match data (supports multiple sources for same match)';
COMMENT ON COLUMN matches.source_type IS 'Data source type (e.g., ''bo3'', ''hltv'')';
COMMENT ON COLUMN matches.source_id IS 'Match ID from the source system';
COMMENT ON COLUMN matches.status IS 'Match status: ''upcoming'', ''current'', ''finished''';
COMMENT ON COLUMN matches.bo_type IS 'Best-of format: 1 (BO1), 3 (BO3), 5 (BO5)';
COMMENT ON COLUMN matches.team1_score IS 'Final score for team 1 (null for upcoming matches)';
COMMENT ON COLUMN matches.team2_score IS 'Final score for team 2 (null for upcoming matches)';
COMMENT ON COLUMN matches.raw_data IS 'Full API response preserved as JSONB for future use';
COMMENT ON COLUMN matches.last_fetched_at IS 'Timestamp when data was last updated from source';

CREATE INDEX idx_matches_source ON matches(source_type, source_id);
CREATE INDEX idx_matches_teams ON matches(team1_id, team2_id);
CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_start_date ON matches(start_date);
CREATE INDEX idx_matches_raw_data ON matches USING GIN(raw_data);  -- For JSONB queries

-- ============================================================================
-- AI PREDICTIONS
-- ============================================================================

-- AI predictions from BO3 API (or other sources)
CREATE TABLE IF NOT EXISTS ai_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,   -- 'bo3', etc.
    source_id INTEGER,                  -- Prediction ID from source
    
    -- Full prediction data (preserve all details)
    prediction_data JSONB NOT NULL,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(match_id, source_type)
);

COMMENT ON TABLE ai_predictions IS 'AI predictions from BO3 API (or other sources)';
COMMENT ON COLUMN ai_predictions.match_id IS 'Reference to the match this prediction is for';
COMMENT ON COLUMN ai_predictions.source_type IS 'Data source type (e.g., ''bo3'')';
COMMENT ON COLUMN ai_predictions.source_id IS 'Prediction ID from the source system';
COMMENT ON COLUMN ai_predictions.prediction_data IS 'Full AI prediction data from BO3 API, including prediction_winner_team_id, prediction_team1_score, prediction_team2_score, prediction_scores_data with proximity_factors, etc.';

CREATE INDEX idx_ai_predictions_match ON ai_predictions(match_id);
CREATE INDEX idx_ai_predictions_data ON ai_predictions USING GIN(prediction_data);

-- ============================================================================
-- BETTING ODDS
-- ============================================================================

-- Betting odds from various providers
CREATE TABLE IF NOT EXISTS betting_odds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id UUID NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,   -- 'bo3', etc.
    provider VARCHAR(100) NOT NULL,      -- '1xbit', 'bet365', etc.
    
    -- Extracted key fields
    team1_odds DECIMAL(10,2),
    team2_odds DECIMAL(10,2),
    team1_implied_prob DECIMAL(5,4),    -- Calculated: 1 / odds
    team2_implied_prob DECIMAL(5,4),
    
    -- Full odds data (includes additional_markets, etc.)
    odds_data JSONB NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    fetched_at TIMESTAMP,                -- When odds were fetched
    
    UNIQUE(match_id, source_type, provider)
);

COMMENT ON TABLE betting_odds IS 'Betting odds from various providers';
COMMENT ON COLUMN betting_odds.match_id IS 'Reference to the match these odds are for';
COMMENT ON COLUMN betting_odds.source_type IS 'Data source type (e.g., ''bo3'')';
COMMENT ON COLUMN betting_odds.provider IS 'Odds provider name (e.g., ''1xbit'', ''bet365'')';
COMMENT ON COLUMN betting_odds.team1_odds IS 'Decimal odds for team 1 (extracted from odds_data)';
COMMENT ON COLUMN betting_odds.team2_odds IS 'Decimal odds for team 2 (extracted from odds_data)';
COMMENT ON COLUMN betting_odds.team1_implied_prob IS 'Implied probability for team 1 (calculated as 1 / team1_odds)';
COMMENT ON COLUMN betting_odds.team2_implied_prob IS 'Implied probability for team 2 (calculated as 1 / team2_odds)';
COMMENT ON COLUMN betting_odds.odds_data IS 'Full betting odds data from BO3 API, including team_1/team_2 objects with coeff, aggrement_score, additional_markets, etc.';
COMMENT ON COLUMN betting_odds.fetched_at IS 'Timestamp when odds were fetched from the source';

CREATE INDEX idx_betting_odds_match ON betting_odds(match_id);
CREATE INDEX idx_betting_odds_provider ON betting_odds(provider);
CREATE INDEX idx_betting_odds_data ON betting_odds USING GIN(odds_data);

