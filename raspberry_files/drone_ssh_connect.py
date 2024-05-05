# Project: SAR with SWARM DRONES
# Author: Wyatt Colburn, wdcolbur@calpoly.edu
# Description: This program allows ssh into drone1 rp when connected to CP IOT
# only portioned need to change for different rp are ip, username, password
# Dependicies: pexpect (pip install pexpect)
# Revision History: 3/13/2024 initial setup 



import pexpect
import argparse


def ssh_into_raspberry_pi(drone_ID):
    # Prompt user for Raspberry Pi IP address

    if drone_ID == "Drone1":
        raspberry_pi_ip = "10.40.127.129"
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

    # Construct the ssh command as a string
    ssh_command = f"ssh {username}@{raspberry_pi_ip}"

    try:
        # Spawn a child process to handle the ssh session
        ssh_session = pexpect.spawn(ssh_command)

        # Wait for the password prompt and send the password
        ssh_session.expect("password:")
        ssh_session.sendline(password)

        # Interact with the ssh session
        ssh_session.interact()

    except pexpect.EOF:
        print("SSH session terminated.")
    except pexpect.TIMEOUT:
        print("Timeout occurred while waiting for SSH response.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SSH into Drone Raspberry Pi')
    parser.add_argument('drone_ID', type=str, help='Enter Drone ID: Drone1, Drone2, Drone3')
    args=parser.parse_args()
    ssh_into_raspberry_pi(args.drone_ID)
