# Data Storage Service

## Purpose

The Data Storage Service provides a centralized persistence layer for all CS2 match data, features, and model artifacts. It abstracts database operations and provides a clean API for other services.

## Responsibilities

- **Data Persistence**: Store matches, teams, players, and related data
- **Feature Storage**: Store engineered features for model training
- **Model Artifact Storage**: Store trained models, metadata, and versions
- **Query Interface**: Provide efficient querying capabilities for other services
- **Data Integrity**: Ensure ACID properties, backups, and data consistency

## Agent Context Boundaries

This service is a pure data layer:
- **Input**: Data from `data-ingestion`, features from `feature-engineering`, models from `model-training`
- **Output**: Queried data to all consuming services
- **No Business Logic**: Only CRUD operations, no ML or prediction logic

## Key Components

### 1. Database Layer
- **PostgreSQL**: Primary database for structured data
  - Tables: matches, teams, players, features, model_metadata
- **Redis**: Caching layer for frequently accessed data
- **Object Storage** (S3/MinIO): For large model artifacts

### 2. Repository Pattern
- Abstract data access logic
- Provide clean interfaces for each entity type
- Handle connection pooling and transactions

### 3. Schema Management
- Database migrations (Alembic, Flyway, etc.)
- Version control for schema changes
- Data validation at the database level

### 4. Query Optimization
- Indexing strategy for common queries
- Query result caching
- Batch operations for bulk inserts

## Data Models

### Core Entities
- **matches**: Match details, scores, dates, tournament info
- **teams**: Team information, rosters, rankings
- **players**: Player profiles, statistics
- **maps**: Map-specific match data
- **features**: Engineered features (linked to matches/teams)
- **models**: Model metadata, versions, performance metrics
- **predictions**: Historical predictions and outcomes

## Communication

- **Consumes From**: `data-ingestion`, `feature-engineering`, `model-training`
- **Provides To**: All services (read-only or read-write based on service)
- **Uses**: `shared` schemas for data models

## API Interface

```python
# Example interface
class StorageService:
    def save_match(match_data: MatchSchema) -> str
    def get_matches(filters: MatchFilters) -> List[Match]
    def save_features(match_id: str, features: FeatureDict) -> None
    def get_features(match_id: str) -> FeatureDict
    def save_model(model_artifact: bytes, metadata: ModelMetadata) -> str
    def get_model(model_id: str) -> ModelArtifact
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up PostgreSQL database
3. Configure connection strings in `config.yaml`
4. Run migrations: `alembic upgrade head`
5. Start service: `python main.py` or `uvicorn app:app`

## Database Schema (High-Level)

```sql
-- Example tables
CREATE TABLE matches (
    id UUID PRIMARY KEY,
    hltv_id INTEGER UNIQUE,
    date TIMESTAMP,
    team1_id UUID REFERENCES teams(id),
    team2_id UUID REFERENCES teams(id),
    score1 INTEGER,
    score2 INTEGER,
    tournament_id UUID,
    created_at TIMESTAMP
);

CREATE TABLE features (
    id UUID PRIMARY KEY,
    match_id UUID REFERENCES matches(id),
    feature_set_version VARCHAR(50),
    features JSONB,
    created_at TIMESTAMP
);
```

## Performance Considerations

- **Indexing**: Index on frequently queried fields (date, team_id, match_id)
- **Partitioning**: Consider partitioning matches table by date
- **Caching**: Cache recent matches and popular queries in Redis
- **Connection Pooling**: Use connection pools to manage database connections

## Future Enhancements

- Read replicas for scaling read operations
- Data archival strategy for old matches
- Graph database for relationship queries (team-player connections)
- Time-series database for performance metrics

