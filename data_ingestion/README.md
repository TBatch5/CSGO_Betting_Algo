# Data Ingestion Service

## Purpose

The Data Ingestion Service is responsible for collecting CS2 match data from external sources and preparing it for storage. Currently, this service provides integration with the BO3 API for fetching match data with AI predictions and betting odds (Method 1).

## Current Implementation

### BO3 API Client

The service includes a BO3 API client for fetching CS2 match data with AI predictions and betting odds.

**Location:** `bo3_api/bo3_client.py`

**Key Features:**
- Fetch upcoming matches for a specified number of days
- Filter by tournament tier (S-tier, A-tier, etc.)
- Tournament whitelisting support
- Extract AI predictions and betting odds
- Automatic pagination handling
- Retry logic with exponential backoff
- Rate limiting support

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. See `bo3_api/example_bo3_usage.py` for usage examples

## Example Usage

### BO3 API Client (Method 1)

```python
# Run from bo3_api directory or add to path
from bo3_client import BO3Client

# Initialize client
client = BO3Client()

try:
    # Fetch upcoming matches for the next week with AI predictions
    matches = client.fetch_upcoming_week_matches(days_ahead=7)
    
    # Or fetch only matches with AI predictions and odds
    matches_with_predictions = client.get_matches_with_predictions(
        days_ahead=7,
        require_odds=True
    )
    
    # Extract AI predictions and odds for analysis
    for match in matches_with_predictions:
        ai_pred = client.extract_ai_predictions(match)
        odds = client.extract_betting_odds(match)
        # Process for Method 1: compare AI predictions vs odds
        
finally:
    client.close()
```

See `bo3_api/example_bo3_usage.py` for more detailed examples.

## Data Ingestion Pipeline

The data ingestion pipeline combines the BO3 API client with the database storage service to automatically fetch and store match data.

**Location:** `ingest_bo3_data.py`

### CLI Options

- `--days N`: Number of days ahead to fetch (default: 7)
- `--tier TIER [TIER ...]`: Tournament tiers to filter (default: s a)
- `--require-predictions`: Only fetch matches with AI predictions (default: True)
- `--no-require-predictions`: Fetch all matches
- `--require-odds`: Only fetch matches with betting odds (default: False)
- `--dry-run`: Fetch data but don't save to database
- `--verbose`: Enable verbose logging

### What Gets Stored

For each match, the ingestion pipeline stores:
- **Match data**: Status, scores, start time, tier, etc.
- **Teams**: Both teams with logos, country codes, etc.
- **Tournament**: Tournament details, prize pool, tier, etc.
- **AI Predictions**: Predicted scores and winner (if available)
- **Betting Odds**: Odds from various providers (if available)

## Future Enhancements

- HLTV integration for historical match data
- Data validation and normalization components
- Scheduling and orchestration for periodic ingestion
- Scheduling and orchestration for periodic ingestion
- Support for other data sources (ESL, BLAST, etc.)
- Real-time match tracking
- Historical data backfill utilities
- Data quality monitoring and alerting
