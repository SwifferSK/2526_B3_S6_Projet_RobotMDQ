"""MCP3208 ADC (SPI) helper.

Channels: 0..7 (CH0..CH7)
"""

from __future__ import annotations

try:
    import spidev  # type: ignore
except ImportError:  # pragma: no cover
    spidev = None

BIT_START = 4
BIT_CONV_SINGLE = 2


class MCP3208:
    def __init__(self, spi_bus: int = 0, spi_device: int = 0, clock_speed: int = 1_000_000, vref: float = 3.3):
        if spidev is None:  # pragma: no cover
            raise ImportError("spidev is required on Raspberry Pi. Install it or run on a Pi with SPI enabled.")

        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = clock_speed
        self.vref = float(vref)

    def read_channel(self, channel: int) -> int:
        """Read raw 12-bit value from one channel (0..7)."""
        if not 0 <= channel <= 7:
            raise ValueError("Invalid channel (must be between 0 and 7).")

        command = [BIT_START | BIT_CONV_SINGLE | (channel >> 2), (channel & 3) << 6, 0]
        result = self.spi.xfer2(command)
        value = ((result[1] & 15) << 8) | result[2]
        return int(value)

    def read_voltage(self, channel: int) -> float:
        value = self.read_channel(channel)
        return (value / 4095.0) * self.vref

    def read_all_channels(self) -> list[float]:
        return [self.read_voltage(ch) for ch in range(8)]

    def close(self) -> None:
        self.spi.close()
