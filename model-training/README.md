# Model Training Service

## Purpose

The Model Training Service trains, evaluates, and versions machine learning models for CS2 match prediction. It handles the complete ML lifecycle from training to model registry.

## Responsibilities

- **Model Training**: Train various ML models (XGBoost, neural networks, etc.)
- **Model Evaluation**: Validate models using cross-validation and holdout sets
- **Hyperparameter Tuning**: Optimize model parameters
- **Model Versioning**: Track model versions, performance metrics, and metadata
- **Model Registry**: Store trained models and their artifacts
- **Experiment Tracking**: Log training experiments, parameters, and results

## Agent Context Boundaries

This service is focused on model development:
- **Input**: Features from `data-storage`
- **Output**: Trained models stored in `data-storage`
- **No Prediction Logic**: Does not make predictions, only trains models
- **No Data Collection**: Does not fetch or process raw data

## Key Components

### 1. Training Pipeline
- **Data Loading**: Load features from storage
- **Train/Val/Test Split**: Temporal splits (no data leakage)
- **Feature Selection**: Optional feature importance-based selection
- **Model Training**: Train multiple model types
- **Evaluation**: Calculate metrics (accuracy, log loss, Brier score, ROI)

### 2. Model Types

#### Baseline Models
- **Logistic Regression**: Simple baseline
- **Random Forest**: Ensemble method
- **XGBoost**: Gradient boosting (likely primary model)

#### Advanced Models
- **Neural Networks**: Deep learning for complex patterns
- **Ensemble Methods**: Combine multiple models
- **Time Series Models**: For sequential match predictions

### 3. Evaluation Framework
- **Metrics**:
  - Classification: Accuracy, Precision, Recall, F1
  - Probability: Log Loss, Brier Score, Calibration
  - Betting: ROI, Expected Value, Kelly Criterion
- **Cross-Validation**: Time-series aware CV
- **Backtesting**: Historical performance simulation

### 4. Model Registry
- Store model artifacts (pickle, ONNX, etc.)
- Track model metadata (features used, hyperparameters, performance)
- Version control for model iterations
- Model comparison and selection

### 5. Experiment Tracking
- Log all training runs (MLflow, Weights & Biases, or custom)
- Track hyperparameters, metrics, and model artifacts
- Enable reproducibility

## Model Output

Models predict:
- **Match Outcome**: Probability of team1 win, team2 win, draw
- **Map Outcomes**: Per-map win probabilities
- **Score Predictions**: Expected round scores

## Communication

- **Consumes From**: `data-storage` (features)
- **Publishes To**: `data-storage` (trained models)
- **Uses**: `shared` utilities for schemas and common functions

## Training Workflow

```python
from model_training.pipeline import TrainingPipeline
from model_training.models import XGBoostModel

# Load features
features = storage_service.get_features(
    feature_version="v2.0",
    date_range="2023-01-01:2024-01-01"
)

# Initialize pipeline
pipeline = TrainingPipeline()

# Train model
model = pipeline.train(
    features=features,
    model_type="xgboost",
    hyperparameters={"n_estimators": 100, "max_depth": 5}
)

# Evaluate
metrics = pipeline.evaluate(model, test_features)

# Save model
storage_service.save_model(
    model=model,
    metadata={
        "version": "v1.2",
        "feature_version": "v2.0",
        "metrics": metrics,
        "hyperparameters": model.get_params()
    }
)
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Ensure `data-storage` service is accessible
3. Configure training parameters in `config/training.yaml`
4. Set up experiment tracking (MLflow, etc.)
5. Run: `python train.py` or schedule periodic retraining

## Model Evaluation Criteria

Models are evaluated on:
1. **Prediction Accuracy**: How often predictions are correct
2. **Probability Calibration**: Are probabilities well-calibrated?
3. **Betting Performance**: Simulated ROI on historical data
4. **Generalization**: Performance on unseen data (temporal splits)

## Hyperparameter Tuning

- **Grid Search**: Exhaustive search over parameter grid
- **Random Search**: Random sampling of parameter space
- **Bayesian Optimization**: Efficient search using Gaussian processes
- **Cross-Validation**: Time-series aware CV to prevent leakage

## Model Versioning Strategy

- **Semantic Versioning**: v1.0.0, v1.1.0, v2.0.0
- **Version Components**:
  - Major: Breaking changes, new model architecture
  - Minor: New features, improved performance
  - Patch: Bug fixes, minor improvements

## Future Enhancements

- Automated retraining pipelines
- Online learning for model updates
- A/B testing framework for model comparison
- Model explainability (SHAP, LIME)
- Multi-objective optimization (accuracy + ROI)
- Transfer learning from other esports

