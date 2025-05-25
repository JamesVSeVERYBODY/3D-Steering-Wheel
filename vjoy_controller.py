import pyvjoy
import numpy as np

class VJoyController:
    def __init__(self, vjoy_device, sensitivity=2.0, deadzone=2, max_rotation=240):
        self.vjoy_device = vjoy_device
        self.STEERING_SENSITIVITY = sensitivity
        self.STEERING_DEADZONE = deadzone
        self.MAX_WHEEL_ROTATION = max_rotation
        self.STEERING_SMOOTHING = 0.0 ## awwalnya 0,1 , sens = 1, sm 21
        self.previous_steering_value = 16384

        self.THROTTLE_AXIS = pyvjoy.HID_USAGE_Y
        self.BRAKE_AXIS = pyvjoy.HID_USAGE_Z
        self.STEERING_AXIS = pyvjoy.HID_USAGE_X

    def map_yaw_to_steering(self, yaw):
        yaw = round(yaw)

        # Deadzone (kecilkan kalau perlu)
        if abs(yaw) < self.STEERING_DEADZONE:
            yaw = 0.0

        # Clamp yaw ke limit stir fisik
        max_yaw = self.MAX_WHEEL_ROTATION / 2  # Misal 240° → max_yaw = 120°
        yaw = max(-max_yaw, min(max_yaw, yaw))

        # Sensitivity boost
        yaw *= self.STEERING_SENSITIVITY

        # Clamp lagi biar ga lewat
        yaw = max(-max_yaw, min(max_yaw, yaw))

        # Non-linear scaling biar yaw kecil lebih terasa
        yaw_sign = np.sign(yaw)
        yaw_abs = abs(yaw) / max_yaw  # Normalisasi ke 0-1
        yaw_scaled = yaw_abs ** 0.7   # Exponent < 1 → yaw kecil lebih agresif
        yaw = yaw_sign * yaw_scaled * max_yaw  # Kembalikan ke derajat aslinya

        # Mapping yaw ke vJoy axis (0 - 32767)
        center_value = 16384
        max_range = 16384
        target_value = center_value + int((yaw / max_yaw) * max_range)

        # Smoothing kalau diaktifkan
        if self.STEERING_SMOOTHING == 0.0:
            return target_value
        else:
            smoothed = int(self.previous_steering_value * (1 - self.STEERING_SMOOTHING) +
                        target_value * self.STEERING_SMOOTHING)
            self.previous_steering_value = smoothed
            return smoothed

    def set_controls(self, yaw, throttle, brake, shift_up, shift_down):
        if yaw is not None:
            steering_value = self.map_yaw_to_steering(yaw)
            self.vjoy_device.set_axis(self.STEERING_AXIS, steering_value)
            self.previous_steering_value = steering_value

        self.vjoy_device.set_axis(self.THROTTLE_AXIS, throttle)
        self.vjoy_device.set_axis(self.BRAKE_AXIS, brake)

        self.vjoy_device.set_button(1, 1 if shift_up else 0)
        self.vjoy_device.set_button(2, 1 if shift_down else 0)
