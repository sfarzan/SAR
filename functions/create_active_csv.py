"""
This script generates a CSV file for a selected drone trajectory and creates a 3D plot of the trajectory. The CSV and PNG files of the trajectory are saved in the "shapes" directory.

Example Usage:
--------------
To generate a CSV file for a circular trajectory, use the following code snippet:

create_active_csv(shape_name="circle", diameter=5.0, direction=1, maneuver_time=60.0, start_x=0.0, start_y=0.0, initial_altitude=10.0, climb_rate=2.0, move_speed=2.5, hold_time=2.0)

Available trajectories:
-----------------------
"eight_shape", "circle", "square", "helix", "heart_shape", "infinity_shape", "spiral_square", "star_shape", "zigzag", "sine_wave"

Visualization:
--------------
After generating the CSV file, you can visualize the trajectory using plot functions and save the trajectory plot in the "shapes" folder along with the CSV file.

Note:
-----
Make sure to have the necessary dependencies installed and correctly set up the offboard control system to use the generated CSV file for controlling the drone in an offboard mode.

Usage:
------
The output generated by `csvCreator.py` can be utilized in the `offboard_from_csv.py` file, also available in the same GitHub repository, to control a drone in an offboard mode. The generated CSV file contains the necessary information for each step of the drone's trajectory, including position, velocity, acceleration, yaw angle, and LED colors.

Offboard Control in PX4:
------------------------
The offboard mode in PX4 is a flight mode that allows external systems to control the drone's position and velocity directly. It enables autonomous flight and is commonly used in research, development, and testing scenarios. The offboard control system communicates with the drone's flight controller through a communication protocol like MAVLink.

To use the CSV output generated by `csvCreator.py` for offboard control in PX4, you can follow these steps:
1. Load the generated CSV file, which represents the desired trajectory for the drone.
2. Extract the position and velocity information from the CSV file.
3. Send the position and velocity commands to the drone's flight controller using an offboard control system, such as the `offboard_from_csv.py` script.
4. The flight controller will interpret the commands and execute the desired trajectory, guiding the drone accordingly.

CSV File Structure and Guide:
----------------------------
The CSV file created by `csvCreator.py` follows a specific structure, where each row represents a step of the drone's trajectory. The columns in the CSV file contain the following information:
- `idx`: Index or step number of the trajectory.
- `t`: Time in seconds for the given step.
- `px`: Drone's position in the X-axis.
- `py`: Drone's position in the Y-axis.
- `pz`: Drone's position in the Z-axis (negative value indicates altitude).
- `vx`: Drone's velocity in the X-axis.
- `vy`: Drone's velocity in the Y-axis.
- `vz`: Drone's velocity in the Z-axis.
- `ax`: Drone's acceleration in the X-axis.
- `ay`: Drone's acceleration in the Y-axis.
- `az`: Drone's acceleration in the Z-axis.
- `yaw`: Drone's yaw angle.\
- 'mode' : Flight Phase Mode
- `ledr`: Red component value for the drone's LED color.
- `ledg`: Green component value for the drone's LED color.
- `ledb`: Blue component value for the drone's LED color.

Flight Modes and Codes:
- 0: On the ground
- 10: Initial climbing state
- 20: Initial holding after climb
- 30: Moving to start point
- 40: Holding at start point
- 50: Moving to maneuvering start point
- 60: Holding at maneuver start point
- 70: Maneuvering (trajectory)
- 80: Holding at the end of the trajectory coordinate
- 90: Returning to home coordinate
- 100: Landing

Each flight mode is represented by an integer code. These codes are used to indicate the different phases of the flight in the CSV file.

To create a valid CSV file for offboard control, make sure to adhere to the structure described above. Each row should represent a specific time step with the corresponding position, velocity, acceleration, and LED color values.
"""



import csv
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from functions.trajectories import *





def create_active_csv(shape_name,diameter, direction, maneuver_time, start_x, start_y, initial_altitude, climb_rate,move_speed, hold_time , step_time, output_file="active.csv"):

    map_shape_to_code(shape_name)
    shape_code, shape_fcn, shape_args = map_shape_to_code(shape_name)

    # The function returns the code, function, and arguments associated with the given shape name
    print(f"Shape Code: {shape_code}")
    print(f"Shape Function: {shape_fcn}")
    print(f"Shape Arguments: {shape_args}")
   
   
    header = ["idx", "t", "px", "py", "pz", "vx", "vy", "vz", "ax", "ay", "az", "yaw", "mode", "ledr", "ledg", "ledb"]

    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)



        # Calculate climb time and steps
        climb_time = initial_altitude / climb_rate
        climb_steps = int(climb_time / step_time)
        # Write climb trajectory
        for i in range(climb_steps):
            t = i * step_time
            x = 0
            y = 0
            z = (climb_rate * t) * -1
            vx = 0.0
            vy = 0.0
            vz = -climb_rate
            ax = 0
            ay = 0
            az = 0
            yaw = 0
            mode =10
            row = [i, t, x, y, z, vx, vy, vz, ax, ay, az, yaw,mode, "nan", "nan", "nan"]
            writer.writerow(row)


        # Hold at intial altitude
        hold_steps = int(hold_time / step_time)

        for i in range(hold_steps):
            t = climb_time + i * step_time
            x = 0
            y = 0
            z = -1 * initial_altitude
            vx = 0.0
            vy = 0.0
            vz = 0.0
            ax = 0
            ay = 0
            az = 0
            yaw = 0
            mode = 20
            row = [climb_steps + i, t, x, y, z, vx, vy, vz, 0,0,0, yaw,mode, "nan", "nan", "nan"]
            writer.writerow(row)  

    # Move to start position
        move_start_distance = math.sqrt(start_x**2 + start_y**2)
        move_start_time = move_start_distance / move_speed
        move_start_steps = int(move_start_time / step_time)

        for i in range(move_start_steps):
            t = climb_time + hold_time+ i * step_time
            ratio = i / move_start_steps
            x = start_x * ratio
            y = start_y * ratio
            z = -1 * initial_altitude
            vx = move_speed * (start_x / move_start_distance)
            vy = move_speed * (start_y / move_start_distance)
            vz = 0.0
            ax = 0
            ay = 0
            az = 0
            yaw = 0
            mode = 30
            row = [climb_steps + hold_steps + i, t, x, y, z, vx, vy, vz, 0 , 0 ,0, yaw,mode, "nan", "nan", "nan"]
            writer.writerow(row)

    # Hold start position for n seconds
        hold_steps = int(hold_time / step_time)

        for i in range(hold_steps):
            t = climb_time + hold_time +move_start_time + i * step_time
            x = start_x
            y = start_y
            z = -1 * initial_altitude
            vx = 0.0
            vy = 0.0
            vz = 0.0
            ax = 0
            ay = 0
            az = 0
            yaw = 0
            mode = 40
            row = [climb_steps + hold_steps + move_start_steps + i, t, x, y, z, vx, vy, vz, 0, 0, 0, yaw,mode, "nan", "nan", "nan"]
            writer.writerow(row)    

        # Check if start position is different from first setpoint of maneuver
        if 0 != shape_fcn(0, maneuver_time, diameter, direction, initial_altitude, step_time, *shape_args)[0] or 0 != shape_fcn(0, maneuver_time, diameter, direction, initial_altitude, step_time, *shape_args)[1]:
            print("different Start and Manuever")
            maneuver_start_x = shape_fcn(0, maneuver_time, diameter, direction, initial_altitude, step_time, *shape_args)[0];
            maneuver_start_y = shape_fcn(0, maneuver_time, diameter, direction, initial_altitude, step_time, *shape_args)[1];
            
            print(f"Origin Start: {start_x} , {start_y}")
            print(f"Manuever Start: {maneuver_start_x} , {maneuver_start_y}")

            # Calculate distance and time required to move to first setpoint of maneuver
            move_distance = math.sqrt(( maneuver_start_x)**2 + ( maneuver_start_y)**2)
            move_time = move_distance / 2.0
            move_steps = int(move_time / step_time)

            # Move drone to first setpoint of maneuver at 2 m/s
            for i in range(move_steps):
                t = climb_time + move_start_time + hold_time + hold_time + i * step_time
                ratio = i / move_steps
                x = start_x + (maneuver_start_x  ) * ratio
                y = start_y + (maneuver_start_y ) * ratio
                z = -1 * initial_altitude
                vx = move_speed * (maneuver_start_x ) / move_distance
                vy = move_speed * (maneuver_start_y ) / move_distance
                vz = 0.0
                ax = 0
                ay = 0
                az = 0
                yaw = 0
                
                mode = 50
                row = [climb_steps + hold_steps + move_start_steps + hold_steps  + i, t, x, y, z, vx, vy, vz,0,0,0, yaw,mode, "nan", "nan", "nan"]
                writer.writerow(row)

            # Hold drone at first setpoint for 2 seconds
            for i in range(hold_steps):
                t = climb_time + hold_time + move_start_time + move_time + hold_time + i * step_time
                x =  start_x + shape_fcn(0, maneuver_time, diameter, direction, initial_altitude, step_time, *shape_args)[0]
                y = start_y + shape_fcn(0, maneuver_time, diameter, direction, initial_altitude, step_time, *shape_args)[1]
                z = -1 * initial_altitude
                vx = 0.0
                vy = 0.0
                vz = 0.0
                ax = 0
                ay = 0
                az = 0
                yaw = 0
                mode = 60
                row = [climb_steps + hold_steps + move_steps + move_start_steps + hold_steps  + i, t, x, y, z, vx, vy, vz, 0 ,0,0, yaw,mode, "nan", "nan", "nan"]
                writer.writerow(row)

            # Calculate the start time after maneuver start
            start_time = climb_time + hold_time + move_start_time + move_time + hold_time  + hold_time
        else:
            # Calculate the start time after maneuver start
            start_time = climb_time + hold_time + move_start_time + hold_time
            move_distance=0
            move_steps =0
            move_time=0

        # Calculate the total duration of the trajectory after maneuver start
        total_duration = maneuver_time + start_time
        total_steps = int(total_duration / step_time)
        maneuver_steps = int(maneuver_time / step_time)

    

        # Fly the shape trajectory
        last_x, last_y, last_z = 0, 0, 0  # Initialize variables to store the last position

        for step in range(maneuver_steps):
            x, y, z, vx, vy, vz, ax, ay, az = shape_fcn(step, maneuver_time, diameter, direction, initial_altitude, step_time, *shape_args)
            x += start_x
            y += start_y
            yaw = 0
            missionTime = start_time + step * step_time
            mode = 70
            row = [climb_steps + hold_steps + move_steps + hold_steps + move_steps + hold_steps + step, missionTime, x, y, z, vx, vy, vz, ax, ay, az, yaw, mode, "nan", "nan", "nan"]
            writer.writerow(row)
            last_x, last_y, last_z = x, y, z  # Update the last position

           
        # Hold drone at last maneuver setpoint for hold_time
        for i in range(hold_steps):
            t = start_time + maneuver_time + i * step_time
            x, y, z = last_x, last_y, last_z  # Use the last position
            vx = 0.0
            vy = 0.0
            vz = 0.0
            ax = 0
            ay = 0
            az = 0
            yaw = 0
            mode = 80
            row = [climb_steps + hold_steps + move_steps + hold_steps + move_steps + hold_steps + step + i, t, x, y, z, vx, vy, vz, ax, ay, az, yaw, mode, "nan", "nan", "nan"]
            writer.writerow(row)

        # Return to origin (0, 0, -initial_altitude)
        return_distance = math.sqrt(last_x**2 + last_y**2 + ((-1 * initial_altitude) - last_z)**2)  # Use the last position
        return_time = return_distance / move_speed
        return_steps = int(return_time / step_time)

        for i in range(return_steps):
            t = start_time + maneuver_time + hold_time + i * step_time
            ratio = i / return_steps
            x_home = last_x * (1 - ratio)  # Use the last position
            y_home = last_y * (1 - ratio)  # Use the last position
            z_home = last_z + ((-1 * initial_altitude) - last_z) * ratio  # Use the last position
            vx = - move_speed * last_x / return_distance  # Use the last position
            vy = - move_speed * last_y / return_distance  # Use the last position
            vz = ((-1 * initial_altitude) - last_z) / return_time  # Use the last position
            ax = 0
            ay = 0
            az = 0
            yaw = 0
            mode = 90
            row = [climb_steps + hold_steps + move_steps + hold_steps + move_steps + hold_steps + step + i + return_steps, t, x_home, y_home, z_home, vx, vy, vz, ax , ay , az, yaw,mode, "nan", "nan", "nan"]
            writer.writerow(row)
            
            
        print(f"Created {output_file} with the {shape_name}.")


