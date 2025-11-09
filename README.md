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

### Getting Started

Each service directory contains its own README with specific setup instructions. Start with:
1. `shared/README.md` - Common setup and dependencies
2. `data-storage/README.md` - Database setup
3. `data-ingestion/README.md` - HLTV integration  