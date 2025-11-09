# API Gateway Service

## Purpose

The API Gateway serves as the single entry point for all external requests to the CS2 betting prediction system. It handles routing, authentication, rate limiting, and orchestrates calls to backend services.

## Responsibilities

- **Request Routing**: Route requests to appropriate backend services
- **API Orchestration**: Coordinate multiple service calls for complex operations
- **Authentication & Authorization**: Manage API keys, user authentication
- **Rate Limiting**: Prevent abuse and manage resource usage
- **Request/Response Transformation**: Format data for external consumers
- **Error Handling**: Centralized error handling and logging
- **Monitoring**: Track API usage, latency, and errors

## Agent Context Boundaries

This service is the orchestration layer:
- **Input**: HTTP requests from external clients
- **Output**: Formatted responses to clients
- **Orchestrates**: Calls to `data-storage`, `prediction-service`, etc.
- **No Business Logic**: Minimal logic, mostly routing and coordination

## Key Components

### 1. API Endpoints

#### Match Data
```
GET /api/v1/matches
  → List matches with filters (date, teams, tournament)
GET /api/v1/matches/{match_id}
  → Get specific match details
```

#### Predictions
```
GET /api/v1/predictions/upcoming
  → Get predictions for upcoming matches
POST /api/v1/predictions/match/{match_id}
  → Generate prediction for specific match
GET /api/v1/predictions/{prediction_id}
  → Get stored prediction
```

#### Value Bets
```
POST /api/v1/value-bets
  → Input: match_id, odds
  → Returns: value bet recommendations
GET /api/v1/value-bets/history
  → Historical value bet performance
```

#### System
```
GET /api/v1/health
  → Service health check
GET /api/v1/models
  → List available model versions
GET /api/v1/stats
  → System statistics and metrics
```

### 2. Request Orchestration

#### Example: Get Match Prediction
1. Receive request: `GET /api/v1/predictions/match/{match_id}`
2. Fetch match data from `data-storage`
3. Fetch features from `data-storage`
4. Call `prediction-service` to generate prediction
5. Format and return response

#### Example: Get Upcoming Predictions
1. Receive request: `GET /api/v1/predictions/upcoming`
2. Fetch upcoming matches from `data-storage`
3. Batch call `prediction-service` for all matches
4. Aggregate and format responses
5. Return list of predictions

### 3. Authentication & Security
- **API Keys**: Simple API key authentication for MVP
- **Rate Limiting**: Per-key rate limits (e.g., 100 requests/hour)
- **CORS**: Configure CORS for web clients
- **Input Validation**: Validate and sanitize all inputs

### 4. Error Handling
- **Standardized Errors**: Consistent error response format
- **Service Failures**: Handle backend service failures gracefully
- **Timeout Management**: Set timeouts for service calls
- **Retry Logic**: Retry transient failures

## Communication

- **Consumes From**: All backend services (`data-storage`, `prediction-service`, etc.)
- **Provides To**: External clients (web apps, mobile apps, scripts)
- **Uses**: `shared` utilities for schemas and common functions

## API Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "MATCH_NOT_FOUND",
    "message": "Match with ID 'uuid' not found",
    "details": { ... }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Setup

1. Install dependencies: `pip install -r requirements.txt` or `npm install`
2. Configure backend service URLs in `config.yaml`
3. Set up authentication (API key storage, rate limiting)
4. Configure CORS if needed
5. Run: `python main.py` or `npm start` or `uvicorn app:app`

## Technology Options

- **Python**: FastAPI (recommended for Python ecosystem)
- **Node.js**: Express.js (if team prefers JavaScript)
- **Go**: Gin or Echo (for high performance)

## Example Implementation (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from api_gateway.services import StorageService, PredictionService

app = FastAPI()

@app.get("/api/v1/predictions/match/{match_id}")
async def get_match_prediction(match_id: str):
    # Fetch match and features
    match = await storage_service.get_match(match_id)
    features = await storage_service.get_features(match_id)
    
    # Generate prediction
    prediction = await prediction_service.predict(match, features)
    
    return {"success": True, "data": prediction}
```

## Rate Limiting Strategy

- **Tier 1 (Free)**: 100 requests/day
- **Tier 2 (Paid)**: 1000 requests/day
- **Tier 3 (Enterprise)**: Unlimited

## Monitoring & Logging

- **Request Logging**: Log all API requests
- **Performance Metrics**: Track latency, throughput
- **Error Tracking**: Monitor error rates and types
- **Usage Analytics**: Track endpoint usage patterns

## Future Enhancements

- GraphQL API for flexible queries
- WebSocket support for real-time updates
- API versioning strategy
- Request/response caching
- Load balancing and auto-scaling
- API documentation (Swagger/OpenAPI)

