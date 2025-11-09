# Prediction Service

## Purpose

The Prediction Service generates real-time predictions for upcoming CS2 matches using trained models. It combines model predictions with betting odds to identify value bets.

## Responsibilities

- **Prediction Generation**: Use trained models to predict match outcomes
- **Probability Calibration**: Ensure predictions are well-calibrated probabilities
- **Value Bet Identification**: Compare predictions to betting odds to find value
- **Confidence Scoring**: Assess prediction confidence and reliability
- **Prediction Caching**: Cache predictions for frequently requested matches

## Agent Context Boundaries

This service is the prediction layer:
- **Input**: Match data and features (from `data-storage`), trained models (from `data-storage`)
- **Output**: Predictions and value bet recommendations
- **No Training Logic**: Does not train models, only uses them
- **No Data Collection**: Does not fetch raw data

## Key Components

### 1. Prediction Engine
- **Model Loading**: Load latest or specified model version
- **Feature Preparation**: Generate features for input matches
- **Inference**: Run predictions through models
- **Post-processing**: Calibrate probabilities, apply confidence thresholds

### 2. Value Bet Calculator
- **Odds Integration**: Fetch or receive betting odds
- **Expected Value (EV)**: Calculate EV = (probability × odds) - 1
- **Kelly Criterion**: Calculate optimal bet sizing
- **Value Thresholds**: Filter bets by minimum EV threshold

### 3. Prediction Types

#### Match Outcome
- Team1 win probability
- Team2 win probability
- Draw probability (if applicable)

#### Map-Specific
- Per-map win probabilities
- Map selection predictions

#### Score Predictions
- Expected round scores
- Over/under round totals

### 4. Confidence Assessment
- **Model Confidence**: Based on feature quality and model certainty
- **Data Quality**: Assess completeness of input features
- **Historical Accuracy**: Track model performance on similar matches

## Communication

- **Consumes From**: `data-storage` (matches, features, models)
- **Provides To**: `api-gateway` (predictions via API)
- **Uses**: `shared` utilities for schemas and common functions

## Prediction Workflow

```python
from prediction_service.engine import PredictionEngine
from prediction_service.value_calculator import ValueBetCalculator

# Initialize
engine = PredictionEngine()
value_calc = ValueBetCalculator()

# Load model and match data
model = storage_service.get_model(model_version="v1.2")
match = storage_service.get_match(match_id="uuid")
features = storage_service.get_features(match_id="uuid")

# Generate prediction
prediction = engine.predict(
    match=match,
    features=features,
    model=model
)

# Calculate value bets
odds = {"team1": 2.0, "team2": 1.8}
value_bets = value_calc.identify_value_bets(
    predictions=prediction,
    odds=odds,
    min_ev=0.1  # 10% expected value threshold
)
```

## API Interface

```python
# Example endpoints
POST /predictions/match/{match_id}
  → Returns: prediction probabilities, confidence scores

POST /predictions/value-bets
  → Input: match_id, odds
  → Returns: value bet recommendations with EV and Kelly sizing

GET /predictions/upcoming
  → Returns: predictions for all upcoming matches
```

## Prediction Output Format

```json
{
  "match_id": "uuid",
  "team1_win_probability": 0.62,
  "team2_win_probability": 0.38,
  "confidence": 0.85,
  "model_version": "v1.2",
  "feature_version": "v2.0",
  "value_bets": [
    {
      "team": "team1",
      "odds": 2.0,
      "probability": 0.62,
      "expected_value": 0.24,
      "kelly_fraction": 0.12,
      "recommended_bet": true
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure `data-storage` service is accessible
3. Configure model version and thresholds in `config/prediction.yaml`
4. Set up caching (Redis) for performance
5. Run: `python main.py` or `uvicorn app:app`

## Performance Considerations

- **Model Caching**: Cache loaded models in memory
- **Prediction Caching**: Cache predictions for upcoming matches
- **Batch Predictions**: Process multiple matches efficiently
- **Async Processing**: Use async/await for I/O operations

## Value Bet Criteria

A value bet is identified when:
1. **EV > Threshold**: Expected value exceeds minimum (e.g., 10%)
2. **Confidence > Threshold**: Prediction confidence is sufficient
3. **Data Quality**: Input features are complete and reliable
4. **Model Performance**: Model has good historical performance on similar matches

## Future Enhancements

- Real-time prediction updates as match approaches
- Live match prediction updates (in-play)
- Multi-model ensemble predictions
- Confidence intervals for probabilities
- Risk-adjusted bet sizing
- Portfolio optimization across multiple bets

