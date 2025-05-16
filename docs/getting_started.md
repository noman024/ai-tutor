# Getting Started with AI Tutor

AI Tutor is a full-stack educational platform combining FastAPI, Next.js, PostgreSQL, Redis, and Docker. This guide will help you set up the project and understand the key development commands used so far.

---

## 1. Clone the Repository
```bash
git clone https://github.com/noman024/ai-tutor.git
cd ai-tutor
```

## 2. Environment Setup
- Copy and edit environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## 3. Build and Start All Services
```bash
docker-compose up --build
# Or in detached mode
docker-compose up -d --build
```

## 4. Useful Development Commands

### Docker & Containers
- Start all services:
  ```bash
  docker-compose up -d
  ```
- Stop all services:
  ```bash
  docker-compose stop
  ```
- View running containers:
  ```bash
  docker ps
  ```
- View logs for a service:
  ```bash
  docker-compose logs backend
  docker-compose logs frontend
  docker-compose logs db
  docker-compose logs redis
  docker-compose logs pgadmin
  docker-compose logs redis-commander
  ```
- Restart a service:
  ```bash
  docker-compose restart backend
  ```
- Remove all containers (keep data):
  ```bash
  docker-compose down
  ```
- Remove all containers and volumes (delete all data!):
  ```bash
  docker-compose down -v
  ```

### Database & Migrations
- Create a new migration:
  ```bash
  cd backend
  PYTHONPATH=.. alembic revision --autogenerate -m "migration message"
  ```
- Apply migrations:
  ```bash
  cd backend
  PYTHONPATH=.. alembic upgrade head
  ```

### Backend
- Run backend locally (if not using Docker):
  ```bash
  cd backend
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- Run backend tests:
  ```bash
  docker-compose exec backend pytest
  ```

### Frontend
- Run frontend locally (if not using Docker):
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- Run frontend tests:
  ```bash
  docker-compose exec frontend npm test
  ```

### Redis & pgAdmin
- Access Redis Commander: http://localhost:8081
- Access pgAdmin: http://localhost:5050

---

## 5. Troubleshooting
- If you lose your database or pgAdmin setup, make sure you are not using `docker-compose down -v` unless you want to delete all data.
- For persistent pgAdmin setup, a volume is now configured in `docker-compose.yml`.

---

For more details, see the main [README.md](../README.md). 