"""
WebSocket endpoint for real-time exercise tracking.

Flow:
1. Client connects with exercise type and member_id
2. Client sends base64-encoded video frames
3. Server processes frames through PoseEngine → ExerciseTracker
4. Server streams back real-time state, rep count, form score, feedback
5. On disconnect, session is saved to MongoDB and Kafka event is published
"""

import base64
import json
import time
from datetime import datetime

import numpy as np
from PIL import Image
import io

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.exercise_tracker import create_tracker
from app.services.exercise_session_service import ExerciseSessionService

router = APIRouter()
logger = structlog.get_logger()

# Try to import PoseEngine — may not be available in test/CI
try:
    from app.services.pose_engine import PoseEngine

    POSE_ENGINE_AVAILABLE = True
except Exception:
    POSE_ENGINE_AVAILABLE = False


@router.websocket("/ws/exercise/{exercise_type}")
async def exercise_websocket(websocket: WebSocket, exercise_type: str):
    """
    Real-time exercise tracking via WebSocket.

    Query params:
        member_id: optional member ID to save session on disconnect

    Message format (client → server):
        {"frame": "<base64-encoded-jpeg>"}

    Message format (server → client):
        {
            "state": "GOING_DOWN",
            "rep_count": 3,
            "completed_rep": false,
            "rep_score": null,
            "avg_form_score": 85.2,
            "feedback": ["Control the descent"],
            "angles": {"left_knee": 120.5, "right_knee": 118.3, "primary": 119.4},
            "landmarks": {...}
        }
    """
    await websocket.accept()

    member_id = websocket.query_params.get("member_id", "anonymous")

    # Validate exercise type
    try:
        tracker = create_tracker(exercise_type)
    except ValueError as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close(code=4000)
        return

    # Initialize pose engine
    pose_engine = None
    if POSE_ENGINE_AVAILABLE:
        try:
            pose_engine = PoseEngine()
            logger.info("pose_engine_ready", exercise=exercise_type)
        except Exception as e:
            logger.warning("pose_engine_init_failed", error=str(e))
    else:
        logger.warning("pose_engine_not_available")

    started_at = datetime.utcnow()
    start_time = time.monotonic()
    rep_details: list[dict] = []
    frame_count = 0

    logger.info(
        "exercise_ws_connected",
        exercise=exercise_type,
        member_id=member_id,
    )

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            frame_b64 = data.get("frame")
            if not frame_b64:
                await websocket.send_json({"error": "Missing 'frame' field"})
                continue

            frame_count += 1
            angles = {}
            landmarks = None

            if pose_engine:
                try:
                    # Decode base64 → PIL Image → numpy RGB array
                    img_bytes = base64.b64decode(frame_b64)
                    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    frame_array = np.array(img)

                    # Extract landmarks
                    landmarks = pose_engine.process_frame(frame_array)

                    if landmarks:
                        angles = pose_engine.get_exercise_angles(
                            landmarks, exercise_type
                        )

                    # Log detection status periodically
                    if frame_count % 30 == 0:
                        logger.info(
                            "frame_status",
                            frame=frame_count,
                            pose_detected=landmarks is not None,
                            primary_angle=angles.get("primary"),
                        )
                except Exception as e:
                    logger.warning(
                        "frame_processing_error",
                        frame=frame_count,
                        error=str(e),
                    )

            # Run state machine with primary angle
            primary_angle = angles.get("primary")
            result = tracker.update(primary_angle)

            # Track completed reps
            if result["completed_rep"]:
                rep_details.append(
                    {
                        "rep_number": result["rep_count"],
                        "score": result["rep_score"],
                        "feedback": result["feedback"],
                    }
                )

            # Build response
            response = {
                **result,
                "angles": angles,
                "landmarks": landmarks,
                "frame_number": frame_count,
            }

            await websocket.send_json(response)

    except WebSocketDisconnect:
        logger.info(
            "exercise_ws_disconnected",
            exercise=exercise_type,
            member_id=member_id,
            total_reps=tracker.rep_count,
            frames_processed=frame_count,
        )
    finally:
        # Clean up pose engine
        if pose_engine:
            try:
                pose_engine.close()
            except Exception:
                pass

        # Save session if any reps were completed
        duration = int(time.monotonic() - start_time)
        if tracker.rep_count > 0 and member_id != "anonymous":
            try:
                avg_score = (
                    round(sum(tracker.form_scores) / len(tracker.form_scores), 1)
                    if tracker.form_scores
                    else None
                )
                await ExerciseSessionService.save_session(
                    member_id=member_id,
                    exercise=exercise_type,
                    total_reps=tracker.rep_count,
                    avg_form_score=avg_score,
                    rep_details=rep_details,
                    duration_seconds=duration,
                    started_at=started_at,
                )
            except Exception as e:
                logger.error("session_save_failed", error=str(e))
