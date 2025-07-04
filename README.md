# 🏎️ 3D Steering Wheel — Gesture & ArUco Powered Virtual Racing Controller

Welcome to the future of sim racing! This project transforms your webcam, your hands, and a simple ArUco marker into a fully interactive, virtual steering wheel system. No expensive hardware needed — just pure computer vision magic, hand gestures, and vJoy integration. 

---

## 🚀 What Makes This Project Awesome?
- **Next-Gen Virtual Steering**: Control your racing games with real hand gestures and marker tracking — feel like a pro, no wheel required!
- **Gesture-Based Throttle & Brake**: Accelerate and brake with intuitive hand movements. No pedals? No problem!
- **Gesture Shifting**: Shift up/down with a flick of your finger. Lightning fast, super cool.
- **Seamless vJoy Output**: Instantly compatible with most racing games and simulators.
- **Live Data Plotting**: Visualize your steering, throttle, brake, and latency in real time with built-in plotting tools.
- **Easy Customization**: Tweak sensitivity, deadzone, and more via a simple config file.

---

## 🗂️ Project Structure
- `main.py` — The heart of the system. Runs everything.
- `hand_detector.py` — Hand gesture recognition (powered by MediaPipe).
- `aruco_detector.py` — ArUco marker tracking for steering.
- `vjoy_controller.py` — Sends your moves to vJoy.
- `multi_threading.py` — Keeps everything smooth and responsive.
- `config.py` — Loads and saves your custom settings.
- `plotting.py` — Visualizes your driving data.
- `plotting_latency.py` — See your system's real-time latency.
- `Loadout/config.json` — Your personal config (auto-generated, not for sharing).

---

## ⚡ Quickstart
1. **Install Python 3.10+**
2. **Install vJoy** ([Download here](https://github.com/njz3/vJoy))
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Plug in your webcam and run:**
   ```bash
   python main.py
   ```

---

## 🛠️ Requirements
- `opencv-python`
- `mediapipe`
- `numpy`
- `pyvjoy`
- `matplotlib`

---

## ⚠️ Notes & Tips
- Ignore files in `Loadout/` and `__pycache__/` — they're local and auto-generated.
- Make sure vJoy is installed and the device ID matches your setup.
- A webcam is required for all the magic to happen!

---

## 🤝 Contributing & License
Open to all contributors — fork, star, and PR away! Licensed under the MIT License.

---

> Made with ❤️ and a need for speed by James Philip
