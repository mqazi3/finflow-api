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

- JWT authentication
- User registration and login
- Account creation and balance tracking
- Transaction creation and retrieval
- Transaction filtering and pagination
- Financial analytics endpoints
- Redis integration
- PostgreSQL persistence with SQLAlchemy ORM
- Health monitoring endpoints
- Dockerized deployment

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
| POST | `/api/v1/login` | Authenticate and receive JWT token |
| POST | `/api/v1/accounts` | Create a financial account |
| POST | `/api/v1/transactions` | Create a transaction |
| GET | `/api/v1/transactions` | Retrieve transactions with filters |
| GET | `/api/v1/analytics/transactions` | Retrieve transaction analytics |
| GET | `/health/full` | Check API, database, and Redis status |

## Local Setup

Clone the repository:

```bash
git clone https://github.com/mqazi3/finflow-api.git
cd finflow-api
