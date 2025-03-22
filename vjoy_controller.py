import pyvjoy

class VJoyController:
    def __init__(self, vjoy_device):
        self.vjoy_device = vjoy_device
        
        # Batasan steering wheel mobil real (default 900° total → ±450°)
        self.MAX_WHEEL_ROTATION = 450  # Bisa ubah ke 540, 720, atau 900 kalau mau
        self.STEERING_SENSITIVITY = 1.0  # Bisa dikurangi kalau masih terlalu responsif
        self.STEERING_DEADZONE = 5  # Biar yaw kecil gak bikin steering gerak (default 2°)
        
        # Variabel smoothing steering
        self.previous_steering_value = 16384  # Posisi tengah di vJoy
        self.STEERING_SMOOTHING = 0.4  # Makin tinggi makin smooth (0.1 - 0.5 ideal)

    def map_yaw_to_steering(self, yaw):
        """Konversi sudut yaw ke nilai steering vJoy"""
        yaw = round(yaw)  # Pastikan yaw selalu bulat

        # Balikin arah yaw biar kiri = kiri, kanan = kanan
        yaw = max(-180, min(180, yaw))
        wheel_rotation = (-yaw / 180) * self.MAX_WHEEL_ROTATION  
        wheel_rotation *= self.STEERING_SENSITIVITY  

        # Konversi ke rentang vJoy (0-32767)
        target_steering = int((wheel_rotation + self.MAX_WHEEL_ROTATION) / (2 * self.MAX_WHEEL_ROTATION) * 32767)

        # Stepwise steering biar nggak langsung lompat
        step_size = 800  # Bisa coba naikkan ke 1000 kalau masih terlalu sensitif
        if abs(target_steering - self.previous_steering_value) > step_size:
            if target_steering > self.previous_steering_value:
                target_steering = self.previous_steering_value + step_size
            else:
                target_steering = self.previous_steering_value - step_size

        # Kurangi smoothing biar lebih responsif
        smoothed_steering = int(self.previous_steering_value * (1 - self.STEERING_SMOOTHING) + 
                               target_steering * self.STEERING_SMOOTHING)
        self.previous_steering_value = smoothed_steering  

        return smoothed_steering

    def set_controls(self, yaw, throttle, brake, shift_up, shift_down):
        """Update input vJoy berdasarkan input kontrol"""
        if yaw is not None:
            steering_value = self.map_yaw_to_steering(yaw)
            self.vjoy_device.set_axis(pyvjoy.HID_USAGE_X, steering_value)  # Set Steering ke vJoy

        # Kontrol Throttle & Brake
        self.vjoy_device.set_axis(pyvjoy.HID_USAGE_Y, throttle)  # Gas
        self.vjoy_device.set_axis(pyvjoy.HID_USAGE_Z, brake)  # Rem

        # Kontrol Shifting
        if shift_up:
            self.vjoy_device.set_button(1, 1)  # Tekan tombol 1 (Shift Up)
        else:
            self.vjoy_device.set_button(1, 0)  # Lepas tombol 1

        if shift_down:
            self.vjoy_device.set_button(2, 1)  # Tekan tombol 2 (Shift Down)
        else:
            self.vjoy_device.set_button(2, 0)  # Lepas tombol 2