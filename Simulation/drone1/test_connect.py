from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address="udp://192.168.0.4:14540")

# Run the async main function
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

