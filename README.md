# FinFlow API

A cloud-deployed financial transaction backend built with Python, FastAPI, PostgreSQL, Redis, Docker, and AWS ECS/Fargate.

FinFlow provides authenticated, user-scoped APIs for managing financial accounts and transactions, querying transaction data, and generating financial analytics. The application uses PostgreSQL for persistent storage and Redis for caching analytics results.

## Architecture

FinFlow uses a containerized backend architecture deployed on AWS:

- **API:** FastAPI application running in Docker on AWS ECS/Fargate
- **Database:** PostgreSQL hosted on Amazon RDS
- **Caching:** Redis hosted on Amazon ElastiCache
- **Container Registry:** Amazon ECR
- **Logging:** Amazon CloudWatch
- **Authentication:** JWT-based authentication with password hashing

```text
Client
  |
  v
FastAPI API
(AWS ECS/Fargate)
  |
  +-----------> PostgreSQL
  |             (Amazon RDS)
  |
  +-----------> Redis
                (Amazon ElastiCache)

Docker Image -> Amazon ECR
Application Logs -> Amazon CloudWatch

## Features

- User registration and login with JWT-based authentication
- Password hashing with bcrypt
- Authenticated, user-scoped account and transaction access
- Account ownership validation
- Transaction creation and retrieval
- Search and filtering by transaction attributes
- Pagination for transaction queries
- Financial analytics including transaction totals, deposits, withdrawals, balances, and flagged transactions
- Redis caching for per-user analytics with a 60-second TTL
- PostgreSQL persistence using SQLAlchemy
- Application and dependency health-check endpoints
- Dockerized local and cloud deployment

## Tech Stack

| Category | Technologies |
|---|---|
| Language & API | Python, FastAPI |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Caching | Redis |
| Authentication | JWT, bcrypt |
| Containerization | Docker |
| AWS | ECS/Fargate, ECR, RDS, ElastiCache, CloudWatch |

## Project Structure

```text
finflow-api/
├── app/
│   ├── dependencies/     # Shared FastAPI dependencies
│   ├── models/           # SQLAlchemy database models
│   ├── routes/           # API route definitions
│   ├── schemas/          # Request and response schemas
│   ├── services/         # Application and business logic
│   ├── storage/          # Data storage functionality
│   ├── auth.py           # Authentication and JWT utilities
│   ├── cache.py          # Redis caching configuration
│   ├── config.py         # Application configuration
│   ├── database.py       # Database connection and session setup
│   ├── logger.py         # Logging configuration
│   └── main.py           # FastAPI application entry point
├── alembic/              # Database migration files
├── .env.example          # Example environment configuration
├── Dockerfile            # API container definition
├── docker-compose.yml    # Local multi-container environment
├── alembic.ini           # Alembic configuration
└── requirements.txt      # Python dependencies
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/register` | Register a new user |
| POST | `/api/v1/login` | Authenticate a user and issue a JWT access token |
| POST | `/api/v1/accounts` | Create an authenticated user's financial account |
| POST | `/api/v1/transactions` | Create a transaction for a user-owned account |
| GET | `/api/v1/transactions` | Query transactions with filtering and pagination |
| GET | `/api/v1/analytics/transactions` | Retrieve user-scoped transaction analytics |
| GET | `/health/full` | Check API, PostgreSQL, and Redis connectivity |

## Authentication & Authorization

FinFlow uses JWT-based authentication to protect user data and API operations.

- Passwords are hashed using bcrypt before storage
- Successful login issues a JWT access token
- Protected endpoints resolve the authenticated user from the token
- Account and transaction queries are scoped to the authenticated user
- Account ownership is validated before user-specific operations
- Unauthorized users cannot access another user's account data

## Data Model & Caching

FinFlow uses a relational data model centered on users, accounts, and transactions.

- Users own one or more financial accounts
- Accounts contain transaction records
- Transaction creation updates the associated account balance
- PostgreSQL stores persistent application data through SQLAlchemy
- Redis caches per-user analytics results
- Cached analytics use a 60-second TTL to reduce repeated database work for frequently requested summaries

## Cloud Deployment

FinFlow was containerized with Docker and deployed to AWS using managed application, database, and caching services.

- Docker image stored in Amazon ECR
- FastAPI application deployed on Amazon ECS with Fargate
- PostgreSQL database hosted on Amazon RDS
- Redis cache hosted on Amazon ElastiCache
- Application logs monitored through Amazon CloudWatch
- Deployment required configuring service connectivity, environment variables, and network access between ECS, RDS, and ElastiCache

During deployment, I troubleshot database connectivity, AWS security-group and networking configuration, application environment settings, and service-to-service communication between the API, PostgreSQL, and Redis.

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/mqazi3/finflow-api.git
cd finflow-api
```

### 2. Configure environment variables

Create a `.env` file with the required database, Redis, and authentication configuration.

Do not commit credentials or secrets to source control.

### 3. Start the application

The project includes Docker configuration for running the API and its supporting services in containers.

```bash
docker compose up --build
```

### 4. Explore the API

Once the application is running, FastAPI provides interactive API documentation at:

```text
http://localhost:8000/docs
```

Use the Swagger UI to register a user, authenticate, create accounts and transactions, query transaction data, and test analytics endpoints.
