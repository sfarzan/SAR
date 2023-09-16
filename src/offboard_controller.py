import logging
import asyncio
import subprocess
import psutil  # Import psutil to find and kill existing MAVSDK server processes
from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw, VelocityNedYaw

class OffboardController:
    """
    This class encapsulates the logic to control a drone in offboard mode
    using the MAVSDK library.
    """

    def __init__(self, drone_config, mavsdk_server_address='localhost', port=50051):
        self.drone_config = drone_config
        self.offboard_follow_update_interval = 0.2
        self.port = port
        self.mavsdk_server_address = mavsdk_server_address
        self.is_offboard = False
        # Add these instance variables 
        self.mavsdk_server_process = None
        self.drone = None

    def start_swarm(self):
        self.is_offboard = True

    def calculate_follow_setpoint(self):
        if self.drone_config.mission == 2 and self.drone_config.state != 0 and int(self.drone_config.swarm.get('follow')) != 0:
            self.drone_config.calculate_setpoints()

    def stop_existing_mavsdk_server(self, port):
        for proc in psutil.process_iter():
            try:
                if "mavsdk_server" in proc.name():
                    for conns in proc.connections(kind='inet'):
                        if conns.laddr.port == port:
                            proc.terminate()
                            logging.info(f"Terminated existing MAVSDK server on port {port}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def start_mavsdk_server(self, port):
        try:
            self.stop_existing_mavsdk_server(port)
            mavsdk_server_process = subprocess.Popen(["./mavsdk_server", "-p", str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            logging.info(f"MAVSDK Server started on port {port}")
            return mavsdk_server_process
        except Exception as e:
            logging.error(f"Error starting MAVSDK Server: {e}")
            return None

    async def connect(self):
        self.mavsdk_server_process = self.start_mavsdk_server(self.port)
        self.drone = System(self.mavsdk_server_address, self.port)

# Rest of connect method...
        
        await self.drone.connect()

        logging.info("Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                logging.info("Drone discovered")
                break
        # Removed redundant call to start_mavsdk_server

    async def set_initial_position(self):
        initial_pos = PositionNedYaw(
            self.drone_config.position_setpoint_NED['north'], 
            self.drone_config.position_setpoint_NED['east'], 
            self.drone_config.position_setpoint_NED['down'], 
            self.drone_config.yaw_setpoint)
        await self.drone.offboard.set_position_ned(initial_pos)
        logging.info(f"Initial setpoint: {initial_pos}")

    async def start_offboard(self):
        """
        Start the offboard mode.
        """
        try:
            await self.drone.offboard.start()
            logging.info("Offboard started.")
            self.is_offboard = True
        except OffboardError as error:
            logging.error(f"Starting offboard mode failed with error code: {error._result.result}")
            return

    async def maintain_position_velocity(self):
        """
        Continuously update the drone's position and velocity setpoints.
        """
        try:
            while True:
                pos_ned_yaw = PositionNedYaw(
                    self.drone_config.position_setpoint_NED['north'],
                    self.drone_config.position_setpoint_NED['east'],
                    self.drone_config.position_setpoint_NED['down'],
                    self.drone_config.yaw_setpoint
                )

                vel_ned_yaw = VelocityNedYaw(
                    self.drone_config.velocity_setpoint_NED['vel_n'],
                    self.drone_config.velocity_setpoint_NED['vel_e'],
                    self.drone_config.velocity_setpoint_NED['vel_d'],
                    self.drone_config.yaw_setpoint
                )

                await self.drone.offboard.set_position_velocity_ned(pos_ned_yaw, vel_ned_yaw)
                logging.debug(f"Setpoint sent | Position: [N:{self.drone_config.position_setpoint_NED.get('north')}, E:{self.drone_config.position_setpoint_NED.get('east')}, D:{self.drone_config.position_setpoint_NED.get('down')}] | Velocity: [N:{self.drone_config.velocity_setpoint_NED.get('vel_n')}, E:{self.drone_config.velocity_setpoint_NED.get('vel_e')}, D:{self.drone_config.velocity_setpoint_NED.get('vel_d')}] | Yaw: {self.drone_config.yaw_setpoint}")

                await asyncio.sleep(0.2)  # Sleep for 200 ms

        except Exception as e:
            logging.error(f"Error in maintain_position_velocity: {e}")
        finally:
            self.stop_mavsdk_server()
            self.is_offboard = False

    async def stop_offboard(self):
        """
        Stop the offboard mode.
        """
        await self.drone.offboard.stop()
        logging.info("Offboard stopped.")
        self.is_offboard = False

    async def land_drone(self):
        """
        Land the drone.
        """
        if self.is_offboard:
            await self.stop_offboard()
            await asyncio.sleep(1)
        await self.drone.action.land()
        logging.info("Drone landing.")

    async def start_offboard_follow(self):
        """
        Initialize and execute offboard following operations.
        """
        await self.connect()
        await self.set_initial_position()
        await self.start_offboard()
        await self.maintain_position_velocity()
        
    def stop_mavsdk_server(self):
        if self.mavsdk_server_process:
            self.mavsdk_server_process.terminate()
        self.mavsdk_server_process = None
        
        if self.drone:
            # Could add something here to disconnect if wanted
            self.drone = None