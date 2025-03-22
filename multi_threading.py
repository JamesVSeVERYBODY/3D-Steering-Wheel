import cv2
import threading
import queue
import time
from hand_detector import HandDetector
from aruco_detector import ArucoDetector
from vjoy_controller import VJoyController

# Inisialisasi Video Capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Queue buat share data antar thread
hand_queue = queue.Queue()
aruco_queue = queue.Queue()

# Buat menyimpan status terakhir
latest_hand_data = None
latest_aruco_data = None

def hand_tracking():
    """Thread buat tracking tangan"""
    global latest_hand_data
    while True:
        success, frame = cap.read()
        if not success:
            print("[ERROR] Gagal menangkap gambar")
            break
        
        hand_data = HandDetector(frame)
        hand_queue.put(hand_data)  # Kirim data ke queue
        latest_hand_data = hand_data  # Simpan data terakhir
        time.sleep(0.01)  # Kurangi beban CPU

def aruco_tracking():
    """Thread buat tracking ArUco marker"""
    global latest_aruco_data
    while True:
        success, frame = cap.read()
        if not success:
            print("[ERROR] Gagal menangkap gambar")
            break
        
        aruco_data = ArucoDetector(frame)
        aruco_queue.put(aruco_data)  # Kirim data ke queue
        latest_aruco_data = aruco_data  # Simpan data terakhir
        time.sleep(0.01)

def vjoy_control():
    """Thread buat kirim kontrol ke vJoy"""
    while True:
        if latest_hand_data and latest_aruco_data:
            throttle, brake, shift_up, shift_down = latest_hand_data
            yaw = latest_aruco_data

            VJoyController(yaw, throttle, brake, shift_up, shift_down)  # Kirim ke vJoy
        time.sleep(0.01)  # Biarkan CPU istirahat

def start_threads():
    """Fungsi buat start semua thread"""
    hand_thread = threading.Thread(target=hand_tracking, daemon=True)
    aruco_thread = threading.Thread(target=aruco_tracking, daemon=True)
    vjoy_thread = threading.Thread(target=vjoy_control, daemon=True)

    hand_thread.start()
    aruco_thread.start()
    vjoy_thread.start()
