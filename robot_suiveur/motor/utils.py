from __future__ import annotations


def angle_to_steps(angle: float, steps_per_rev: int, microstep: int) -> int:
    """Convert an angle (degrees) to step count (microsteps included)."""
    return int((angle / 360.0) * (steps_per_rev * microstep))
