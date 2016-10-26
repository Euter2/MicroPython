"""Micropython module for HC-SR04 ultrasonic ranging module."""
from machine import Pin, time_pulse_us
from time import sleep_us


class Ultrasonic:
    """HC-SR04 ultrasonic ranging module class."""

    def __init__(self, trig_Pin, echo_Pin):
        """Initialize Input(echo) and Output(trig) Pins."""
        self._trig = trig_Pin
        self._echo = echo_Pin
        self._trig.init(Pin.OUT)
        self._echo.init(Pin.IN)
        self._sound_speed = 340  # m/s

    def _pulse(self):
        """Trigger ultrasonic module with 10us pulse."""
        self._trig.high()
        sleep_us(10)
        self._trig.low()

    def distance(self):
        """Measure pulse length and return calculated distance [m]."""
        self._pulse()
        pulse_width_s = time_pulse_us(self._echo, Pin.high) / 1000000
        dist_m = (pulse_width_s / 2) * self._sound_speed
        return dist_m

    def calibration(self, known_dist_m):
        """Calibrate speed of sound."""
        self._sound_speed = known_dist_m / self.distance() * self._sound_speed
        print("Speed of sound was successfully calibrated! \n" +
              "Current value: " + str(self._sound_speed) + " m/s")
