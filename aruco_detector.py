import cv2
import numpy as np
import cv2.aruco as aruco

class ArucoDetector:
    def __init__(self):
        # ArUco dictionary dan parameter deteksi
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.parameters = aruco.DetectorParameters()
        self.parameters.adaptiveThreshWinSizeMin = 3
        self.parameters.adaptiveThreshWinSizeMax = 23
        self.parameters.adaptiveThreshWinSizeStep = 10
        self.parameters.adaptiveThreshConstant = 7
        
        # Variabel untuk kalibrasi
        self.neutral_y = None  # Sudut netral pada sumbu Y (pitch = 0)
        self.neutral_yaw = None  # Yaw saat pitch = 0
        self.neutral_roll = None  # Roll saat pitch = 0
        self.calibrated = False  # Status kalibrasi
        
        # Kamera matrix dan distorsi
        self.camera_matrix = np.array([[800, 0, 320], [0, 800, 240], [0, 0, 1]], dtype=np.float32)  # Contoh
        self.dist_coeffs = np.zeros((4, 1), dtype=np.float32)  # Asumsi tanpa distorsi
        
        # Panjang marker (dalam meter atau unit relatif)
        self.marker_length = 0.05  # 5 cm
        
        # Variabel untuk menyimpan poses dan rotasi
        self.rotation_matrix = None
        self.yaw = None
        self.pitch = None
        self.roll = None

    def detect_markers(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        
        result = {
            'detected': ids is not None and len(corners) > 0,
            'corners': corners if ids is not None and len(corners) > 0 else None,
            'ids': ids
        }
        
        return result

    def draw_markers(self, frame, corners, ids):
        aruco.drawDetectedMarkers(frame, corners, ids)

    def estimate_pose(self, corners):
        rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners, self.marker_length, self.camera_matrix, self.dist_coeffs)
        self.rotation_matrix, _ = cv2.Rodrigues(rvec[0])
        self.yaw, self.pitch, self.roll = self.rotation_matrix_to_euler_angles(self.rotation_matrix)

    def get_angles(self):
        return self.yaw, self.pitch, self.roll

    def rotation_matrix_to_euler_angles(self, R):
        """Konversi matriks rotasi ke sudut Euler (yaw, pitch, roll)."""
        sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
        singular = sy < 1e-6

        if not singular:
            yaw = np.arctan2(R[1, 0], R[0, 0])
            pitch = np.arctan2(-R[2, 0], sy)
            roll = np.arctan2(R[1, 0], R[0, 0])
        else:
            yaw = np.arctan2(-R[1, 2], R[1, 1])
            pitch = np.arctan2(-R[2, 0], sy)
            roll = 0

        return np.degrees(yaw), np.degrees(pitch), np.degrees(roll)

    def normalize_yaw(self, yaw):
        """Gunakan atan2 untuk memastikan yaw tetap dalam rentang -180° sampai 180°"""
        return (yaw + 180) % 360 - 180

    def is_calibrated(self):
        return self.calibrated

    def set_calibrated(self, value):
        self.calibrated = value

    def get_neutral_yaw(self):
        return self.neutral_yaw

    def get_neutral_roll(self):
        return self.neutral_roll

    def set_neutral_y(self, value):
        self.neutral_y = value

    def set_neutral_yaw(self, value):
        if abs(value) < 1:
            self.neutral_yaw = 0.0
        else:
            self.neutral_yaw = value

    def set_neutral_roll(self, value):
        self.neutral_roll = value
        