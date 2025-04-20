from scouter_agent.infrastructure.capture_devices import WindowCapture
import asyncio, cv2

async def main():
    cap = WindowCapture()
    frame = await cap.grab()
    cv2.imshow("frame", frame); cv2.waitKey(0)

asyncio.run(main())
