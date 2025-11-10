# Data Storage Service

## Purpose

The Data Storage Service provides a centralized PostgreSQL-based persistence layer for CS2 match data from the BO3 API. It stores AI predictions, betting odds, and match results to enable tracking and analysis of prediction accuracy against odds.

## Responsibilities

- **Data Persistence**: Store matches, teams, tournaments from BO3 API
- **AI Prediction Tracking**: Store AI predictions before matches
- **Odds Tracking**: Store betting odds before matches
- **Result Tracking**: Store match results after completion
- **Query Interface**: Provide efficient querying capabilities for analysis
- **Data Integrity**: Ensure ACID properties, referential integrity, and data consistency

## Agent Context Boundaries

This service is a pure data layer:
- **Input**: Data from `data-ingestion` (BO3 API)
- **Output**: Queried data for analysis and tracking
- **No Business Logic**: Only CRUD operations, no analysis or prediction logic
- **No Data Fetching**: Does not fetch data from external APIs

## Technology Stack

- **PostgreSQL**: Primary database for all structured and semi-structured data
- **JSONB**: For flexible nested data (AI predictions, betting odds, games)
- **Alembic**: Database migrations and schema versioning
- **SQLAlchemy**: ORM for Python services (optional, can use raw SQL)

## Database Schema

### Core Tables

#### `data_sources`
Tracks different data ingestion sources (BO3, HLTV, etc.)

```sql
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,  -- 'bo3', 'hltv', 'esl', etc.
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    base_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `teams`
Normalized team information (can come from multiple sources)

```sql
CREATE TABLE teams (
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

CREATE INDEX idx_teams_source ON teams(source_type, source_id);
CREATE INDEX idx_teams_name ON teams(name);
```

#### `tournaments`
Normalized tournament information

```sql
CREATE TABLE tournaments (
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

CREATE INDEX idx_tournaments_source ON tournaments(source_type, source_id);
CREATE INDEX idx_tournaments_tier ON tournaments(tier);
CREATE INDEX idx_tournaments_dates ON tournaments(start_date, end_date);
```

#### `matches`
Core match data (supports multiple sources for same match)

```sql
CREATE TABLE matches (
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

CREATE INDEX idx_matches_source ON matches(source_type, source_id);
CREATE INDEX idx_matches_teams ON matches(team1_id, team2_id);
CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_start_date ON matches(start_date);
CREATE INDEX idx_matches_raw_data ON matches USING GIN(raw_data);  -- For JSONB queries
```

#### `ai_predictions`
AI predictions from BO3 API (or other sources)

```sql
CREATE TABLE ai_predictions (
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

CREATE INDEX idx_ai_predictions_match ON ai_predictions(match_id);
CREATE INDEX idx_ai_predictions_data ON ai_predictions USING GIN(prediction_data);
```

#### `betting_odds`
Betting odds from various providers

```sql
CREATE TABLE betting_odds (
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

CREATE INDEX idx_betting_odds_match ON betting_odds(match_id);
CREATE INDEX idx_betting_odds_provider ON betting_odds(provider);
CREATE INDEX idx_betting_odds_data ON betting_odds USING GIN(odds_data);
```


## Data Flow

1. **Before Match**: Store AI predictions and betting odds from BO3 API
2. **After Match**: Update match with final scores and winner
3. **Analysis**: Query stored data to compare AI predictions vs odds vs actual results

The schema preserves full API responses in JSONB columns while providing normalized tables for efficient querying.

## API Interface

```python
# Example interface (Python)
class StorageService:
    # Match operations
    def save_match(match_data: Dict, source_type: str) -> UUID
    def get_match(match_id: UUID) -> Optional[Dict]
    def get_matches(filters: MatchFilters) -> List[Dict]
    def update_match(match_id: UUID, updates: Dict) -> None  # For updating results
    
    # Team operations
    def get_or_create_team(team_data: Dict, source_type: str) -> UUID
    def get_team_by_source(source_type: str, source_id: int) -> Optional[UUID]
    
    # Tournament operations
    def get_or_create_tournament(tournament_data: Dict, source_type: str) -> UUID
    
    # AI Predictions
    def save_ai_prediction(match_id: UUID, prediction_data: Dict, source_type: str) -> UUID
    def get_ai_predictions(match_id: UUID) -> List[Dict]
    
    # Betting Odds
    def save_betting_odds(match_id: UUID, odds_data: Dict, source_type: str, provider: str) -> UUID
    def get_betting_odds(match_id: UUID, provider: Optional[str] = None) -> List[Dict]
```

## Query Patterns

### Common Queries

```sql
-- Get upcoming matches with AI predictions and odds (for tracking before match)
SELECT m.*, ap.prediction_data, bo.odds_data
FROM matches m
LEFT JOIN ai_predictions ap ON m.id = ap.match_id
LEFT JOIN betting_odds bo ON m.id = bo.match_id
WHERE m.status = 'upcoming'
  AND m.start_date >= NOW()
  AND ap.id IS NOT NULL
ORDER BY m.start_date;

-- Get finished matches with predictions, odds, and results (for analysis)
SELECT 
    m.id,
    m.start_date,
    m.team1_score,
    m.team2_score,
    m.winner_team_id,
    ap.prediction_data,
    bo.odds_data
FROM matches m
LEFT JOIN ai_predictions ap ON m.id = ap.match_id
LEFT JOIN betting_odds bo ON m.id = bo.match_id
WHERE m.status = 'finished'
  AND ap.id IS NOT NULL
ORDER BY m.start_date DESC;

-- Compare AI predictions vs actual results
SELECT 
    m.id,
    ap.prediction_data->>'prediction_winner_team_id' as predicted_winner,
    m.winner_team_id as actual_winner,
    CASE 
        WHEN ap.prediction_data->>'prediction_winner_team_id'::text = m.winner_team_id::text 
        THEN true 
        ELSE false 
    END as prediction_correct
FROM matches m
JOIN ai_predictions ap ON m.id = ap.match_id
WHERE m.status = 'finished';
```

## Setup

1. **Install PostgreSQL** (version 14+ recommended)
2. **Create database**:
   ```sql
   CREATE DATABASE csgo_betting;
   ```
3. **Install dependencies**: `pip install -r requirements.txt`
   - psycopg2 or asyncpg (PostgreSQL driver)
   - SQLAlchemy (optional ORM)
   - Alembic (migrations)
4. **Configure connection** in `config.yaml` or environment variables:
   ```yaml
   database:
     host: localhost
     port: 5432
     database: csgo_betting
     user: postgres
     password: your_password
   ```
5. **Run migrations**: `alembic upgrade head`
6. **Initialize data sources**: Insert BO3 into `data_sources` table

## Performance Considerations

- **Indexing**: All foreign keys and frequently queried fields are indexed
- **JSONB Indexing**: GIN indexes on JSONB columns for efficient nested queries
- **Partitioning**: Consider partitioning `matches` table by date for large datasets
- **Connection Pooling**: Use connection pools (SQLAlchemy, asyncpg) to manage connections
- **Query Optimization**: Use EXPLAIN ANALYZE to optimize slow queries

## Future Enhancements

- **Additional Data Sources**: Support for HLTV, ESL, etc.
- **Caching Layer**: Redis for frequently accessed matches
- **Data Archival**: Archive old matches to separate tables/database
- **Analytics Views**: Pre-computed views for common analysis queries

## Notes

- All timestamps are stored in UTC
- Use UUIDs for primary keys to avoid ID conflicts
- JSONB columns preserve full BO3 API responses while allowing efficient querying
- The schema is designed to track: AI predictions → Odds → Results for analysis

