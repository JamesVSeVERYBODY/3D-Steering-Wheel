import pyvjoy

class VJoyController:
    def __init__(self, vjoy_device, sensitivity=2.0, deadzone=5, max_rotation=450, steering_steps=31):
        self.vjoy_device = vjoy_device
        self.STEERING_SENSITIVITY = sensitivity
        self.STEERING_DEADZONE = deadzone
        self.MAX_WHEEL_ROTATION = max_rotation
        self.STEERING_SMOOTHING = 0.0 ## awwalnya 0,1 , sens = 1, sm 21
        self.previous_steering_value = 16384
        self.STEERING_STEPS = steering_steps
        
        self.THROTTLE_AXIS = pyvjoy.HID_USAGE_Y
        self.BRAKE_AXIS = pyvjoy.HID_USAGE_Z
        self.STEERING_AXIS = pyvjoy.HID_USAGE_X

    def map_yaw_to_steering(self, yaw):
        yaw = round(yaw)

        # Terapkan deadzone
        if abs(yaw) < self.STEERING_DEADZONE:
            yaw = 0.0

        # Clamp yaw
        yaw = max(-180, min(180, yaw))

        # (Optional) boost yaw biar makin tajam respons
        yaw *= self.STEERING_SENSITIVITY

        # Konversi yaw ke bucket
        half_steps = self.STEERING_STEPS // 2
        step_size = 180 / half_steps

        bucket = int(round(yaw / step_size))
        bucket = max(-half_steps, min(half_steps, bucket))

        # Target steering value
        center_value = 16384
        max_range = 16384
        target_value = center_value + int(bucket / half_steps * max_range)

        if self.STEERING_SMOOTHING == 0.0:
            smoothed = target_value
        else: # SMOOTH TRANSITION
            smoothed = int(self.previous_steering_value * (1 - self.STEERING_SMOOTHING) +
                        target_value * self.STEERING_SMOOTHING)
            
        self.previous_steering_value = smoothed
        return smoothed

    def set_controls(self, yaw, throttle, brake, shift_up, shift_down):
        if yaw is not None:
            steering_value = self.map_yaw_to_steering(yaw)
            self.vjoy_device.set_axis(self.STEERING_AXIS, steering_value)

        self.vjoy_device.set_axis(self.THROTTLE_AXIS, throttle)
        self.vjoy_device.set_axis(self.BRAKE_AXIS, brake)

        self.vjoy_device.set_button(1, 1 if shift_up else 0)
        self.vjoy_device.set_button(2, 1 if shift_down else 0)
