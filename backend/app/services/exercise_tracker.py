"""
Exercise Tracker — state machine for counting reps and scoring form.

Each exercise type has its own tracker subclass that defines:
- angle thresholds for state transitions
- form scoring rules
- real-time feedback generation
"""

from abc import ABC, abstractmethod
from enum import Enum

import structlog

logger = structlog.get_logger()


class ExerciseState(str, Enum):
    IDLE = "IDLE"
    GOING_DOWN = "GOING_DOWN"
    DOWN = "DOWN"
    GOING_UP = "GOING_UP"
    UP = "UP"


class BaseTracker(ABC):
    """Base class for exercise-specific trackers."""

    def __init__(self):
        self.state = ExerciseState.IDLE
        self.rep_count = 0
        self.form_scores: list[float] = []
        self._rep_angles: list[float] = []  # angles collected during current rep
        self._prev_angle: float | None = None

    @property
    @abstractmethod
    def exercise_name(self) -> str: ...

    @property
    @abstractmethod
    def down_threshold(self) -> float:
        """Angle below which we consider 'DOWN' position."""
        ...

    @property
    @abstractmethod
    def up_threshold(self) -> float:
        """Angle above which we consider 'UP' position."""
        ...

    @abstractmethod
    def score_rep(self, angles: list[float]) -> float:
        """Score the form of a completed rep (0-100)."""
        ...

    @abstractmethod
    def generate_feedback(self, angle: float, state: ExerciseState) -> list[str]:
        """Generate real-time coaching feedback."""
        ...

    def update(self, primary_angle: float | None) -> dict:
        """
        Update the state machine with a new angle reading.
        Returns the current state, rep count, and any completed rep info.
        """
        if primary_angle is None:
            return self._build_result(completed_rep=False)

        self._rep_angles.append(primary_angle)
        completed_rep = False
        rep_score = None

        prev_state = self.state

        if self.state == ExerciseState.IDLE:
            if self._prev_angle and primary_angle < self._prev_angle - 2:
                self.state = ExerciseState.GOING_DOWN

        elif self.state == ExerciseState.GOING_DOWN:
            if primary_angle <= self.down_threshold:
                self.state = ExerciseState.DOWN
            elif self._prev_angle and primary_angle > self._prev_angle + 5:
                # Changed direction without reaching bottom — reset
                self.state = ExerciseState.IDLE
                self._rep_angles.clear()

        elif self.state == ExerciseState.DOWN:
            if self._prev_angle and primary_angle > self._prev_angle + 2:
                self.state = ExerciseState.GOING_UP

        elif self.state == ExerciseState.GOING_UP:
            if primary_angle >= self.up_threshold:
                self.state = ExerciseState.UP

        elif self.state == ExerciseState.UP:
            # Rep completed
            self.rep_count += 1
            rep_score = self.score_rep(self._rep_angles)
            self.form_scores.append(rep_score)
            completed_rep = True
            self._rep_angles.clear()
            self.state = ExerciseState.IDLE

        self._prev_angle = primary_angle

        if prev_state != self.state:
            logger.info(
                "state_transition",
                exercise=self.exercise_name,
                from_state=prev_state.value,
                to_state=self.state.value,
                angle=primary_angle,
            )

        feedback = self.generate_feedback(primary_angle, self.state)

        return self._build_result(
            completed_rep=completed_rep,
            rep_score=rep_score,
            feedback=feedback,
        )

    def _build_result(
        self,
        completed_rep: bool = False,
        rep_score: float | None = None,
        feedback: list[str] | None = None,
    ) -> dict:
        avg_score = (
            round(sum(self.form_scores) / len(self.form_scores), 1)
            if self.form_scores
            else None
        )
        return {
            "state": self.state.value,
            "rep_count": self.rep_count,
            "completed_rep": completed_rep,
            "rep_score": rep_score,
            "avg_form_score": avg_score,
            "feedback": feedback or [],
        }

    def reset(self):
        self.state = ExerciseState.IDLE
        self.rep_count = 0
        self.form_scores.clear()
        self._rep_angles.clear()
        self._prev_angle = None


class SquatTracker(BaseTracker):
    """
    Squat: tracks knee angle.
    DOWN = knee angle < 90° (deep squat)
    UP = knee angle > 160° (standing)
    """

    exercise_name = "squat"
    down_threshold = 90
    up_threshold = 160

    def score_rep(self, angles: list[float]) -> float:
        if not angles:
            return 50.0
        min_angle = min(angles)
        score = 100.0

        # Depth score: ideal is 60-90°, penalize if not deep enough
        if min_angle > 100:
            score -= (min_angle - 100) * 1.5  # shallow squat penalty
        elif min_angle < 50:
            score -= (50 - min_angle) * 1.0  # too deep penalty

        # Consistency: check for wobble during the rep
        if len(angles) > 5:
            diffs = [abs(angles[i] - angles[i - 1]) for i in range(1, len(angles))]
            avg_diff = sum(diffs) / len(diffs)
            if avg_diff > 8:
                score -= 10  # wobbly form

        return max(0, min(100, round(score, 1)))

    def generate_feedback(self, angle: float, state: ExerciseState) -> list[str]:
        feedback = []
        if state == ExerciseState.DOWN:
            if angle > 95:
                feedback.append("Go deeper — aim for 90° knee angle")
            elif angle < 50:
                feedback.append("Careful — you're going too deep")
            else:
                feedback.append("Good depth!")
        elif state == ExerciseState.GOING_DOWN:
            feedback.append("Control the descent")
        elif state == ExerciseState.UP:
            feedback.append("Great rep!")
        return feedback


class BicepCurlTracker(BaseTracker):
    """
    Bicep Curl: tracks elbow angle.
    DOWN = elbow angle > 160° (arm extended)
    UP = elbow angle < 40° (arm curled)

    Note: inverted compared to squat — arm starts extended (high angle)
    and curls up (low angle). We swap the logic accordingly.
    """

    exercise_name = "bicep_curl"
    down_threshold = 40  # curled position (low angle = top of curl)
    up_threshold = 160  # extended position

    def update(self, primary_angle: float | None) -> dict:
        """
        Override: bicep curl has inverted motion.
        Angle decreases going UP (curling), increases going DOWN (extending).
        """
        if primary_angle is None:
            return self._build_result(completed_rep=False)

        self._rep_angles.append(primary_angle)
        completed_rep = False
        rep_score = None
        prev_state = self.state

        if self.state == ExerciseState.IDLE:
            if self._prev_angle and primary_angle < self._prev_angle - 2:
                self.state = ExerciseState.GOING_DOWN  # curling up (angle decreasing)

        elif self.state == ExerciseState.GOING_DOWN:
            if primary_angle <= self.down_threshold:
                self.state = ExerciseState.DOWN  # fully curled

        elif self.state == ExerciseState.DOWN:
            if self._prev_angle and primary_angle > self._prev_angle + 2:
                self.state = ExerciseState.GOING_UP  # extending

        elif self.state == ExerciseState.GOING_UP:
            if primary_angle >= self.up_threshold:
                self.state = ExerciseState.UP  # fully extended

        elif self.state == ExerciseState.UP:
            self.rep_count += 1
            rep_score = self.score_rep(self._rep_angles)
            self.form_scores.append(rep_score)
            completed_rep = True
            self._rep_angles.clear()
            self.state = ExerciseState.IDLE

        self._prev_angle = primary_angle

        if prev_state != self.state:
            logger.info(
                "state_transition",
                exercise=self.exercise_name,
                from_state=prev_state.value,
                to_state=self.state.value,
                angle=primary_angle,
            )

        feedback = self.generate_feedback(primary_angle, self.state)
        return self._build_result(
            completed_rep=completed_rep,
            rep_score=rep_score,
            feedback=feedback,
        )

    def score_rep(self, angles: list[float]) -> float:
        if not angles:
            return 50.0
        min_angle = min(angles)
        max_angle = max(angles)
        score = 100.0

        # Full range of motion check
        rom = max_angle - min_angle
        if rom < 100:
            score -= (100 - rom) * 0.5  # incomplete range

        # Top curl check
        if min_angle > 50:
            score -= (min_angle - 50) * 1.0

        # Full extension check
        if max_angle < 150:
            score -= (150 - max_angle) * 0.5

        return max(0, min(100, round(score, 1)))

    def generate_feedback(self, angle: float, state: ExerciseState) -> list[str]:
        feedback = []
        if state == ExerciseState.DOWN:
            if angle > 50:
                feedback.append("Curl higher — squeeze at the top")
            else:
                feedback.append("Good curl!")
        elif state == ExerciseState.GOING_UP:
            feedback.append("Extend fully — control the negative")
        elif state == ExerciseState.UP:
            feedback.append("Great rep!")
        return feedback


class ShoulderPressTracker(BaseTracker):
    """
    Shoulder Press: tracks shoulder angle (hip-shoulder-elbow).
    DOWN = shoulder angle < 90° (arms at shoulder level)
    UP = shoulder angle > 160° (arms overhead)
    """

    exercise_name = "shoulder_press"
    down_threshold = 90
    up_threshold = 160

    def score_rep(self, angles: list[float]) -> float:
        if not angles:
            return 50.0
        max_angle = max(angles)
        score = 100.0

        # Full lockout check
        if max_angle < 155:
            score -= (155 - max_angle) * 1.0

        # Starting position check
        min_angle = min(angles)
        if min_angle > 100:
            score -= (min_angle - 100) * 0.5

        return max(0, min(100, round(score, 1)))

    def generate_feedback(self, angle: float, state: ExerciseState) -> list[str]:
        feedback = []
        if state == ExerciseState.UP:
            if angle < 155:
                feedback.append("Press higher — full lockout")
            else:
                feedback.append("Great lockout!")
        elif state == ExerciseState.DOWN:
            feedback.append("Good starting position")
        elif state == ExerciseState.GOING_UP:
            feedback.append("Drive it up!")
        return feedback


# --- Factory ---

TRACKERS = {
    "squat": SquatTracker,
    "bicep_curl": BicepCurlTracker,
    "shoulder_press": ShoulderPressTracker,
}


def create_tracker(exercise: str) -> BaseTracker:
    tracker_cls = TRACKERS.get(exercise)
    if not tracker_cls:
        raise ValueError(
            f"Unknown exercise: {exercise}. Available: {list(TRACKERS.keys())}"
        )
    return tracker_cls()
