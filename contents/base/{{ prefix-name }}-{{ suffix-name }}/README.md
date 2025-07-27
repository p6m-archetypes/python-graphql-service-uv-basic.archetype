# {{ PrefixName }} {{ SuffixName }} Python

A modular, enterprise-grade Python GraphQL {{ suffix-name }} with Strawberry GraphQL, FastAPI and modern tooling.

## 🚀 Getting Started

### Prerequisites
- **Python 3.11+**
- **uv** (modern Python package manager)
- **Docker & Docker Compose** (for database and services)

### Quick Setup

```bash
# 1. Install dependencies
uv sync --dev

# 2. Start database
docker-compose up postgres -d

# 3. Run migrations
uv run {{ prefix-name }}-{{ suffix-name }}-migrate upgrade

# 4. Start the server
uv run {{ prefix-name }}-{{ suffix-name }}-server
```

**That's it!** The server runs on:
- **GraphQL API**: `http://localhost:8080/graphql`
- **Management/Health**: `http://localhost:8080/health`

### Alternative: Ephemeral Database

For development without Docker Compose, use the built-in ephemeral database:

```bash
# 1. Install dependencies
uv sync --dev

# 2. Start server with ephemeral database (auto-starts TestContainers PostgreSQL)
./scripts/run-server-ephemeral.sh
```

**Requirements**: Docker must be running (Docker Desktop, Rancher Desktop, etc.)

**Connection Information**: When the ephemeral database starts, detailed connection information is logged to help you connect with database tools:

```
================================================================================
🐘 EPHEMERAL POSTGRESQL DATABASE CONNECTION INFO
================================================================================

📋 Connection Details:
   Host:     localhost
   Port:     54321  (randomized port)
   Database: {{ prefix_name }}_{{ suffix_name }}
   Username: postgres
   Password: postgres

💻 Connect via psql:
   psql -h localhost -p 54321 -U postgres -d {{ prefix_name }}_{{ suffix_name }}

🔧 DataGrip/Database Tool Settings:
   Type:     PostgreSQL
   Host:     localhost
   Port:     54321
   Database: {{ prefix_name }}_{{ suffix_name }}
   User:     postgres
   Password: postgres
================================================================================
```

### Quick Test

```bash
# Health check
curl http://localhost:8080/health

# GraphQL ping query
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ ping }"}'

# GraphQL schema introspection
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'

# Example {{ prefix_name }} query
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ {{ prefix_name }}(id: \"1\") { id name } }"}'
```

## 🏗️ Build System

This project features a **modern build pipeline** with uv:

```bash
# Build all components
uv build

# Development installation
uv sync --dev
```

The build system automatically:
- ✅ Installs dependencies with deterministic resolution
- ✅ Validates project structure
- ✅ Handles multi-package workspace
- ✅ Provides extensible pipeline for future build steps

## 📋 Essential Commands

### Development
```bash
uv sync --dev                          # Install dependencies with dev tools
uv run {{ prefix-name }}-{{ suffix-name }}-server          # Start GraphQL server
uv build                               # Build all packages
```

### Database
```bash
uv run {{ prefix-name }}-{{ suffix-name }}-migrate upgrade  # Run migrations
uv run {{ prefix-name }}-{{ suffix-name }}-migrate current  # Check migration status
```

### Testing
```bash
uv run pytest                          # All tests
uv run pytest -m unit                  # Unit tests only
uv run pytest -m integration           # Integration tests only
uv run pytest -m graphql               # GraphQL-specific tests
```

### Code Quality
```bash
uv run black . && uv run isort . && uv run flake8  # Format and lint
uv run mypy                            # Type checking
```

## 🏛️ Architecture

Modular design with clear separation of concerns:

```
{{ prefix-name }}-{{ suffix-name }}-python/
├── {{ prefix-name }}-{{ suffix-name }}-api/          # GraphQL schemas and type definitions
├── {{ prefix-name }}-{{ suffix-name }}-core/         # Business logic implementation
├── {{ prefix-name }}-{{ suffix-name }}-persistence/  # Database entities and repositories
├── {{ prefix-name }}-{{ suffix-name }}-server/       # GraphQL resolvers and FastAPI server
├── {{ prefix-name }}-{{ suffix-name }}-client/       # GraphQL client library (optional)
└── {{ prefix-name }}-{{ suffix-name }}-integration-tests/ # End-to-end GraphQL testing
```

## ✨ Enterprise Features

### Core Capabilities
- **GraphQL-First**: Strawberry GraphQL with automatic schema generation
- **Async/Await**: Full async implementation using asyncio
- **Database**: SQLAlchemy 2.0 with Alembic migrations
- **Testing**: pytest with TestContainers for integration tests

### GraphQL Features
- **Queries**: Efficient data fetching with strong typing
- **Mutations**: Data modification operations
- **Subscriptions**: Real-time updates via WebSocket
- **Schema Introspection**: Runtime schema exploration
- **Type Safety**: Full type validation with Strawberry and Pydantic

### Observability
- **Structured Logging**: JSON logging with correlation IDs
- **GraphQL Metrics**: Prometheus with operation-specific metrics
- **Health Checks**: Kubernetes-ready endpoints (`/health`, `/health/live`, `/health/ready`)
- **GraphQL Playground**: Interactive schema exploration at `/graphql`

### Enterprise Middleware
- **Query Complexity Analysis**: Protection against expensive queries
- **Depth Limiting**: Prevent deeply nested queries
- **Rate Limiting**: Request throttling
- **CORS**: Cross-origin resource sharing
- **Correlation IDs**: Request tracing across services

## 🔧 Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/{{ prefix_name }}_{{ suffix_name }}

# Server Ports
API_PORT=8080                     # GraphQL API port
MANAGEMENT_PORT=8080              # Health/metrics port (same as API)

# GraphQL Settings
GRAPHQL_ENDPOINT=/graphql         # GraphQL endpoint path
GRAPHQL_PLAYGROUND_ENABLED=true   # Enable GraphQL Playground (development)
GRAPHQL_INTROSPECTION_ENABLED=true # Enable schema introspection

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_LEVEL=INFO                    # Application log level
ENVIRONMENT=development           # Deployment environment
```

## 🐳 Docker

### Development
```bash
# Start all services (database + monitoring)
docker-compose up -d

# Build and run {{ suffix-name }}
docker build -t {{ prefix-name }}-{{ suffix-name }} .
docker run -p 8080:8080 {{ prefix-name }}-{{ suffix-name }}
```

### Production
The Dockerfile uses **multi-stage builds** with uv for fast, secure containers:
- Non-root execution
- Minimal dependencies
- Optimized layer caching

## 📊 Monitoring

### Included Monitoring Stack
```bash
docker-compose up -d  # Includes Prometheus + Grafana
```

- **Grafana**: `http://localhost:3000` (GraphQL dashboards included)
- **Prometheus**: `http://localhost:9090` (metrics collection)
- **Application Metrics**: `http://localhost:8080/metrics`

### Key GraphQL Metrics
- GraphQL request rates, latencies, error rates by operation
- Query complexity and depth analysis
- Active subscription count
- Schema introspection usage
- Custom business metrics
- Database connection pool status
- Health check status

## 🧪 Testing

### Test Categories
- **Unit Tests**: Fast, isolated component testing
- **Integration Tests**: Database and service integration with TestContainers
- **GraphQL Tests**: Complete query, mutation, and subscription testing

### Running Tests
```bash
# All tests
uv run pytest

# Specific categories
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m graphql

# With coverage
uv run pytest --cov={{ org-name }} --cov-report=html
```

### GraphQL Testing Examples
```python
# Example GraphQL test
async def test_{{ prefix_name }}_query(graphql_client):
    query = """
    query {
        {{ prefix_name }}(id: "1") {
            id
            name
        }
    }
    """
    result = await graphql_client.execute(query)
    assert result["data"]["{{ prefix_name }}"]["id"] == "1"
```

## 🔒 Security

- **Container Security**: Non-root execution, minimal base image
- **Database Security**: Parameterized queries, connection pooling
- **Network Security**: Port isolation, secure configuration
- **GraphQL Security**: Query complexity limiting, depth limiting, rate limiting
- **Schema Security**: Controlled introspection in production

## 📈 Performance

- **Async Architecture**: Full asyncio implementation
- **Connection Pooling**: Configurable database connection management
- **GraphQL Optimizations**: DataLoader for N+1 query prevention
- **Query Analysis**: Complexity and depth limiting for security
- **Caching**: Redis integration for performance-critical paths

## 🎪 GraphQL Usage Examples

### Basic Queries
```graphql
# Get a single {{ prefix_name }}
query {
  {{ prefix_name }}(id: "1") {
    id
    name
  }
}

# Get multiple {{ prefix_name }}s with pagination
query {
  {{ prefix_name }}s(first: 10, after: "cursor") {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Mutations
```graphql
# Create a new {{ prefix_name }}
mutation {
  create{{ PrefixName }}(input: {
    name: "New {{ PrefixName }}"
  }) {
    success
    message
    {{ prefix_name }} {
      id
      name
    }
  }
}
```

### Subscriptions
```graphql
# Subscribe to {{ prefix_name }} changes
subscription {
  {{ prefix_name }}Changes {
    type
    {{ prefix_name }} {
      id
      name
    }
  }
}
```

## 🚧 Advanced Features Available (Currently Disabled)

This {{ PrefixName }} {{ SuffixName }} service includes several **enterprise-grade GraphQL features** that are currently commented out for initial compatibility. These features can be re-enabled for production deployments:

### 🔌 Real-time Subscriptions
**Current Status**: Basic subscription placeholder implemented  
**Available**: Full WebSocket subscription system with event bus

```graphql
# Available when re-enabled
subscription {
  {{ prefix_name }}Updates(filter: { status: ACTIVE }) {
    operation
    {{ prefix_name }} {
      id
      name
      updatedAt
    }
  }
}
```

**To Enable**: Uncomment WebSocket configuration in `{{ prefix-name }}-{{ suffix-name }}-server/src/.../server/app.py`

### 📊 Advanced GraphQL Monitoring
**Current Status**: Basic health metrics  
**Available**: Operation-specific Prometheus metrics

**Metrics Available When Enabled**:
- `graphql_requests_total{operation="get{{ PrefixName }}", type="query"}`
- `graphql_request_duration_seconds{operation="create{{ PrefixName }}"}`
- `graphql_active_subscriptions{operation="{{ prefix_name }}Updates"}`
- `graphql_query_complexity{operation="complex{{ PrefixName }}Query"}`

**To Enable**: Uncomment monitoring extensions in `{{ prefix-name }}-{{ suffix-name }}-server/src/.../server/graphql/schema.py`

### 🛡️ GraphQL Security Features
**Current Status**: Basic GraphQL functionality  
**Available**: Production-ready security extensions

**Security Features When Enabled**:
- **Query Complexity Limiting**: Prevent expensive operations
- **Query Depth Limiting**: Block deeply nested attacks  
- **Rate Limiting**: Throttle requests per operation
- **Input Sanitization**: Clean user inputs
- **Error Masking**: Hide sensitive error details in production

**To Enable**: Uncomment security extensions in `{{ prefix-name }}-{{ suffix-name }}-server/src/.../server/graphql/schema.py`

### 🔧 Advanced {{ PrefixName }} Operations
**Current Status**: Simple placeholder queries/mutations  
**Available**: Full CRUD operations with business logic

**Operations Available When Enabled**:
```graphql
# Advanced queries with filtering and sorting
query {
  {{ prefix_name }}s(
    filter: { status: ACTIVE, createdAfter: "2024-01-01" }
    sort: { field: CREATED_AT, direction: DESC }
    first: 20
  ) {
    edges {
      node {
        id
        name
        status
        metadata
        createdAt
        updatedAt
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}

# Batch operations
mutation {
  createMultiple{{ PrefixName }}s(input: {
    {{ prefix_name }}s: [
      { name: "{{ PrefixName }} 1" },
      { name: "{{ PrefixName }} 2" }
    ]
  }) {
    success
    results {
      id
      name
    }
    errors {
      index
      message
    }
  }
}
```

**To Enable**: 
1. Uncomment API package imports in `{{ prefix-name }}-{{ suffix-name }}-server/src/.../server/graphql/schema.py`
2. Replace placeholder types with real API package types
3. Uncomment resolver implementations

### 🔄 DataLoader Integration
**Current Status**: Direct database queries  
**Available**: N+1 query prevention with DataLoader

**Benefits When Enabled**:
- Batch database queries automatically
- Cache results within request scope
- Prevent N+1 query problems
- Improve GraphQL performance significantly

### 📦 Full Package Integration
**Current Status**: Server package only with placeholders  
**Available**: Complete multi-package architecture

**Integration When Enabled**:
- **API Package**: GraphQL type definitions and schemas
- **Core Package**: Business logic and validation rules  
- **Persistence Package**: Database entities and repositories
- **Server Package**: GraphQL resolvers and implementations

## 🔧 Re-enabling Advanced Features

### Quick Start (Basic Features)
```bash
# 1. Update dependencies if needed
uv sync

# 2. Enable monitoring first (safest)
# Edit: {{ prefix-name }}-{{ suffix-name }}-server/src/.../server/graphql/schema.py
# Uncomment: create_monitoring_extensions() in schema creation

# 3. Test the service
uv run pytest -m graphql
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ ping }"}'
```

### Full Production Setup
```bash
# 1. Enable all features incrementally
# - Monitoring extensions
# - Security extensions  
# - API package integration
# - WebSocket subscriptions

# 2. Update Strawberry GraphQL if needed
uv add strawberry-graphql@latest

# 3. Run comprehensive tests
uv run pytest
./scripts/run-tests.sh

# 4. Validate production readiness
docker-compose up -d
# Check Grafana dashboards: http://localhost:3000
# Check metrics: http://localhost:8080/metrics
```

### 🚨 Important Notes

- **Start incrementally**: Enable one feature group at a time
- **Test thoroughly**: Use `pytest -m graphql` after each change
- **Check compatibility**: Ensure Strawberry GraphQL version supports all features
- **Monitor performance**: Advanced features may impact startup time
- **Production deployment**: All security features should be enabled in production

**This service is designed for enterprise production use** - the commented features provide the full GraphQL stack you need for scalable, secure, observable GraphQL services.

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Run `uv sync --dev` to set up environment
3. Make changes with tests
4. Run `uv run pytest` and code quality checks
5. Test GraphQL operations manually via `/graphql`
6. Submit a pull request

### Code Quality Standards
- **Type Hints**: Full type annotation coverage
- **Formatting**: Black and isort for consistent code style
- **Linting**: Comprehensive checks with flake8 and mypy
- **Testing**: Maintain high test coverage including GraphQL operations

## 📚 More Information

- **GraphQL Playground**: Interactive schema exploration at `http://localhost:8080/graphql`
- **Health Endpoints**: Kubernetes-compatible health checks at `/health/*`
- **Metrics**: Prometheus metrics at `http://localhost:8080/metrics`
- **Schema Documentation**: Auto-generated GraphQL schema documentation