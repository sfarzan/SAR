import time
from pymavlink import mavutil

# Set up connection to Pixhawk
master = mavutil.mavlink_connection('udpout:0.0.0.0:14550')  # Replace with your Pixhawk's IP address and port

# Main loop
while True:
    try:
        msg = master.recv_match()
        if not msg:
            continue
        # Print received messages
        print(msg)
    except KeyboardInterrupt:
        break

# Close connection
master.close()
