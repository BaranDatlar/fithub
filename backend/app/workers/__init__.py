import asyncio
import structlog

from app.workers.analytics_worker import AnalyticsWorker
from app.workers.workout_summary_worker import WorkoutSummaryWorker
from app.workers.notification_worker import NotificationWorker
from app.db.mongodb import connect_mongodb
from app.db.redis import connect_redis

logger = structlog.get_logger()


async def run_workers():
    await connect_mongodb()
    await connect_redis()

    analytics = AnalyticsWorker()
    workout_summary = WorkoutSummaryWorker()
    notification = NotificationWorker()

    logger.info("starting_all_workers")
    await asyncio.gather(
        analytics.run(),
        workout_summary.run(),
        notification.run(),
    )


if __name__ == "__main__":
    asyncio.run(run_workers())
