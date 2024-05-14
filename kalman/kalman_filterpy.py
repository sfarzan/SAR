from filterpy.kalman import KalmanFilter
import numpy as np

# Initialize Kalman filter for predicting RSSI values from drones
kf = KalmanFilter(dim_x=3, dim_z=1)  # State vector dimension: 3 (one for each drone), Measurement vector dimension: 1
                                     # Add another dim_z for GPS information


# Define process noise covariance matrix Q based on system dynamics
Q = np.array([[0.01, 0, 0],
              [0, 0.01, 0],
              [0, 0, 0.01]])  # Adjust values based on system characteristics

# Set process noise covariance matrix Q
kf.Q = Q

# Define initial state estimate x and state covariance matrix P
x = np.array([initial_estimate_drone1, initial_estimate_drone2, initial_estimate_drone3])  # Initial RSSI estimates for each drone
P = np.eye(3)  # Identity matrix as initial state covariance

# Predict next state based on current state estimate and process noise
kf.x = x
kf.P = P
kf.predict()

# Update Kalman filter with RSSI measurements from drones
z = np.array([measurement_drone1, measurement_drone2, measurement_drone3])  # RSSI measurements from each drone, include GPS information

kf.update(z)

# Get the predicted RSSI values for the next time step
predicted_rssi_values = kf.x
