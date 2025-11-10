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
- **Input**: Data from `data-ingestion` (BO3 API) - **strongly typed models**
- **Output**: Queried data for analysis and tracking
- **No Business Logic**: Only CRUD operations, no analysis or prediction logic
- **No Data Fetching**: Does not fetch data from external APIs

## Architecture

### Mutation Framework

The storage service uses a **mutation framework** to convert strongly typed API response models (from `data-ingestion`) into database-ready dictionaries. This provides:

- **Type Safety**: Strongly typed models from data-ingestion ensure data integrity
- **Separation of Concerns**: API models are separate from database schema
- **Extensibility**: Easy to add new data sources by creating new mutation classes
- **Standardization**: Consistent conversion pattern across all data sources

**Location**: `mutations/` directory

**Base Interface**: `mutations/base.py` - `BaseMutation` abstract class

**BO3 Implementation**: `mutations/bo3_mutations.py` - `BO3Mutation` class

### Adding a New Data Source

1. Create typed models in `data-ingestion/{source}/models.py`
2. Create mutation class in `data-storage/mutations/{source}_mutations.py` extending `BaseMutation`
3. Implement conversion methods: `to_team_dict`, `to_tournament_dict`, `to_match_dict`, etc.
4. Use the mutation when initializing `StorageService`

## Technology Stack

- **PostgreSQL**: Primary database for all structured and semi-structured data
- **JSONB**: For flexible nested data (AI predictions, betting odds, games)
- **Alembic**: Database migrations and schema versioning
- **SQLAlchemy**: ORM for Python services (optional, can use raw SQL)

## Database Schema

The complete database schema is defined in `schema.sql` with detailed documentation using PostgreSQL's `COMMENT ON` functionality. The schema includes:

- **`data_sources`**: Tracks different data ingestion sources (BO3, HLTV, etc.)
- **`teams`**: Normalized team information
- **`tournaments`**: Normalized tournament information
- **`matches`**: Core match data with team and tournament references
- **`ai_predictions`**: AI predictions from BO3 API stored as JSONB
- **`betting_odds`**: Betting odds from various providers with extracted key fields

To view the schema documentation, run:
```sql
\d+ table_name  -- In psql to see table structure and comments
```

Or query the PostgreSQL system catalogs:
```sql
SELECT 
    obj_description('table_name'::regclass, 'pg_class') as table_comment,
    col_description('table_name'::regclass, column_number) as column_comment
FROM information_schema.columns
WHERE table_name = 'table_name';
```

See `schema.sql` for the complete schema definition with all documentation.

## Data Flow

1. **Before Match**: Store AI predictions and betting odds from BO3 API (as strongly typed models)
2. **After Match**: Update match with final scores and winner
3. **Analysis**: Query stored data to compare AI predictions vs odds vs actual results

The mutation framework converts strongly typed API models to database schema format, preserving full API responses in JSONB columns while providing normalized tables for efficient querying.

## API Interface

```python
from storage_service import StorageService
from data_ingestion.bo3_api.models import BO3Match, BO3AIPrediction, BO3BettingOdds

# Initialize service (uses BO3Mutation by default)
storage = StorageService()

# Save a match from BO3 API (strongly typed)
match_id = storage.save_match(bo3_match_model)  # BO3Match instance

# Save AI prediction (strongly typed)
prediction_id = storage.save_ai_prediction(match_id, bo3_prediction_model)  # BO3AIPrediction instance

# Save betting odds (strongly typed)
odds_id = storage.save_betting_odds(match_id, bo3_odds_model)  # BO3BettingOdds instance

# Update match with results after completion
storage.update_match(match_id, {
    'status': 'finished',
    'team1_score': 2,
    'team2_score': 0,
    'winner_team_id': team1_id
})

# Query matches
upcoming_matches = storage.get_matches(status='upcoming', limit=10)
finished_matches = storage.get_matches(status='finished', limit=10)
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

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure connection** using environment variables:
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env with your database credentials
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=csgo_betting
   DB_USER=postgres
   DB_PASSWORD=your_password
   ```

5. **Run migrations**:
   ```bash
   alembic upgrade head
   ```
   This will create all tables with the schema defined in `schema.sql`.

6. **Initialize data sources** (optional):
   ```sql
   INSERT INTO data_sources (name, display_name, description, base_url, is_active)
   VALUES ('bo3', 'BO3 API', 'BO3 API for CS2 match data', 'https://api.bo3.gg/api/v1', true);
   ```

## Usage

```python
from storage_service import StorageService
from data_ingestion.bo3_api.models import BO3Match, BO3AIPrediction, BO3BettingOdds

# Initialize service (loads config from environment, uses BO3Mutation by default)
storage = StorageService()

# Save a match from BO3 API (strongly typed model)
match_id = storage.save_match(bo3_match_model)

# Save AI prediction (strongly typed model)
prediction_id = storage.save_ai_prediction(match_id, bo3_prediction_model)

# Save betting odds (strongly typed model)
odds_id = storage.save_betting_odds(match_id, bo3_odds_model)

# Update match with results after completion
storage.update_match(match_id, {
    'status': 'finished',
    'team1_score': 2,
    'team2_score': 0,
    'winner_team_id': team1_id
})

# Query matches
upcoming_matches = storage.get_matches(status='upcoming', limit=10)
finished_matches = storage.get_matches(status='finished', limit=10)
```

## Performance Considerations

- **Indexing**: All foreign keys and frequently queried fields are indexed
- **JSONB Indexing**: GIN indexes on JSONB columns for efficient nested queries
- **Partitioning**: Consider partitioning `matches` table by date for large datasets
- **Connection Pooling**: Use connection pools (SQLAlchemy, asyncpg) to manage connections
- **Query Optimization**: Use EXPLAIN ANALYZE to optimize slow queries

## Future Enhancements

- **Additional Data Sources**: Support for HLTV, ESL, etc. (via mutation framework)
- **Caching Layer**: Redis for frequently accessed matches
- **Data Archival**: Archive old matches to separate tables/database
- **Analytics Views**: Pre-computed views for common analysis queries

## Notes

- All timestamps are stored in UTC
- Use UUIDs for primary keys to avoid ID conflicts
- JSONB columns preserve full BO3 API responses while allowing efficient querying
- The schema is designed to track: AI predictions → Odds → Results for analysis
- **Strongly typed models** from `data-ingestion` ensure type safety and data integrity
- **Mutation framework** provides standardized conversion from API models to database schema
