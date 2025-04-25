from scouter_agent.infrastructure.minitouch_controller import MiniTouchController
import os
if __name__ == "__main__":
    print(os.getcwd())
    controller = MiniTouchController(device_id="emulator-5554", architecture="x86", screen_res=(1280, 720))
    controller.initialize()
    controller.zoom_out()
