import cv2
import time
import numpy as np
import pyvjoy
from hand_detector import HandDetector
from aruco_detector import ArucoDetector
from vjoy_controller import VJoyController
from multi_threading import start_threads
from config import load_config

# Inisialisasi Video Capture dari kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  

# Inisialisasi vJoy
vjoy_device = pyvjoy.VJoyDevice(1)

# Inisialisasi detector dan controller
hand_detector = HandDetector()
aruco_detector = ArucoDetector()
vjoy_controller = VJoyController(vjoy_device)

# Inisialisasi shift counter dan state tangan
shift_counter = 0  # Mulai dari 1
right_hand_shift_detected = False
left_hand_shift_detected = False
last_shift_time = 0  # Waktu terakhir shifting buat delay
shift_cooldown = 0.3  # Delay shifting biar nggak bentrok sama throttle/rem

# Variabel untuk tampilan shifting
SHIFT_DISPLAY_TIME = 0.5  # Waktu tampilan shift di layar (dalam detik)
shift_display_time = 0  # Buat nyimpen waktu terakhir shift
current_shift_text = "Shift: R"  # Default tampilan shift

# Default nilai throttle & brake
throttle_value = 0
brake_value = 0

#multithreading
start_threads()

# Load config
config = load_config()

# Pakai nilai dari config
STEERING_SENSITIVITY = config["steering_sensitivity"]
STEERING_DEADZONE = config["steering_deadzone"]
MAX_WHEEL_ROTATION = config["max_wheel_rotation"]
GAS_MIN = config["gas_min"]
GAS_MAX = config["gas_max"]
BRAKE_MIN = config["brake_min"]
BRAKE_MAX = config["brake_max"]

def display_shift_counter(counter):
    return "R" if counter == 0 else str(counter)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Gagal menangkap gambar")
        break
    
    shift_up = False   # Default off tiap frame
    shift_down = False  # Default off tiap frame

    gesture_frame = frame.copy() # Frame khusus gesture
    aruco_frame = frame.copy()   # Frame khusus untuk deteksi ArUco
    output_frame = frame.copy()  # Frame akhir untuk tampilan

    current_time = time.time()  # Ambil waktu sekarang

    # Reset state throttle & brake setiap frame
    is_throttle = False
    is_braking = False
    right_hand_detected = False
    left_hand_detected = False

    # ===== BAGIAN DETEKSI TANGAN =====
    hand_results = hand_detector.process_frame(gesture_frame)
    
    if hand_results.multi_hand_landmarks:
        for hand_landmarks, hand_type in zip(hand_results.multi_hand_landmarks, hand_results.multi_handedness):
            # Tampilkan jenis tangan (kiri atau kanan)
            hand_label = hand_type.classification[0].label  # 'Left' atau 'Right'
            hand_label = "Right" if hand_label == "Left" else "Left"  # Tukar label

            # Menghitung bounding box untuk setiap tangan
            h, w, _ = frame.shape
            x_min, y_min = w, h
            x_max, y_max = 0, 0
            
            for lm in hand_landmarks.landmark:
                cx, cy = int(lm.x * w), int(lm.y * h)
                x_min, y_min = min(x_min, cx), min(y_min, cy)
                x_max, y_max = max(x_max, cx), max(y_max, cy)
            
            # Gambar kotak merah di sekitar tangan
            cv2.rectangle(frame, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20), (0, 0, 255), 2)
            
            # Tampilkan label Left/Right di atas kotak
            cv2.putText(frame, hand_label, (x_min, y_min - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # Hitung jumlah jari yang lurus
            finger_count = hand_detector.count_extended_fingers(hand_landmarks)

            if hand_label == "Right":
                right_hand_detected = True
                if hand_detector.is_index_finger_vertical(hand_landmarks) and not right_hand_shift_detected:
                    if shift_counter < 6 and (current_time - last_shift_time > shift_cooldown):
                        shift_counter += 1
                        right_hand_shift_detected = True
                        last_shift_time = current_time
                        shift_up = True
                elif not hand_detector.is_index_finger_vertical(hand_landmarks):
                    right_hand_shift_detected = False
                    shift_up = False

            if hand_label == "Left":
                left_hand_detected = True
                if hand_detector.is_index_finger_vertical(hand_landmarks) and not left_hand_shift_detected:
                    if shift_counter > 0 and (current_time - last_shift_time > shift_cooldown):
                        shift_counter -= 1
                        left_hand_shift_detected = True
                        last_shift_time = current_time
                        shift_down = True
                elif not hand_detector.is_index_finger_vertical(hand_landmarks):
                    left_hand_shift_detected = False
                    shift_down = False

            # Throttle & brake
            if hand_label == "Right":
                throttle_value, _ = hand_detector.get_throttle_brake_value(hand_landmarks, hand_label)
                is_throttle = True
            elif hand_label == "Left":
                _, brake_value = hand_detector.get_throttle_brake_value(hand_landmarks, hand_label)
                is_braking = True
            
            # Tampilkan nilai throttle & brake di frame
            cv2.putText(frame, f"Throttle: {throttle_value}", (10, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Brake: {brake_value}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Gambar landmark pada tangan
            hand_detector.draw_landmarks(output_frame, hand_landmarks)

    # ===== BAGIAN DETEKSI ARUCO =====
    aruco_result = aruco_detector.detect_markers(aruco_frame)
    yaw_value = None
    aruco_crop = None

    if aruco_result['detected']:
        # Gambar marker di frame utama
        aruco_detector.draw_markers(frame, aruco_result['corners'], aruco_result['ids'])

        # Crop ArUco marker
        x_min, y_min = np.min(aruco_result['corners'][0][0], axis=0).astype(int)
        x_max, y_max = np.max(aruco_result['corners'][0][0], axis=0).astype(int)

        # Hindari error cropping di luar batas gambar
        x_min, x_max = max(x_min, 0), min(x_max, aruco_frame.shape[1])
        y_min, y_max = max(y_min, 0), min(y_max, aruco_frame.shape[0])

        # Crop dan resize gambar ArUco
        aruco_crop = aruco_frame[y_min:y_max, x_min:x_max]
        if aruco_crop.size > 0:
            aruco_crop = cv2.resize(aruco_crop, (120, 120))

        # Dapatkan sudut dari marker
        aruco_detector.estimate_pose(aruco_result['corners'])
        yaw, pitch, roll = aruco_detector.get_angles()
        temp_yaw = aruco_detector.normalize_yaw(yaw)

        if not aruco_detector.is_calibrated():
            # Kalibrasi jika pitch dan roll mendekati nol
            if abs(pitch) < 5 and abs(roll) < 5:
                aruco_detector.set_neutral_y(pitch)
                if abs(temp_yaw) > 3:
                    cv2.putText(frame, "Recalibrating, Keep on steering", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    aruco_detector.set_neutral_yaw(round(aruco_detector.normalize_yaw(yaw), 1))
                    aruco_detector.set_neutral_roll(roll)
                    aruco_detector.set_calibrated(True)
                    cv2.putText(frame, "Calibrated! Keep Steering!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Align Marker Horizontally (Pitch & Roll)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            # Hitung rotasi relatif berdasarkan yaw referensi
            relative_yaw = round(aruco_detector.normalize_yaw(yaw - aruco_detector.get_neutral_yaw()))

            if abs(relative_yaw) < 0.5:
                relative_yaw = 0.0
            
            # Gunakan relative_yaw untuk steering
            yaw_value = aruco_detector.normalize_yaw(relative_yaw)
            
            # Kirim data ke vJoy
            vjoy_controller.set_controls(yaw_value, throttle_value, brake_value, shift_up, shift_down)
            
            # Tampilkan informasi steering
            center_x = frame.shape[1] // 2
            center_y = frame.shape[0] - 50

            # Mapping yaw ke bar panjang
            bar_length = int(abs(relative_yaw) * 5)  # Skala yaw ke panjang bar
            bar_x_start = center_x - bar_length if relative_yaw < 0 else center_x
            bar_x_end = center_x + bar_length if relative_yaw > 0 else center_x

            # Warna indikator (hijau kalau netral, merah kalau miring)
            color = (0, 255, 0) if -2 <= relative_yaw <= 2 else (0, 0, 255)

            # Gambar garis tengah (crosshair)
            cv2.line(frame, (center_x - 50, center_y), (center_x + 50, center_y), (255, 255, 255), 2)
            cv2.rectangle(frame, (bar_x_start, center_y - 5), (bar_x_end, center_y + 5), color, -1)
            
            # Tampilkan informasi sudut
            neutral_yaw = aruco_detector.get_neutral_yaw()
            neutral_roll = aruco_detector.get_neutral_roll()
            
            cv2.putText(frame, f"Yaw (ref): {neutral_yaw:.2f} deg", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Roll (ref): {neutral_roll:.2f} deg", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Real Yaw: {yaw:.2f} deg", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Real Roll: {roll:.2f} deg", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Real Pitch: {pitch:.2f} deg", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Relative Yaw: {relative_yaw:.2f} deg", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Steering: {relative_yaw:.2f} deg", (center_x - 80, center_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Steering Value: {vjoy_controller.previous_steering_value}", 
                (10, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    else:
        cv2.putText(frame, "Marker Not Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # **Tempelkan hasil crop di bagian kanan atas frame**
    if aruco_crop is not None:
        h, w, _ = aruco_crop.shape
        frame[10:10+h, frame.shape[1]-w-10:frame.shape[1]-10] = aruco_crop  # Tempel di pojok kanan atas

    # ===== TAMPILKAN SEMUA INFO =====
    # Info shifting dari kode pertama
    # Cek apakah baru saja shift up/down
    if shift_up:
        current_shift_text = "Shift Up!"
        shift_display_time = time.time()

    elif shift_down:
        current_shift_text = "Shift Down!"
        shift_display_time = time.time()

    # Kalau sudah lewat SHIFT_DISPLAY_TIME detik, balikin teks ke normal
    if time.time() - shift_display_time > SHIFT_DISPLAY_TIME:
        current_shift_text = f"Shift: {display_shift_counter(shift_counter)}"

    # Warna teks shifting
    shift_color = (0, 255, 0)  # Hijau normal
    if "Up" in current_shift_text:
        shift_color = (0, 255, 255)  # Kuning kalau shift up
    elif "Down" in current_shift_text:
        shift_color = (255, 0, 0)  # Merah kalau shift down

    # Tampilkan di layar
    cv2.putText(frame, current_shift_text, (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, shift_color, 2)

    # Info throttle & brake dari kode pertama
    cv2.putText(frame, f"Throttle: {'ON' if is_throttle else 'OFF'}", (10, 290), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    cv2.putText(frame, f"Brake: {'ON' if is_braking else 'OFF'}", (10, 330), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Tampilkan hasil
    cv2.imshow("Racing Control System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()