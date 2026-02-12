.PHONY: up down build logs test lint seed clean

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Rebuild and start
build:
	docker-compose up -d --build

# View logs
logs:
	docker-compose logs -f

# Backend logs only
logs-backend:
	docker-compose logs -f backend worker

# Run backend tests
test:
	docker-compose exec backend pytest app/tests/ -v

# Run linter
lint:
	docker-compose exec backend ruff check app/
	docker-compose exec backend ruff format --check app/

# Format code
format:
	docker-compose exec backend ruff format app/

# Seed database with demo data
seed:
	docker-compose exec backend python -m app.seed

# Clean everything (volumes included)
clean:
	docker-compose down -v --remove-orphans

# Show running services
status:
	docker-compose ps
