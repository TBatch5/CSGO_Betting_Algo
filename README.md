# CS2 Betting Predictive Modeling MVP

**Project Purpose:**  
This project aims to build a predictive modeling system for CS2 esports matches, designed to analyze historical data and generate probability-based predictions, and identify potential value bets. The focus is on **robust, modular, and experiment-friendly services** to explore whether an edge exists in CS2 betting.

## Architecture Overview

This project follows a **microservices architecture** designed to be agent-friendly, with each service maintaining a small, focused context boundary. This design enables:

- **Independent Development**: Each service can be developed, tested, and deployed independently
- **Agent Efficiency**: Small context windows allow agents to work effectively within each service boundary
- **Scalability**: Services can scale independently based on demand
- **Experimentability**: Easy to swap implementations or add new models/features

### Service Architecture

```
┌─────────────────┐
│   API Gateway   │  ← Entry point, request routing
└────────┬────────┘
         │
    ┌────┴────┬──────────────┬──────────────┬──────────────┐
    │         │              │              │              │
┌───▼───┐ ┌───▼───┐    ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ Data │ │ Data  │    │  Feature  │  │   Model   │  │Prediction │
│Ingest│ │Storage│    │Engineering│  │  Training │  │  Service  │
└──────┘ └───────┘    └───────────┘  └───────────┘  └───────────┘
   │         │              │              │              │
   └─────────┴──────────────┴──────────────┴──────────────┘
                              │
                        ┌─────▼─────┐
                        │  Shared   │
                        │ Utilities │
                        └───────────┘
```

### Services

1. **data-ingestion/** - HLTV data collection and initial processing
2. **data-storage/** - Data persistence and retrieval layer
3. **feature-engineering/** - Feature extraction and transformation
4. **model-training/** - ML model training and versioning
5. **prediction-service/** - Real-time prediction generation
6. **api-gateway/** - Request orchestration and API endpoints
7. **shared/** - Common utilities, schemas, and configurations

### Data Flow

1. **Ingestion**: HLTV data → `data-ingestion` → `data-storage`
2. **Feature Engineering**: Raw data → `feature-engineering` → Features stored
3. **Model Training**: Features → `model-training` → Trained models stored
4. **Prediction**: Match data → `prediction-service` → Probabilities & value bets

### Technology Stack (Recommended)

- **Language**: Python (for ML/data processing)
- **Data Storage**: PostgreSQL (structured data) + Redis (caching)
- **Message Queue**: RabbitMQ or Kafka (async communication)
- **API**: FastAPI (Python) or Express.js (Node.js)
- **ML Framework**: scikit-learn, XGBoost, or PyTorch
- **Containerization**: Docker + Docker Compose

## Development Practices

### Type Checking

This project uses **strict typing** with mypy. All Python code must pass type checking.

**Configuration:**
- `pyproject.toml` - mypy strict configuration
- Type stubs: `types-requests` for external libraries

**Enforcement:**
- **Pre-commit hooks**: Automatically run mypy before commits (install with `make install-hooks`)
- **CI/CD**: GitHub Actions workflow checks types on push/PR
- **Manual check**: Run `make type-check` or `mypy data-ingestion/bo3-api/ --config-file pyproject.toml`

**Quick Start:**
```bash
# Install type checking dependencies
make install-types

# Run type check
make type-check

# Install pre-commit hooks (recommended)
make install-hooks
```

All new code must include complete type annotations. The strict mypy configuration will catch:
- Missing type annotations
- Incorrect types
- Implicit optional values
- Untyped function definitions

## Methods

### Method 1 - BO3-API prediction leveraging

The BO3-API has a ai_predictions key. I want to look to leverage this key, combined with odds data and figure out if utilising the score or team prediction would result in above average statistical chance and return.