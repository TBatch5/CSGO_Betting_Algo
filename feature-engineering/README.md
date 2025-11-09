# Feature Engineering Service

## Purpose

The Feature Engineering Service transforms raw match data into features suitable for machine learning models. It creates statistical, temporal, and contextual features that capture team performance, player form, and match context.

## Responsibilities

- **Feature Extraction**: Derive features from raw match data
- **Feature Transformation**: Normalize, scale, and encode features
- **Temporal Features**: Calculate rolling statistics, form indicators, recent performance
- **Contextual Features**: Tournament importance, map preferences, head-to-head records
- **Feature Versioning**: Track feature set versions for reproducibility

## Agent Context Boundaries

This service is focused solely on feature creation:
- **Input**: Raw match data from `data-storage`
- **Output**: Engineered features back to `data-storage`
- **No Model Logic**: Does not train or use models, only creates features

## Key Components

### 1. Feature Extractors

#### Team Features
- Recent form (last N matches win rate)
- Map-specific win rates
- Average round difference
- Performance vs. top teams
- Tournament performance history

#### Player Features
- Individual player statistics (K/D, rating, impact)
- Recent form trends
- Map-specific performance
- Role-specific metrics (AWPer, IGL, etc.)

#### Match Context Features
- Head-to-head record
- Tournament stage (group, playoffs, final)
- Time since last match
- Travel/jetlag factors (if available)
- Map pool strengths

### 2. Feature Pipeline
- **ETL Process**: Extract → Transform → Load
- **Batch Processing**: Process historical matches in batches
- **Incremental Updates**: Update features for new matches
- **Validation**: Ensure feature completeness and quality

### 3. Feature Store
- Store computed features in `data-storage`
- Link features to match IDs
- Version feature sets for model reproducibility

### 4. Feature Registry
- Document all features and their definitions
- Track feature importance over time
- Manage feature deprecation

## Feature Categories

### 1. Statistical Features
- Win rates, averages, medians
- Standard deviations, percentiles
- Rolling windows (7-day, 30-day, etc.)

### 2. Temporal Features
- Time since last match
- Days of rest
- Match frequency
- Form trends (improving/declining)

### 3. Categorical Features
- Map names (one-hot encoded)
- Tournament types
- Team rankings
- Player roles

### 4. Interaction Features
- Team vs. team historical performance
- Map-specific team matchups
- Player combinations

## Communication

- **Consumes From**: `data-storage` (raw match data)
- **Publishes To**: `data-storage` (engineered features)
- **Uses**: `shared` utilities for data models and common functions

## Example Feature Set

```python
{
    "match_id": "uuid",
    "team1_features": {
        "recent_win_rate_7d": 0.65,
        "map_win_rate_dust2": 0.72,
        "avg_round_diff": 2.3,
        "vs_top10_win_rate": 0.45,
        "days_since_last_match": 3
    },
    "team2_features": { ... },
    "match_context": {
        "head_to_head_team1_wins": 5,
        "head_to_head_team2_wins": 3,
        "tournament_stage": "playoffs",
        "map": "dust2"
    }
}
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure `data-storage` service is accessible
3. Configure feature definitions in `config/features.yaml`
4. Run: `python main.py` or schedule periodic feature updates

## Usage

```python
from feature_engineering.pipeline import FeaturePipeline
from feature_engineering.extractors import TeamFeatureExtractor

# Initialize pipeline
pipeline = FeaturePipeline()

# Process matches
matches = storage_service.get_matches(date_range="2024-01-01:2024-01-31")
features = pipeline.extract_features(matches)

# Save features
storage_service.save_features(features)
```

## Feature Versioning

Features are versioned to ensure model reproducibility:
- **v1.0**: Initial feature set
- **v1.1**: Added player form features
- **v2.0**: Major refactor with new statistical features

Each model training run references a specific feature version.

## Future Enhancements

- Automated feature selection
- Feature importance analysis
- Real-time feature computation for live matches
- Feature drift detection
- Advanced features (momentum, psychological factors)

