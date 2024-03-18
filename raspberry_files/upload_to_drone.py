# Project: SAR with SWARM DRONES
# Author: Wyatt Colburn, wdcolbur@calpoly.edu
# Description: This program allows ssh into drone1 rp when connected to CP IOT
# only portioned need to change for different rp are ip, username, password
# Dependicies: pexpect (pip install pexpect)
# Revision History: 3/13/2024 initial setup 



import pexpect
import argparse
import os
import sys


def upload_to_raspberry_pi(drone_ID, pi_file_path, local_file_path):
    #Config Depending on drone_ID
    if drone_ID == "Drone1":
        raspberry_pi_ip = "10.40.126.73"
        username = "sar"
        password = "drone1"
    elif drone_ID == "Drone2":
        raspberry_pi_ip = "10.40.126.55"
        username = "ander"
        password = "drone2"
    elif drone_ID == "Drone3":
        username = "wyattcolburn"
        raspberry_pi_ip = "10.40.127.129"
        password = "drone3"
    else:
        print("[ERROR] Unrecognized Drone ID: Enter either Drone1, Drone2 or Drone3")
        return

    #Check Local Path Entered by User
    if os.path.isdir(local_file_path):
        scp_command = f"scp -r {local_file_path} {username}@{raspberry_pi_ip}:{pi_file_path}"
    elif os.path.isfile(local_file_path):
        scp_command = f"scp {local_file_path} {username}@{raspberry_pi_ip}:{pi_file_path}"
    else:
        print(f"[ERROR] {local_file_path} does not exist or is not a valid path")
        return

    # Spawn a child process to handle scp
    scp_session = pexpect.spawn(scp_command, logfile=sys.stdout.buffer)

    # Wait for the password prompt and send the password
    scp_session.expect(f"{username}@{raspberry_pi_ip}'s password:")
    scp_session.sendline(password)

    scp_session.expect(pexpect.EOF, timeout=None)

    exit_status = scp_session.exitstatus
    if exit_status == 0:
        print("SCP transfer successful")
    else: 
        print("[ERROR] SCP transfer failed. Raspberry Pi Address may be invalid")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload File/Directory to Drone Raspberry Pi')
    parser.add_argument('drone_ID', type=str, help='Enter Drone ID: Drone1, Drone2, Drone3')
    parser.add_argument('local_file_path', type=str, help='Enter Local File Path')
    parser.add_argument('pi_file_path', type=str, help='Enter Destination File Path')

    args=parser.parse_args()
    upload_to_raspberry_pi(args.drone_ID, args.pi_file_path, args.local_file_path)
