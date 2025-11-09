# Data Ingestion Service

## Purpose

The Data Ingestion Service is responsible for collecting CS2 match data from HLTV and preparing it for storage. This service acts as the entry point for all external data into the system.

## Responsibilities

- **HLTV Integration**: Scrape/fetch match data, team information, player statistics, and historical results from HLTV
- **Data Validation**: Ensure data quality and completeness before storage
- **Data Normalization**: Transform HLTV data into our internal schema format
- **Scheduling**: Run periodic ingestion jobs to keep data up-to-date
- **Error Handling**: Manage rate limiting, retries, and failed ingestion attempts

## Agent Context Boundaries

This service should be self-contained with minimal external dependencies:
- **Input**: HLTV API/website endpoints, configuration (schedules, rate limits)
- **Output**: Validated, normalized data sent to `data-storage` service
- **No Direct Dependencies On**: Feature engineering, models, or predictions

## Key Components

### 1. HLTV Client
- Web scraping or API client for HLTV
- Handles authentication, rate limiting, and retries
- Extracts: matches, teams, players, maps, statistics

### 2. Data Validator
- Schema validation against shared data models
- Completeness checks (required fields)
- Data quality checks (ranges, formats)

### 3. Data Normalizer
- Transform HLTV format → internal schema
- Handle missing/null values
- Standardize date formats, team names, etc.

### 4. Ingestion Orchestrator
- Schedule periodic ingestion jobs
- Manage batch vs. real-time ingestion
- Coordinate with storage service

## Data Schema (Output)

The service outputs data in the following structure:
- **Matches**: Match ID, date, teams, score, maps, tournament info
- **Teams**: Team ID, name, roster, rankings
- **Players**: Player ID, name, team, statistics
- **Maps**: Map name, statistics, round-by-round data

## Communication

- **Publishes To**: `data-storage` service (via message queue or direct API)
- **Consumes From**: HLTV (external)
- **Uses**: `shared` utilities for schemas and common functions

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure HLTV credentials/endpoints in `config.yaml`
3. Set up message queue connection (if using async)
4. Run: `python main.py` or use scheduler (cron, Celery, etc.)

## Example Usage

```python
from data_ingestion.hltv_client import HLTVClient
from data_ingestion.validator import DataValidator
from data_ingestion.storage_client import StorageClient

# Fetch recent matches
client = HLTVClient()
matches = client.fetch_recent_matches(days=7)

# Validate and normalize
validator = DataValidator()
normalized = validator.validate_and_normalize(matches)

# Send to storage
storage = StorageClient()
storage.save_matches(normalized)
```

## Future Enhancements

- Support for other data sources (ESL, BLAST, etc.)
- Real-time match tracking
- Historical data backfill utilities
- Data quality monitoring and alerting

