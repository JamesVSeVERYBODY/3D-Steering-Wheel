import matplotlib.pyplot as plt
import csv

# --- Steering Plot ---
times, yaws, vjoys = [], [], []
with open('steering_log.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        times.append(float(row['timestamp']))
        yaws.append(float(row['yaw']))
        vjoys.append(float(row['vjoy_value']))

t0 = times[0]
times = [t - t0 for t in times]

plt.figure()
plt.plot(times, yaws, label='Yaw (deg)')
plt.plot(times, vjoys, label='vJoy Steering Output')
plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.title('Steering Mapping')
plt.legend()
plt.grid()

# --- Throttle & Brake Plot ---
t_times, throttles = [], []
b_times, brakes = [], []

with open('throttle_log.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        t_times.append(float(row['timestamp']))
        throttles.append(float(row['throttle_value']))

with open('brake_log.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        b_times.append(float(row['timestamp']))
        brakes.append(float(row['brake_value']))

t0 = min(t_times[0], b_times[0])
t_times = [t - t0 for t in t_times]
b_times = [t - t0 for t in b_times]

plt.figure()
plt.plot(t_times, throttles, label='Throttle', color='blue')
plt.plot(b_times, brakes, label='Brake', color='red')
plt.xlabel('Time (s)')
plt.ylabel('vJoy Axis Value')
plt.title('Throttle & Brake Response')
plt.legend()
plt.grid()

plt.show()
