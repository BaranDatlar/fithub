"""
MediaPipe Pose Engine — extracts body landmarks and calculates joint angles.

Uses MediaPipe Pose to detect 33 body landmarks from an image frame,
then computes angles between specified joints for exercise form analysis.
"""

import math

import numpy as np

try:
    import mediapipe as mp

    mp_pose = mp.solutions.pose
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp_pose = None

import structlog

logger = structlog.get_logger()

# Landmark indices (MediaPipe Pose)
LANDMARKS = {
    "NOSE": 0,
    "LEFT_SHOULDER": 11,
    "RIGHT_SHOULDER": 12,
    "LEFT_ELBOW": 13,
    "RIGHT_ELBOW": 14,
    "LEFT_WRIST": 15,
    "RIGHT_WRIST": 16,
    "LEFT_HIP": 23,
    "RIGHT_HIP": 24,
    "LEFT_KNEE": 25,
    "RIGHT_KNEE": 26,
    "LEFT_ANKLE": 27,
    "RIGHT_ANKLE": 28,
}


def calculate_angle(a: tuple, b: tuple, c: tuple) -> float:
    """
    Calculate the angle at point B formed by vectors BA and BC.

    Args:
        a: (x, y) coordinates of point A
        b: (x, y) coordinates of point B (vertex)
        c: (x, y) coordinates of point C

    Returns:
        Angle in degrees (0-180)
    """
    ba = np.array([a[0] - b[0], a[1] - b[1]])
    bc = np.array([c[0] - b[0], c[1] - b[1]])

    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    cosine = np.clip(cosine, -1.0, 1.0)
    angle = math.degrees(math.acos(cosine))
    return round(angle, 1)


class PoseEngine:
    """Wraps MediaPipe Pose for landmark detection and angle computation."""

    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("mediapipe is not installed")
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process_frame(self, frame: np.ndarray) -> dict | None:
        """
        Process an RGB image frame and extract pose landmarks.

        Returns dict with landmark positions and visibility, or None if no pose detected.
        """
        results = self.pose.process(frame)
        if not results.pose_landmarks:
            return None

        landmarks = {}
        for name, idx in LANDMARKS.items():
            lm = results.pose_landmarks.landmark[idx]
            landmarks[name] = {
                "x": round(lm.x, 4),
                "y": round(lm.y, 4),
                "z": round(lm.z, 4),
                "visibility": round(lm.visibility, 2),
            }

        return landmarks

    def get_angle(
        self, landmarks: dict, point_a: str, point_b: str, point_c: str
    ) -> float | None:
        """
        Calculate angle at point_b between point_a and point_c.
        Returns None if any landmark has low visibility.
        """
        for name in (point_a, point_b, point_c):
            if name not in landmarks:
                return None
            if landmarks[name]["visibility"] < 0.3:
                return None

        a = (landmarks[point_a]["x"], landmarks[point_a]["y"])
        b = (landmarks[point_b]["x"], landmarks[point_b]["y"])
        c = (landmarks[point_c]["x"], landmarks[point_c]["y"])

        return calculate_angle(a, b, c)

    def get_exercise_angles(self, landmarks: dict, exercise: str) -> dict:
        """Calculate relevant angles for a given exercise, using both sides."""
        angles = {}

        if exercise == "squat":
            angles["left_knee"] = self.get_angle(
                landmarks, "LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"
            )
            angles["right_knee"] = self.get_angle(
                landmarks, "RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE"
            )
            # Use the average of both knees for state machine
            valid = [v for v in [angles["left_knee"], angles["right_knee"]] if v]
            angles["primary"] = round(sum(valid) / len(valid), 1) if valid else None

        elif exercise == "bicep_curl":
            angles["left_elbow"] = self.get_angle(
                landmarks, "LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"
            )
            angles["right_elbow"] = self.get_angle(
                landmarks, "RIGHT_SHOULDER", "RIGHT_ELBOW", "RIGHT_WRIST"
            )
            valid = [v for v in [angles["left_elbow"], angles["right_elbow"]] if v]
            angles["primary"] = round(sum(valid) / len(valid), 1) if valid else None

        elif exercise == "shoulder_press":
            angles["left_shoulder"] = self.get_angle(
                landmarks, "LEFT_HIP", "LEFT_SHOULDER", "LEFT_ELBOW"
            )
            angles["right_shoulder"] = self.get_angle(
                landmarks, "RIGHT_HIP", "RIGHT_SHOULDER", "RIGHT_ELBOW"
            )
            valid = [
                v for v in [angles["left_shoulder"], angles["right_shoulder"]] if v
            ]
            angles["primary"] = round(sum(valid) / len(valid), 1) if valid else None

        return angles

    def close(self):
        self.pose.close()
