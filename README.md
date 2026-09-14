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

- Python
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- Docker
- AWS ECS/Fargate
- AWS RDS
- AWS ECR
- AWS CloudWatch

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

## Local Setup

Clone the repository:

```bash
git clone https://github.com/mqazi3/finflow-api.git
cd finflow-api
