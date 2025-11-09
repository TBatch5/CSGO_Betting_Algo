# Shared Utilities

## Purpose

The Shared module contains common code, schemas, utilities, and configurations used across all microservices. This ensures consistency and reduces code duplication.

## Responsibilities

- **Data Schemas**: Common data models and schemas
- **Utilities**: Helper functions used by multiple services
- **Configuration**: Shared configuration patterns
- **Constants**: Shared constants and enums
- **Type Definitions**: Type hints and interfaces
- **Error Classes**: Common exception types

## Agent Context Boundaries

This is a library module:
- **No Service Logic**: Pure utilities, no business logic
- **No Dependencies**: Should not depend on other services
- **Used By**: All services import from this module

## Key Components

### 1. Data Schemas

#### Match Schema
```python
@dataclass
class Match:
    id: str
    hltv_id: int
    date: datetime
    team1_id: str
    team2_id: str
    score1: int
    score2: int
    tournament_id: str
    maps: List[MapResult]
```

#### Team Schema
```python
@dataclass
class Team:
    id: str
    name: str
    hltv_id: int
    ranking: int
    players: List[str]  # Player IDs
```

#### Feature Schema
```python
@dataclass
class Features:
    match_id: str
    feature_version: str
    team1_features: Dict[str, float]
    team2_features: Dict[str, float]
    match_context: Dict[str, Any]
```

### 2. Common Utilities

#### Date/Time Helpers
- Date parsing and formatting
- Timezone handling
- Date range utilities

#### Data Validation
- Schema validation functions
- Type checking utilities
- Data sanitization

#### Logging
- Standardized logging configuration
- Structured logging format
- Log levels and handlers

### 3. Constants

```python
# Tournament types
TOURNAMENT_TYPES = ["Major", "Premier", "Pro", "Challenger"]

# Map names
MAPS = ["dust2", "mirage", "inferno", "overpass", "nuke", "vertigo", "ancient"]

# Model types
MODEL_TYPES = ["xgboost", "random_forest", "neural_network"]
```

### 4. Error Classes

```python
class ServiceError(Exception):
    """Base exception for service errors"""
    pass

class DataNotFoundError(ServiceError):
    """Raised when requested data is not found"""
    pass

class ValidationError(ServiceError):
    """Raised when data validation fails"""
    pass
```

### 5. Configuration Patterns

```python
# config.py
from pydantic import BaseSettings

class DatabaseConfig(BaseSettings):
    host: str
    port: int
    database: str
    user: str
    password: str

class RedisConfig(BaseSettings):
    host: str
    port: int
```

## Usage Across Services

### In Data Ingestion
```python
from shared.schemas import Match, Team
from shared.utils import validate_match_data
from shared.errors import ValidationError

match = Match(...)
if not validate_match_data(match):
    raise ValidationError("Invalid match data")
```

### In Feature Engineering
```python
from shared.schemas import Features
from shared.constants import FEATURE_VERSION

features = Features(
    match_id="uuid",
    feature_version=FEATURE_VERSION,
    ...
)
```

### In Model Training
```python
from shared.schemas import Features
from shared.utils import load_config

config = load_config("model_training")
```

## Package Structure

```
shared/
├── __init__.py
├── schemas/
│   ├── __init__.py
│   ├── match.py
│   ├── team.py
│   ├── features.py
│   └── model.py
├── utils/
│   ├── __init__.py
│   ├── date_utils.py
│   ├── validation.py
│   └── logging.py
├── constants.py
├── errors.py
└── config.py
```

## Installation

This module should be installed as a package:

```bash
# In each service directory
pip install -e ../shared
```

Or add to requirements.txt:
```
-e ../shared
```

## Versioning

- **Semantic Versioning**: Follow semver for breaking changes
- **Backward Compatibility**: Maintain backward compatibility when possible
- **Migration Guides**: Document breaking changes

## Testing

Shared utilities should have comprehensive tests:
- Unit tests for all utility functions
- Schema validation tests
- Integration tests for common workflows

## Future Enhancements

- Protocol buffers for service communication
- Shared message queue message formats
- Common authentication/authorization utilities
- Shared monitoring and observability utilities

