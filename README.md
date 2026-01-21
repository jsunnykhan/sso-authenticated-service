# SSO-IDENTITY-SERVICE

An enterprise-grade Single Sign-On (SSO) Identity Provider built with FastAPI. This service implements OAuth 2.0 and OpenID Connect protocols to provide secure authentication and authorization capabilities for distributed applications.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Database Migrations](#database-migrations)
- [Docker Deployment](#docker-deployment)
- [Development](#development)
- [Project Structure](#project-structure)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)

## Features

- **OAuth 2.0 Authorization Code Flow**: Complete implementation of the authorization code grant type
- **OpenID Connect Support**: Implement the OpenID Connect standard for authentication
- **JWT Token Management**: Secure token generation, validation, and expiration handling
- **Password Security**: Industry-standard bcrypt password hashing with configurable rounds
- **Redis Caching**: High-performance session and state caching with expiration
- **PostgreSQL Database**: Persistent storage with Alembic migrations
- **User Consent Management**: GDPR-compliant consent workflow for third-party access
- **Multi-tenant Support**: Built to support multiple OAuth clients
- **Well-Known Endpoint**: Standard OAuth 2.0 configuration endpoint (/.well-known/oauth-authorization-server)
- **Secure Session Management**: Server-side session handling with Redis backend

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│                    API Routes Layer                          │
│  ├─ Authorization    ├─ Token          ├─ User Info         │
│  ├─ Login            ├─ Consent        ├─ Client Management │
│  └─ Well-Known       └─ Password       └─ Callback          │
├─────────────────────────────────────────────────────────────┤
│                    Services Layer                            │
│  ├─ User Service     ├─ Client Service ├─ Consent Service  │
│  ├─ Token Utility    └─ Redis Cache    └─ Hash Utility     │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                                │
│  ├─ PostgreSQL DB    ├─ Redis Cache    └─ Session Store    │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+**
- **Redis 7.2+**
- **Docker & Docker Compose** (optional, for containerized deployment)
- **pip** or **conda** (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sso-identity-service
```

### 2. Create a Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440

# PostgreSQL Configuration
POSTGRES_DB=sso_identity_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# IDP Configuration
IDP_ISSUER=https://your-domain.com

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
REDIS_CACHE_EXPIRE_SECONDS=3600
```

## Configuration

### Key Configuration Files

- **`app/core/config.py`**: Application settings and environment variable management
- **`alembic.ini`**: Database migration configuration
- **`.env`**: Environment-specific variables (not committed to version control)

### Important Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for JWT token signing | Required |
| `JWT_ALGORITHM` | Algorithm for JWT encoding | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token validity period | 30 |
| `POSTGRES_HOST` | PostgreSQL server hostname | localhost |
| `REDIS_HOST` | Redis server hostname | localhost |
| `IDP_ISSUER` | OAuth 2.0 Issuer identifier | Required |

## Running the Application

### Local Development (without Docker)

1. **Start PostgreSQL and Redis** (ensure services are running)

2. **Run Database Migrations**

```bash
alembic upgrade head
```

3. **Create Default OAuth Client** (First-time setup only)

This step creates a default OAuth client that can be used for testing and initial configuration:

```bash
python app/services/scripts/create_default_client.py
```

The script will:
- Generate a unique `client_id` and `client_secret`
- Create RSA key pairs for the client
- Store the default client in the database
- Output: `Default client created successfully.`

4. **Run the FastAPI Server**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4010 --reload
```

The API will be available at: `http://localhost:4010`

**API Documentation:**
- **Swagger UI**: http://localhost:4010/v1/docs
- **ReDoc**: http://localhost:4010/v1/redoc

### Using Makefile (Convenient)

If a Makefile is available, use convenient commands:

```bash
make run              # Run the application
make migrate          # Run database migrations
make create-client    # Create default OAuth client
make test             # Run tests
```

## API Endpoints

### Well-Known Configuration
- `GET /.well-known/oauth-authorization-server` - OAuth 2.0 server metadata

### OAuth 2.0 Authorization
- `GET /oauth/authorize` - Authorization endpoint (user consent required)
- `POST /oauth/token` - Token endpoint (exchange code for tokens)
- `POST /oauth/token` - Refresh token endpoint

### User Management
- `GET /oauth/user_info` - Get authenticated user profile (requires access token)
- `POST /oauth/login` - User login endpoint

### Client Management
- `GET /oauth/clients/{client_id}` - Get client details
- `POST /oauth/clients` - Register new OAuth client (admin only)

### Consent
- `GET /oauth/consent` - Display user consent screen
- `POST /oauth/consent` - Submit user consent

## Database Migrations

Database migrations are managed using Alembic, an SQLAlchemy migration tool.

### Create a New Migration

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision>

# Rollback latest migration
alembic downgrade -1
```

### View Migration History

```bash
alembic history
```

## Docker Deployment

### Using Docker Compose (Recommended)

The project includes a `docker-compose.yml` file that orchestrates PostgreSQL, Redis, and the FastAPI application.

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Create default client in Docker
docker-compose exec web python app/services/scripts/create_default_client.py

# Run migrations in Docker
docker-compose exec web alembic upgrade head

# Stop all services
docker-compose down
```

### Manual Docker Build

```bash
# Build the Docker image
docker build -t sso-identity-service:latest .

# Run the container
docker run -d \
  --name sso-service \
  -p 4010:4010 \
  --env-file .env \
  --network sso-identity-network \
  sso-identity-service:latest
```

### Service Health Checks

The docker-compose setup includes health checks for all services:
- PostgreSQL: Validates connectivity
- Redis: Validates connectivity
- Web Service: Validates API responsiveness

## Development

### Project Structure

```
sso-authenticated-service/
├── app/
│   ├── api/
│   │   └── routes/              # API endpoint handlers
│   │       ├── authorize.py      # OAuth authorization
│   │       ├── token.py          # Token generation/refresh
│   │       ├── login.py          # User authentication
│   │       ├── consent.py        # User consent handling
│   │       ├── client.py         # OAuth client management
│   │       ├── user_profile.py   # User information
│   │       └── well_known.py     # OAuth config endpoint
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── security.py          # Security utilities
│   │   └── radis.py             # Redis configuration
│   ├── db/
│   │   ├── models/              # SQLAlchemy ORM models
│   │   │   ├── user.py          # User model
│   │   │   ├── oauth_client.py   # OAuth client model
│   │   │   ├── user_consent.py   # Consent model
│   │   │   ├── user_profile.py   # Profile model
│   │   │   └── password.py       # Password history model
│   │   ├── session.py           # Database session management
│   │   └── base.py              # Base model configuration
│   ├── schemas/                 # Pydantic request/response models
│   │   ├── authorize.py
│   │   ├── client.py
│   │   ├── jwt.py
│   │   ├── user.py
│   │   └── api_response.py       # Standard API response wrapper
│   ├── services/
│   │   ├── user.py              # User business logic
│   │   ├── client.py            # OAuth client logic
│   │   ├── consent.py           # Consent management
│   │   ├── redis.py             # Redis operations
│   │   └── scripts/
│   │       └── create_default_client.py  # Default client creation
│   ├── templates/               # HTML templates (Jinja2)
│   │   ├── login.html           # Login page
│   │   └── consent.html         # Consent page
│   ├── utils/
│   │   ├── token.py             # Token utilities
│   │   ├── hash.py              # Password hashing
│   │   ├── logger.py            # Logging configuration
│   │   └── url.py               # URL utilities
│   └── main.py                  # FastAPI application entry point
├── alembic/                     # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                # Migration files
├── keys/                        # RSA keys storage (gitignored)
├── .env                         # Environment variables (gitignored)
├── .gitignore
├── Dockerfile                   # Container image definition
├── docker-compose.yml           # Multi-container orchestration
├── requirements.txt             # Python dependencies
├── alembic.ini                  # Alembic configuration
├── Makefile                     # Development commands
└── README.md                    # This file
```

### Key Dependencies

- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type hints
- **python-jose**: JWT token handling
- **passlib**: Password hashing with bcrypt
- **redis**: In-memory data store client
- **alembic**: Database migration tool
- **uvicorn**: ASGI web server

## Security Considerations

### 1. Password Storage
- Passwords are hashed using bcrypt with a minimum of 12 rounds
- Never store plain-text passwords in the database
- Use the `hash_password()` function from `app/utils/hash.py`

### 2. JWT Tokens
- Access tokens have a configurable expiration time (default: 30 minutes)
- Refresh tokens are used to obtain new access tokens
- `JWT_SECRET_KEY` must be strong (minimum 32 characters)
- Always use HTTPS in production

### 3. OAuth 2.0 Best Practices
- Redirect URIs must be whitelisted per client
- Authorization codes expire after 10 minutes
- Client credentials must be securely transmitted
- PKCE (Proof Key for Code Exchange) recommended for public clients

### 4. Session Management
- Sessions are stored in Redis with automatic expiration
- Session data is encrypted before storage
- Use secure, HttpOnly cookies in production

### 5. Database Security
- Enable SSL connections to PostgreSQL in production
- Use strong, unique passwords for database users
- Regularly backup the database
- Implement row-level security policies

### 6. Redis Security
- Set a strong `REDIS_PASSWORD`
- Use Redis with encryption in production
- Restrict Redis access to trusted networks
- Enable Redis persistence with AOF (Append-Only File)

### 7. Environment Variables
- Never commit `.env` file to version control
- Use secret management tools (AWS Secrets Manager, HashiCorp Vault) in production
- Rotate secrets regularly
- Implement comprehensive logging (without leaking secrets)

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d sso_identity_db

# Check migration status
alembic current
```

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli -h localhost -p 6379 ping
```

### Port Already in Use
```bash
# Change the port in the uvicorn command
uvicorn app.main:app --port 5000
```

### Clear Database (Development Only)
```bash
# Drop all tables and recreate schema
alembic downgrade base
alembic upgrade head
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Write docstrings for all functions and classes
- Include type hints in function signatures
- Add unit tests for new features
- Run linting before committing: `flake8 app/`

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue in the repository or contact the development team.

---

**Last Updated**: January 2026
**Version**: 0.0.1
**Status**: Active Development
