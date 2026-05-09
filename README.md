# FinFlow API

Cloud-deployed financial transaction management backend built with FastAPI, PostgreSQL, Redis, Docker, and AWS ECS/Fargate.

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