"""Tests for pose engine angle calculations."""

from app.services.pose_engine import calculate_angle


class TestCalculateAngle:
    def test_right_angle(self):
        """90° angle at vertex B."""
        a = (0, 1)
        b = (0, 0)
        c = (1, 0)
        angle = calculate_angle(a, b, c)
        assert abs(angle - 90.0) < 1.0

    def test_straight_line(self):
        """180° — points are collinear."""
        a = (0, 0)
        b = (1, 0)
        c = (2, 0)
        angle = calculate_angle(a, b, c)
        assert abs(angle - 180.0) < 1.0

    def test_acute_angle(self):
        """~45° angle."""
        a = (0, 1)
        b = (0, 0)
        c = (1, 1)
        angle = calculate_angle(a, b, c)
        assert 40 < angle < 50

    def test_obtuse_angle(self):
        """~135° angle."""
        a = (1, 0)
        b = (0, 0)
        c = (-1, 1)
        angle = calculate_angle(a, b, c)
        assert 130 < angle < 140

    def test_zero_angle(self):
        """0° — same direction vectors."""
        a = (1, 0)
        b = (0, 0)
        c = (2, 0)
        angle = calculate_angle(a, b, c)
        assert angle < 1.0

    def test_symmetry(self):
        """Angle should be the same regardless of A/C swap."""
        a = (0, 2)
        b = (0, 0)
        c = (2, 0)
        angle1 = calculate_angle(a, b, c)
        angle2 = calculate_angle(c, b, a)
        assert abs(angle1 - angle2) < 0.1
