"""
Seed script to populate the database with demo data.
Run with: python -m app.seed
"""

import asyncio
from datetime import datetime, timedelta
from bson import ObjectId

from app.db.mongodb import connect_mongodb, get_database, close_mongodb


MEMBERS = [
    {
        "_id": ObjectId(),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+31612345678",
        "membership": {"plan": "premium", "status": "active", "start_date": datetime(2024, 6, 1), "end_date": None},
        "profile": {"age": 28, "weight": 80.0, "height": 180.0, "fitness_level": "intermediate", "goals": ["muscle_gain"]},
        "created_at": datetime(2024, 6, 1),
        "updated_at": datetime(2024, 6, 1),
        "is_deleted": False,
    },
    {
        "_id": ObjectId(),
        "first_name": "Emma",
        "last_name": "Wilson",
        "email": "emma.wilson@example.com",
        "phone": "+31698765432",
        "membership": {"plan": "basic", "status": "active", "start_date": datetime(2024, 9, 15), "end_date": None},
        "profile": {"age": 32, "weight": 62.0, "height": 168.0, "fitness_level": "beginner", "goals": ["weight_loss", "flexibility"]},
        "created_at": datetime(2024, 9, 15),
        "updated_at": datetime(2024, 9, 15),
        "is_deleted": False,
    },
    {
        "_id": ObjectId(),
        "first_name": "Carlos",
        "last_name": "Garcia",
        "email": "carlos.garcia@example.com",
        "phone": "+31645678901",
        "membership": {"plan": "pt", "status": "active", "start_date": datetime(2024, 3, 1), "end_date": None},
        "profile": {"age": 25, "weight": 90.0, "height": 185.0, "fitness_level": "advanced", "goals": ["strength", "competition"]},
        "created_at": datetime(2024, 3, 1),
        "updated_at": datetime(2024, 3, 1),
        "is_deleted": False,
    },
    {
        "_id": ObjectId(),
        "first_name": "Sophie",
        "last_name": "van der Berg",
        "email": "sophie.vdb@example.com",
        "phone": "+31634567890",
        "membership": {"plan": "premium", "status": "frozen", "start_date": datetime(2024, 1, 1), "end_date": None},
        "profile": {"age": 41, "weight": 70.0, "height": 172.0, "fitness_level": "intermediate", "goals": ["health"]},
        "created_at": datetime(2024, 1, 1),
        "updated_at": datetime(2025, 1, 1),
        "is_deleted": False,
    },
    {
        "_id": ObjectId(),
        "first_name": "Amir",
        "last_name": "Hassan",
        "email": "amir.hassan@example.com",
        "phone": "+31678901234",
        "membership": {"plan": "basic", "status": "active", "start_date": datetime(2025, 1, 10), "end_date": None},
        "profile": {"age": 22, "weight": 72.0, "height": 175.0, "fitness_level": "beginner", "goals": ["general_fitness"]},
        "created_at": datetime(2025, 1, 10),
        "updated_at": datetime(2025, 1, 10),
        "is_deleted": False,
    },
]

CLASSES = [
    {
        "_id": ObjectId(),
        "name": "Morning Yoga",
        "description": "Start your day with a peaceful yoga session",
        "instructor": "Sarah",
        "category": "yoga",
        "schedule": {"day_of_week": 1, "start_time": "09:00", "end_time": "10:00", "recurring": True},
        "capacity": 20,
        "current_bookings": 12,
        "participants": [MEMBERS[0]["_id"], MEMBERS[1]["_id"]],
        "location": "Studio A",
        "status": "scheduled",
        "created_at": datetime(2025, 1, 1),
    },
    {
        "_id": ObjectId(),
        "name": "HIIT Blast",
        "description": "High intensity interval training for maximum burn",
        "instructor": "Mike",
        "category": "hiit",
        "schedule": {"day_of_week": 2, "start_time": "18:00", "end_time": "19:00", "recurring": True},
        "capacity": 15,
        "current_bookings": 15,
        "participants": [MEMBERS[0]["_id"], MEMBERS[2]["_id"]],
        "location": "Main Floor",
        "status": "scheduled",
        "created_at": datetime(2025, 1, 1),
    },
    {
        "_id": ObjectId(),
        "name": "Strength Fundamentals",
        "description": "Build a solid foundation with compound lifts",
        "instructor": "Coach Alex",
        "category": "strength",
        "schedule": {"day_of_week": 3, "start_time": "17:00", "end_time": "18:30", "recurring": True},
        "capacity": 10,
        "current_bookings": 7,
        "participants": [MEMBERS[2]["_id"]],
        "location": "Weight Room",
        "status": "scheduled",
        "created_at": datetime(2025, 1, 1),
    },
    {
        "_id": ObjectId(),
        "name": "Pilates Flow",
        "description": "Core strengthening and flexibility",
        "instructor": "Sarah",
        "category": "pilates",
        "schedule": {"day_of_week": 4, "start_time": "10:00", "end_time": "11:00", "recurring": True},
        "capacity": 18,
        "current_bookings": 8,
        "participants": [MEMBERS[1]["_id"]],
        "location": "Studio A",
        "status": "scheduled",
        "created_at": datetime(2025, 1, 1),
    },
]

WORKOUT_PLANS = [
    {
        "_id": ObjectId(),
        "name": "Beginner Full Body",
        "description": "A balanced full body workout for newcomers",
        "difficulty": "beginner",
        "exercises": [
            {"exercise_id": None, "name": "Squat", "sets": 3, "reps": 12, "rest_seconds": 60, "notes": "Keep back straight"},
            {"exercise_id": None, "name": "Push-up", "sets": 3, "reps": 10, "rest_seconds": 60, "notes": ""},
            {"exercise_id": None, "name": "Dumbbell Row", "sets": 3, "reps": 10, "rest_seconds": 60, "notes": "Each side"},
            {"exercise_id": None, "name": "Plank", "sets": 3, "reps": 30, "rest_seconds": 45, "notes": "30 seconds hold"},
        ],
        "estimated_duration_minutes": 45,
        "created_by": "Coach Mike",
        "created_at": datetime(2025, 1, 1),
    },
    {
        "_id": ObjectId(),
        "name": "Advanced Strength",
        "description": "Heavy compound lifts for experienced lifters",
        "difficulty": "advanced",
        "exercises": [
            {"exercise_id": None, "name": "Barbell Squat", "sets": 5, "reps": 5, "rest_seconds": 180, "notes": "80% 1RM"},
            {"exercise_id": None, "name": "Bench Press", "sets": 5, "reps": 5, "rest_seconds": 180, "notes": "80% 1RM"},
            {"exercise_id": None, "name": "Deadlift", "sets": 5, "reps": 5, "rest_seconds": 180, "notes": "80% 1RM"},
            {"exercise_id": None, "name": "Overhead Press", "sets": 4, "reps": 8, "rest_seconds": 120, "notes": ""},
        ],
        "estimated_duration_minutes": 75,
        "created_by": "Coach Alex",
        "created_at": datetime(2025, 1, 1),
    },
]


async def seed():
    await connect_mongodb()
    db = get_database()

    print("Clearing existing data...")
    await db["members"].delete_many({})
    await db["classes"].delete_many({})
    await db["workout_plans"].delete_many({})
    await db["workout_logs"].delete_many({})
    await db["workout_assignments"].delete_many({})

    print("Seeding members...")
    await db["members"].insert_many(MEMBERS)
    print(f"  Inserted {len(MEMBERS)} members")

    print("Seeding classes...")
    await db["classes"].insert_many(CLASSES)
    print(f"  Inserted {len(CLASSES)} classes")

    print("Seeding workout plans...")
    await db["workout_plans"].insert_many(WORKOUT_PLANS)
    print(f"  Inserted {len(WORKOUT_PLANS)} workout plans")

    # Create some workout logs
    logs = []
    for i in range(15):
        logs.append({
            "_id": ObjectId(),
            "member_id": MEMBERS[i % len(MEMBERS)]["_id"],
            "plan_id": WORKOUT_PLANS[i % len(WORKOUT_PLANS)]["_id"],
            "completed_at": datetime.utcnow() - timedelta(days=i),
            "duration_minutes": 30 + (i * 5 % 45),
            "exercises_completed": [
                {
                    "exercise_name": "Squat",
                    "sets_completed": 3,
                    "reps_per_set": [12, 12, 10],
                    "form_score": 70 + (i * 3 % 30),
                },
            ],
            "source": "manual" if i % 3 != 0 else "ai_tracker",
        })

    await db["workout_logs"].insert_many(logs)
    print(f"  Inserted {len(logs)} workout logs")

    # Create indexes
    print("Creating indexes...")
    await db["members"].create_index("email", unique=True)
    await db["members"].create_index([("first_name", 1), ("last_name", 1)])
    await db["members"].create_index("membership.status")
    await db["members"].create_index("membership.plan")
    await db["classes"].create_index("category")
    await db["classes"].create_index("schedule.day_of_week")
    await db["workout_logs"].create_index("member_id")
    await db["workout_logs"].create_index("completed_at")

    print("Seed complete!")
    await close_mongodb()


if __name__ == "__main__":
    asyncio.run(seed())
