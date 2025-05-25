import matplotlib.pyplot as plt
import csv

def load_latency(file_path):
    times, latencies = [], []
    with open(file_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(float(row['timestamp']))
            latencies.append(float(row['latency_ms']))
    t0 = times[0]
    times = [t - t0 for t in times]
    return times, latencies

# Load data
steer_times, steer_latencies = load_latency('latency_steer_log.csv')
throttle_times, throttle_latencies = load_latency('latency_throttle_log.csv')
brake_times, brake_latencies = load_latency('latency_brake_log.csv')

# Plot Steering Latency
plt.figure(figsize=(10,5))
plt.plot(steer_times, steer_latencies, color='green')
plt.xlabel('Time (s)')
plt.ylabel('Latency (ms)')
plt.title('Steering Latency (Yaw → vJoy Output)')
plt.grid()

# Plot Throttle Latency
plt.figure(figsize=(10,5))
plt.plot(throttle_times, throttle_latencies, color='blue')
plt.xlabel('Time (s)')
plt.ylabel('Latency (ms)')
plt.title('Throttle Gesture Latency')
plt.grid()

# Plot Brake Latency
plt.figure(figsize=(10,5))
plt.plot(brake_times, brake_latencies, color='red')
plt.xlabel('Time (s)')
plt.ylabel('Latency (ms)')
plt.title('Brake Gesture Latency')
plt.grid()

plt.show()
