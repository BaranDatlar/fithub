"""Tests for the exercise tracker state machine."""

import pytest

from app.services.exercise_tracker import (
    ExerciseState,
    SquatTracker,
    BicepCurlTracker,
    ShoulderPressTracker,
    create_tracker,
)


class TestSquatTracker:
    def test_initial_state(self):
        tracker = SquatTracker()
        assert tracker.state == ExerciseState.IDLE
        assert tracker.rep_count == 0
        assert tracker.form_scores == []

    def test_full_rep_cycle(self):
        """Simulate a complete squat rep: stand → descend → bottom → ascend → stand."""
        tracker = SquatTracker()

        # Start standing (angle ~170°), begin descent
        tracker.update(170)
        tracker.update(167)  # trigger GOING_DOWN (167 < 170 - 2)
        assert tracker.state == ExerciseState.GOING_DOWN

        # Descend to bottom
        tracker.update(140)
        tracker.update(110)
        tracker.update(85)  # below down_threshold (90)
        assert tracker.state == ExerciseState.DOWN

        # Begin ascent
        tracker.update(88)  # trigger GOING_UP (+2 from prev)
        assert tracker.state == ExerciseState.GOING_UP

        # Rise to top
        tracker.update(120)
        tracker.update(150)
        result = tracker.update(162)  # above up_threshold (160)
        assert tracker.state == ExerciseState.UP

        # Next update completes the rep
        result = tracker.update(165)
        assert result["completed_rep"] is True
        assert result["rep_count"] == 1
        assert result["rep_score"] is not None
        assert tracker.state == ExerciseState.IDLE

    def test_multiple_reps(self):
        tracker = SquatTracker()

        for _ in range(3):
            # Stand → going down
            tracker.update(170)
            tracker.update(165)
            # Descend
            tracker.update(130)
            tracker.update(100)
            tracker.update(80)
            # Going up
            tracker.update(85)
            tracker.update(120)
            tracker.update(150)
            tracker.update(165)
            # Complete rep (UP state triggers on next update)
            tracker.update(170)

        assert tracker.rep_count == 3
        assert len(tracker.form_scores) == 3

    def test_none_angle_returns_result(self):
        tracker = SquatTracker()
        result = tracker.update(None)
        assert result["completed_rep"] is False
        assert result["state"] == "IDLE"

    def test_reset(self):
        tracker = SquatTracker()
        # Do a rep
        tracker.update(170)
        tracker.update(165)
        tracker.update(80)
        tracker.update(85)
        tracker.update(165)
        tracker.update(170)

        tracker.reset()
        assert tracker.state == ExerciseState.IDLE
        assert tracker.rep_count == 0
        assert tracker.form_scores == []

    def test_score_rep_good_form(self):
        tracker = SquatTracker()
        # Good depth range (60-90)
        angles = [170, 150, 120, 90, 75, 80, 90, 120, 150, 170]
        score = tracker.score_rep(angles)
        assert score >= 80

    def test_score_rep_shallow_squat(self):
        tracker = SquatTracker()
        # Shallow — min angle > 100
        angles = [170, 150, 130, 115, 110, 120, 140, 160, 170]
        score = tracker.score_rep(angles)
        assert score < 90  # penalized

    def test_generate_feedback_at_bottom(self):
        tracker = SquatTracker()
        # Good depth
        fb = tracker.generate_feedback(75, ExerciseState.DOWN)
        assert any("Good depth" in f for f in fb)

        # Too shallow
        fb = tracker.generate_feedback(96, ExerciseState.DOWN)
        assert any("deeper" in f for f in fb)

    def test_direction_change_resets(self):
        """If user changes direction before reaching bottom, state resets."""
        tracker = SquatTracker()
        tracker.update(170)
        tracker.update(165)  # GOING_DOWN
        assert tracker.state == ExerciseState.GOING_DOWN
        # Change direction (go back up by > 5°)
        tracker.update(172)
        assert tracker.state == ExerciseState.IDLE


class TestBicepCurlTracker:
    def test_initial_state(self):
        tracker = BicepCurlTracker()
        assert tracker.state == ExerciseState.IDLE
        assert tracker.exercise_name == "bicep_curl"

    def test_full_rep_cycle(self):
        """Bicep curl: extended → curl up → extend down → complete."""
        tracker = BicepCurlTracker()

        # Start extended, begin curling (angle decreasing)
        tracker.update(165)
        tracker.update(160)
        assert tracker.state == ExerciseState.GOING_DOWN  # curling up

        # Curl to top
        tracker.update(120)
        tracker.update(80)
        tracker.update(35)  # below down_threshold (40)
        assert tracker.state == ExerciseState.DOWN  # fully curled

        # Extend back
        tracker.update(40)  # +5, triggers GOING_UP
        assert tracker.state == ExerciseState.GOING_UP

        tracker.update(80)
        tracker.update(120)
        tracker.update(162)  # above up_threshold (160)
        assert tracker.state == ExerciseState.UP

        # Complete rep on next update
        result = tracker.update(165)
        assert result["completed_rep"] is True
        assert result["rep_count"] == 1

    def test_score_full_rom(self):
        tracker = BicepCurlTracker()
        angles = [165, 140, 100, 60, 35, 60, 100, 140, 165]
        score = tracker.score_rep(angles)
        assert score >= 85

    def test_score_incomplete_rom(self):
        tracker = BicepCurlTracker()
        # Short range of motion
        angles = [140, 120, 100, 80, 100, 120, 140]
        score = tracker.score_rep(angles)
        assert score < 90

    def test_feedback_curl_higher(self):
        tracker = BicepCurlTracker()
        fb = tracker.generate_feedback(55, ExerciseState.DOWN)
        assert any("Curl higher" in f for f in fb)


class TestShoulderPressTracker:
    def test_initial_state(self):
        tracker = ShoulderPressTracker()
        assert tracker.exercise_name == "shoulder_press"

    def test_full_rep_cycle(self):
        tracker = ShoulderPressTracker()

        # Start at shoulder level
        tracker.update(100)
        tracker.update(95)
        assert tracker.state == ExerciseState.GOING_DOWN

        tracker.update(85)  # below down_threshold (90)
        assert tracker.state == ExerciseState.DOWN

        # Press up
        tracker.update(90)  # +5, triggers GOING_UP
        assert tracker.state == ExerciseState.GOING_UP

        tracker.update(120)
        tracker.update(150)
        tracker.update(165)  # above up_threshold (160)
        assert tracker.state == ExerciseState.UP

        # Complete rep
        result = tracker.update(170)
        assert result["completed_rep"] is True
        assert result["rep_count"] == 1

    def test_score_rep_full_lockout(self):
        tracker = ShoulderPressTracker()
        angles = [85, 100, 130, 160, 170, 165]
        score = tracker.score_rep(angles)
        assert score >= 90

    def test_feedback_lockout(self):
        tracker = ShoulderPressTracker()
        fb = tracker.generate_feedback(165, ExerciseState.UP)
        assert any("lockout" in f.lower() for f in fb)


class TestTrackerFactory:
    def test_create_squat(self):
        tracker = create_tracker("squat")
        assert isinstance(tracker, SquatTracker)

    def test_create_bicep_curl(self):
        tracker = create_tracker("bicep_curl")
        assert isinstance(tracker, BicepCurlTracker)

    def test_create_shoulder_press(self):
        tracker = create_tracker("shoulder_press")
        assert isinstance(tracker, ShoulderPressTracker)

    def test_create_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown exercise"):
            create_tracker("jumping_jacks")


class TestBuildResult:
    def test_result_structure(self):
        tracker = SquatTracker()
        result = tracker.update(170)
        assert "state" in result
        assert "rep_count" in result
        assert "completed_rep" in result
        assert "feedback" in result
        assert isinstance(result["feedback"], list)

    def test_avg_form_score_calculated(self):
        tracker = SquatTracker()
        tracker.form_scores = [80.0, 90.0, 85.0]
        result = tracker._build_result()
        assert result["avg_form_score"] == 85.0

    def test_avg_form_score_none_when_empty(self):
        tracker = SquatTracker()
        result = tracker._build_result()
        assert result["avg_form_score"] is None
