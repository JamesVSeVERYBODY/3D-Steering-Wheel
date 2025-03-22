import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self):
        # Inisialisasi MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        # Konversi ke RGB untuk MediaPipe Hands
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Proses deteksi tangan
        results = self.hands.process(img_rgb)
        return results

    def draw_landmarks(self, frame, hand_landmarks):
        # Gambar landmark pada tangan
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def count_extended_fingers(self, hand_landmarks):
        """Hitung jumlah jari yang lurus."""
        extended_fingers = 0
        for i in [8, 12, 16, 20]:  # Landmark ujung jari (telunjuk, tengah, manis, kelingking)
            if hand_landmarks.landmark[i].y < hand_landmarks.landmark[i - 2].y:
                extended_fingers += 1
        return extended_fingers

    def check_index_pinky_fingers(self, hand_landmarks):
        """
        Cek apakah hanya telunjuk (8) dan kelingking (20) yang lurus.
        """
        index_extended = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
        pinky_extended = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

        # Pastikan jari tengah (12) dan manis (16) tidak lurus
        middle_folded = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y
        ring_folded = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y

        return index_extended and pinky_extended and middle_folded and ring_folded

    def is_index_finger_vertical(self, hand_landmarks):
        """
        Cek apakah telunjuk benar-benar lurus ke atas sementara jari lainnya menggenggam.
        """
        index_tip = hand_landmarks.landmark[8]  # Ujung telunjuk
        index_base = hand_landmarks.landmark[5]  # Sendi bawah telunjuk

        # Cek apakah telunjuk benar-benar lurus ke atas (vertikal)
        vertical_threshold = 0.1  # Threshold minimum supaya dianggap vertikal
        is_vertical = index_tip.y < index_base.y - vertical_threshold  # Telunjuk harus lebih tinggi dari sendinya

        # Pastikan jari lainnya (tengah, manis, kelingking) benar-benar terlipat
        def is_finger_folded(base, mid, tip):
            return hand_landmarks.landmark[tip].y > hand_landmarks.landmark[base].y

        middle_folded = is_finger_folded(9, 10, 12)  # Jari tengah
        ring_folded = is_finger_folded(13, 14, 16)  # Jari manis
        pinky_folded = is_finger_folded(17, 18, 20)  # Kelingking

        return is_vertical and middle_folded and ring_folded and pinky_folded

    def get_throttle_brake_value(self, hand_landmarks, hand_label):
        """Menghitung throttle & brake dari posisi tangan berdasarkan ketinggian jari"""
        # Gunakan sendi tengah ke ujung, lebih responsif terhadap perubahan kecil
        gas_distance = max(0, hand_landmarks.landmark[6].y - hand_landmarks.landmark[8].y)
        brake_distance = max(0, hand_landmarks.landmark[18].y - hand_landmarks.landmark[20].y)

        # Normalisasi ke rentang 0 - 1
        gas_distance = min(1, gas_distance * 5)
        brake_distance = min(1, brake_distance * 5)

        # Konversi ke vJoy (20000-32767 untuk gas, 9000-29000 untuk rem)
        max_throttle = 32767  
        max_brake = 29000  
        min_throttle = 20000  
        min_brake = 9000  

        throttle_value = int(min_throttle + (gas_distance * (max_throttle - min_throttle))) if hand_label == "Right" else 0
        brake_value = int(min_brake + (brake_distance * (max_brake - min_brake))) if hand_label == "Left" else 0
        
        return throttle_value, brake_value
    