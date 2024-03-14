# Project: SAR with SWARM DRONES
# Author: Wyatt Colburn, wdcolbur@calpoly.edu
# Description: This program allows ssh into drone1 rp when connected to CP IOT
# only portioned need to change for different rp are ip, username, password
# Dependicies: pexpect (pip install pexpect)
# Revision History: 3/13/2024 initial setup 



import pexpect

def ssh_into_raspberry_pi():
    # Prompt user for Raspberry Pi IP address
    raspberry_pi_ip = "10.40.126.73"

    username = "sar"
    password = "drone1"
    

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
    ssh_into_raspberry_pi()


