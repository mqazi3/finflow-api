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
```

## Features

- User registration and login with JWT-based authentication
- Password hashing with bcrypt
- Authenticated, user-scoped account and transaction access
- User-scoped account and transaction operations with ownership checks
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

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/register` | Register a new user |
| POST | `/api/v1/login` | Authenticate a user and issue a JWT bearer token |

### Accounts

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/accounts/` | Create an account for the authenticated user |
| GET | `/api/v1/accounts/` | Retrieve accounts belonging to the authenticated user |

### Transactions

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/transactions/` | Create a transaction |
| GET | `/api/v1/transactions/` | Query user transactions with filtering, search, and pagination |
| GET | `/api/v1/transactions/count` | Count transactions using optional category and search filters |
| GET | `/api/v1/transactions/{transaction_id}` | Retrieve a specific user-owned transaction |
| PUT | `/api/v1/transactions/{transaction_id}` | Update a transaction and recalculate its account balance |
| DELETE | `/api/v1/transactions/{transaction_id}` | Delete a transaction and update its account balance |

### Analytics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/analytics/transactions` | Retrieve transaction-level financial analytics |
| GET | `/api/v1/analytics/categories` | Summarize transactions by category |
| GET | `/api/v1/analytics/monthly` | Retrieve monthly analytics with optional date-range filtering |
| GET | `/api/v1/analytics/merchants` | Summarize transaction activity by merchant |
| GET | `/api/v1/analytics/top-merchants` | Retrieve top spending merchants |

### Health & Service Information

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Service entry point and API metadata |
| GET | `/info` | Application version, environment, and feature information |
| GET | `/health` | Basic application health check |
| GET | `/health/db` | PostgreSQL connectivity check |
| GET | `/health/redis` | Redis connectivity check |
| GET | `/health/full` | Combined application, PostgreSQL, and Redis health check |

## Authentication & Authorization

FinFlow uses JWT-based authentication to protect user data and API operations.

- Passwords are hashed using bcrypt before storage
- Successful login issues a JWT bearer token
- Protected endpoints resolve the authenticated user from the token
- Account and transaction queries are scoped to the authenticated user
- User-specific transaction lookups return `404` when the transaction is missing or not owned by the current user

## Data Model & Caching

FinFlow uses a relational data model centered on users, accounts, and transactions.

- Users own one or more financial accounts
- Accounts contain transaction records
- Transaction creation updates the associated account balance
- PostgreSQL stores persistent application data through SQLAlchemy
- Redis caches per-user transaction analytics using keys scoped by user ID
- Cached transaction analytics use a 60-second TTL to reduce repeated database queries

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
