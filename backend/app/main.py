from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.mongodb import connect_mongodb, close_mongodb
from app.db.redis import connect_redis, close_redis
from app.services.kafka_service import start_producer, stop_producer

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("starting_fithub", app=settings.app_name)
    await connect_mongodb()
    await connect_redis()
    try:
        await start_producer()
    except Exception as e:
        logger.warning("kafka_producer_failed", error=str(e))
    yield
    # Shutdown
    await stop_producer()
    await close_redis()
    await close_mongodb()
    logger.info("fithub_stopped")


app = FastAPI(
    title=settings.app_name,
    description="Gym management platform with AI-powered exercise tracking",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health Checks ---
@app.get("/health/live", tags=["Health"])
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness():
    checks = {}
    try:
        from app.db.mongodb import get_database
        db = get_database()
        await db.command("ping")
        checks["mongodb"] = "ok"
    except Exception:
        checks["mongodb"] = "unavailable"

    try:
        from app.db.redis import get_redis
        redis = get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "unavailable"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}


# --- Register Routers ---
from app.api.members import router as members_router
from app.api.classes import router as classes_router
from app.api.workouts import router as workouts_router
from app.api.analytics import router as analytics_router

app.include_router(members_router)
app.include_router(classes_router)
app.include_router(workouts_router)
app.include_router(analytics_router)
