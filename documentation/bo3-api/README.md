# BO3 API Documentation

## Overview

The BO3 API provides access to CS2 esports match data, including AI predictions, betting odds, tournament information, and team details. This documentation focuses on utilizing the API for Method 1: leveraging AI predictions combined with odds data to identify value betting opportunities.

**Base URL:** `https://api.bo3.gg/api/v1/`

## Endpoints

### Matches Endpoint

**Endpoint:** `/matches`

The matches endpoint is the primary resource for retrieving match data with AI predictions and related information.

## Query Parameters

### Pagination

- `page[offset]` - Starting position for pagination (default: 0)
- `page[limit]` - Number of results per page (default: varies)

**Example:**
```
page[offset]=0&page[limit]=5
```

### Sorting

- `sort` - Field to sort by (e.g., `start_date` for chronological order)

**Example:**
```
sort=start_date
```

### Filtering

The API uses a nested filter syntax: `filter[resource.field][operator]=value`

#### Match Status Filter
- `filter[matches.status][in]` - Filter by match status
  - Values: `upcoming`, `current`, `finished`, etc.
  - Use comma-separated values for multiple statuses

**Example:**
```
filter[matches.status][in]=upcoming,current
```

#### Tier Filter
- `filter[matches.tier][in]` - Filter by tournament tier
  - Values: `s` (S-tier), `a` (A-tier), etc.
  - Use comma-separated values for multiple tiers

**Example:**
```
filter[matches.tier][in]=s,a
```

#### Team Filters
- `filter[matches.team1_id][not_eq_null]` - Ensure team1 exists (no value needed)
- `filter[matches.team2_id][not_eq_null]` - Ensure team2 exists (no value needed)

**Example:**
```
filter[matches.team1_id][not_eq_null]&filter[matches.team2_id][not_eq_null]
```

#### Discipline Filter
- `filter[matches.discipline_id][eq]` - Filter by game discipline
  - `1` = CS2 (Counter-Strike 2)

**Example:**
```
filter[matches.discipline_id][eq]=1
```

#### Tournament Filter
- `filter[matches.tournament_id][in]` - Filter by specific tournament IDs
  - Use comma-separated tournament IDs for whitelisting

**Example:**
```
filter[matches.tournament_id][in]=3578,4473,1234
```

#### Date Range Filters
- `filter[matches.start_date][gte]` - Matches starting on or after this date (ISO 8601 format)
- `filter[matches.start_date][lte]` - Matches starting on or before this date (ISO 8601 format)

**Example (upcoming week):**
```
filter[matches.start_date][gte]=2025-11-12T00:00:00.000Z&filter[matches.start_date][lte]=2025-11-19T23:59:59.999Z
```

### Related Data Inclusion

- `with` - Include related resources (comma-separated)
  - `teams` - Team information
  - `tournament` - Tournament details
  - `ai_predictions` - AI prediction data (required for Method 1)
  - `games` - Individual game/map data

**Example:**
```
with=teams,tournament,ai_predictions,games
```

## Complete Example URL

```
https://api.bo3.gg/api/v1/matches?page[offset]=0&page[limit]=5&sort=start_date&filter[matches.status][in]=upcoming,current&filter[matches.tier][in]=s,a&filter[matches.team1_id][not_eq_null]&filter[matches.team2_id][not_eq_null]&filter[matches.discipline_id][eq]=1&with=teams,tournament,ai_predictions,games
```

## Response Structure

### Top-Level Response

```json
{
  "total": {
    "count": 12,
    "pages": 3,
    "offset": 0,
    "limit": 5
  },
  "results": [...],
  "links": {
    "self": "...",
    "next": "...",
    "last": "..."
  }
}
```

### Match Object Structure

Each match in the `results` array contains:

- **Basic Match Info:**
  - `id` - Match ID
  - `slug` - URL-friendly identifier
  - `team1_id`, `team2_id` - Team identifiers
  - `status` - Match status (`upcoming`, `current`, `finished`)
  - `start_date` - ISO 8601 timestamp
  - `bo_type` - Best-of format (1, 3, 5)
  - `tier` - Tournament tier (`s`, `a`, etc.)

- **Scores:**
  - `team1_score`, `team2_score` - Current scores (0 for upcoming matches)
  - `winner_team_id`, `loser_team_id` - Results (null for upcoming)

- **Tournament:**
  - `tournament_id` - Tournament identifier

### AI Predictions (Key for Method 1)

The `ai_predictions` object contains:

```json
{
  "id": 110222,
  "prediction_team1_score": 2,
  "prediction_team2_score": 0,
  "prediction_winner_team_id": 736,
  "prediction_scores_data": {
    "predicted_score": 2.39,
    "proximity_factors": {
      "(0, 2)": 0.933490527805698,
      "(1, 2)": 0.898718600319035,
      "(2, 0)": 0.457145095905913,
      "(2, 1)": 0.710645775969354
    },
    "closest_valid_score": [2, 0],
    "overall_proximity_factor": 0.510284162196592,
    "neighbor_proximity_factor": 0.289354224030646
  },
  "match_id": 103084
}
```

#### AI Predictions Fields Explained

- **`prediction_team1_score`** / **`prediction_team2_score`** - Predicted final scores
- **`prediction_winner_team_id`** - Predicted winning team ID
- **`prediction_scores_data.predicted_score`** - Raw predicted score (may be decimal, e.g., 2.39)
- **`prediction_scores_data.proximity_factors`** - Probability scores for different score combinations
  - Keys are score tuples as strings: `"(team1_score, team2_score)"`
  - Values are probability factors (higher = more likely)
- **`prediction_scores_data.closest_valid_score`** - Rounded prediction to valid score
- **`prediction_scores_data.overall_proximity_factor`** - Confidence metric for the prediction
- **`prediction_scores_data.neighbor_proximity_factor`** - Confidence for adjacent score combinations

### Betting Odds

The `bet_updates` object contains:

```json
{
  "path": "https://...",
  "team_1": {
    "name": "The MongolZ",
    "coeff": 1.3,
    "active": true,
    "team_id": 736,
    "max_coeff": 1.3,
    "aggrement_score": 0.74
  },
  "team_2": {
    "name": "Passion UA",
    "coeff": 3.52,
    "active": true,
    "team_id": 7631,
    "max_coeff": 3.52,
    "aggrement_score": 0.26
  },
  "provider": "1xbit",
  "markets_count": 36,
  "additional_markets": [...]
}
```

#### Betting Odds Fields

- **`team_1.coeff`** / **`team_2.coeff`** - Decimal odds for each team
- **`team_1.aggrement_score`** / **`team_2.aggrement_score`** - Implied probability (sum should equal 1.0)
- **`additional_markets`** - Additional betting markets (total maps, handicaps, etc.)

### Tournament Data

The `tournament` object contains:

```json
{
  "id": 3578,
  "slug": "blast-rivals-fall-2025",
  "name": "BLAST Rivals Fall 2025",
  "status": "upcoming",
  "tier": "s",
  "tier_rank": 1,
  "prize": 350000,
  "discipline_id": 1
}
```

**Key Fields:**
- `id` - Tournament ID (use for whitelisting)
- `name` - Tournament name
- `tier` - Tournament tier (`s` = S-tier, `a` = A-tier)
- `tier_rank` - Ranking within tier

## Fetching Upcoming Matches for a Week

To fetch all upcoming matches for the current week:

1. **Calculate date range** (current date to 7 days ahead)
2. **Use date filters** with ISO 8601 format
3. **Include pagination** to get all results

### Example Implementation Logic

```python
from datetime import datetime, timedelta
from urllib.parse import urlencode

base_url = "https://api.bo3.gg/api/v1/matches"

# Calculate week range
today = datetime.utcnow()
week_end = today + timedelta(days=7)

# Build query parameters
params = {
    "page[offset]": 0,
    "page[limit]": 50,  # Adjust based on expected volume
    "sort": "start_date",
    "filter[matches.status][in]": "upcoming,current",
    "filter[matches.tier][in]": "s,a",
    "filter[matches.team1_id][not_eq_null]": "",
    "filter[matches.team2_id][not_eq_null]": "",
    "filter[matches.discipline_id][eq]": "1",
    "filter[matches.start_date][gte]": today.isoformat() + "Z",
    "filter[matches.start_date][lte]": week_end.isoformat() + "Z",
    "with": "teams,tournament,ai_predictions,games"
}

# Build URL
url = f"{base_url}?{urlencode(params, doseq=True)}"
```

### Handling Pagination

The API response includes pagination metadata. To fetch all results:

```python
def fetch_all_matches(base_params):
    all_matches = []
    offset = 0
    
    while True:
        params = {**base_params, "page[offset]": offset}
        response = requests.get(url, params=params).json()
        
        all_matches.extend(response["results"])
        
        # Check if more pages exist
        if offset + response["total"]["limit"] >= response["total"]["count"]:
            break
            
        offset += response["total"]["limit"]
    
    return all_matches
```

## Tournament Whitelisting

To filter matches by specific tournaments (whitelisting):

### Option 1: Filter by Tournament IDs

```
filter[matches.tournament_id][in]=3578,4473,1234
```

### Option 2: Filter by Tournament Tier

```
filter[matches.tier][in]=s,a
```

### Option 3: Post-Processing Filter

Fetch all matches and filter in your application:

```python
whitelisted_tournament_ids = [3578, 4473, 1234]

filtered_matches = [
    match for match in all_matches 
    if match["tournament_id"] in whitelisted_tournament_ids
]
```

## Method 1: Leveraging AI Predictions

For Method 1 implementation, focus on:

1. **Extract AI Predictions:**
   - `prediction_winner_team_id` - Predicted winner
   - `prediction_team1_score` / `prediction_team2_score` - Predicted score
   - `prediction_scores_data.proximity_factors` - Score probability distribution

2. **Extract Betting Odds:**
   - `bet_updates.team_1.coeff` / `bet_updates.team_2.coeff` - Decimal odds
   - Calculate implied probability: `1 / coeff`
   - `bet_updates.team_1.aggrement_score` - Already calculated implied probability

3. **Compare Predictions vs Odds:**
   - AI prediction probability vs bookmaker implied probability
   - Identify value bets where AI probability > implied probability
   - Consider `overall_proximity_factor` as confidence metric

4. **Score Predictions:**
   - Use `proximity_factors` to identify most likely score combinations
   - Compare with score-specific betting markets in `additional_markets`

## Error Handling

- Check for `null` values in `ai_predictions` (not all matches may have predictions)
- Check for `null` values in `bet_updates` (not all matches may have odds)
- Handle pagination edge cases
- Validate date formats when filtering

## Rate Limiting

The API may implement rate limiting. Consider:
- Implementing request throttling
- Caching responses
- Using appropriate pagination limits

## Notes

- All timestamps are in ISO 8601 format with UTC timezone
- The `discipline_id` of `1` specifically refers to CS2 (Counter-Strike 2)
- Tournament tiers: `s` = S-tier (highest), `a` = A-tier
- Match statuses: `upcoming`, `current`, `finished`
- `bo_type` indicates best-of format (1 = BO1, 3 = BO3, 5 = BO5)

