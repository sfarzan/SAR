# process_formation.py

from functions.plot_drone_paths import plot_drone_paths
from functions.process_drone_files import process_drone_files
from functions.update_config_file import update_config_file

# Process the drone files and output the processed data to another directory
skybrush_dir = 'C:\Users\rusha\OneDrive\Documents\GitHub\SAR\mavsdk_drone_show-0.4\shapes\swarm\skybrush'
processed_dir = 'C:\Users\rusha\OneDrive\Documents\GitHub\SAR\mavsdk_drone_show-0.4\shapes\swarm\processed'
method = 'cubic'
dt = 0.05
SHOW_PLOTS = True


process_drone_files(skybrush_dir, processed_dir, method, dt)

# Update the 'x' and 'y' columns of the config file with the initial position of each drone
config_file = 'config.csv'
update_config_file(skybrush_dir, config_file)

plot_drone_paths(skybrush_dir, processed_dir,SHOW_PLOTS)