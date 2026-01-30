from __future__ import annotations

import time

from .MCP3208 import MCP3208


THRESHOLD = 1.5


def detect_line(adc: MCP3208, threshold: float = THRESHOLD, *, verbose: bool = True) -> str:
    """Read the 8 sensors (CH0..CH7) and classify the line position.

    Returns one of: 'left', 'center', 'right', 'none'.

    Notes:
    - Many IR line sensors output *lower* voltage on black line (depends on your module).
      This code assumes: line detected when voltage < threshold.
    """

    # Sensor readings
    left0 = adc.read_voltage(0)
    left1 = adc.read_voltage(1)
    left2 = adc.read_voltage(2)
    center1 = adc.read_voltage(3)
    center0 = adc.read_voltage(4)
    right0 = adc.read_voltage(5)
    right1 = adc.read_voltage(6)
    right2 = adc.read_voltage(7)

    if verbose:
        print(
            f"L:{left0:.2f}V | L1:{left1:.2f}V | L2:{left2:.2f}V | "
            f"C:{center0:.2f}V | C1:{center1:.2f}V | "
            f"R:{right0:.2f}V | R1:{right1:.2f}V | R2:{right2:.2f}V",
            end=" -> ",
        )

    # Simple detection
    if left0 < threshold or left1 < threshold or left2 < threshold:
        pos = "left"
    elif center0 < threshold or center1 < threshold:
        pos = "center"
    elif right0 < threshold or right1 < threshold or right2 < threshold:
        pos = "right"
    else:
        pos = "none"

    if verbose:
        print(pos)

    # Small delay to avoid spamming too fast
    time.sleep(0.05)
    return pos
