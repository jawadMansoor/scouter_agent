import subprocess
import socket
import time
import threading
import os

class MiniTouchController:
    def __init__(self, device_id, architecture="android-x86", port=1111, screen_res=(1080, 1920)):
        self.device_id = device_id
        self.architecture = architecture
        self.port = port
        self.screen_res = screen_res
        self.minitouch_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), f"minitouch_binaries/{architecture}/bin/minitouch")
        )


    def deploy(self):
        print(f"🚀 Deploying minitouch to {self.device_id}...")
        subprocess.run(["adb", "-s", self.device_id, "push", self.minitouch_path, "/data/local/tmp/"], check=True)
        subprocess.run(["adb", "-s", self.device_id, "shell", "chmod", "755", "/data/local/tmp/minitouch"], check=True)

    def start(self):
        print(f"🖐️ Starting minitouch on {self.device_id}...")
        threading.Thread(target=self._run_daemon, daemon=True).start()
        time.sleep(2)

        subprocess.run(["adb", "-s", self.device_id, "forward", f"tcp:{self.port}", "localabstract:minitouch"], check=True)
        print(f"🔗 Port forwarding on tcp:{self.port}")

    def _run_daemon(self):
        subprocess.run(["adb", "-s", self.device_id, "shell", "/data/local/tmp/minitouch"])

    def zoom_out(self):
        print("🔍 Sending zoom out gesture...")
        width, height = self.screen_res
        mid_x = width // 2
        mid_y = height // 2

        gesture = f"""
d 0 {mid_x - 10} {mid_y} 50
d 1 {mid_x + 10} {mid_y} 50
c
w 100
m 0 {mid_x - 100} {mid_y} 50
m 1 {mid_x + 100} {mid_y} 50
c
w 100
u 0
u 1
c
"""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', self.port))
            time.sleep(1)
            s.sendall(gesture.encode('utf-8'))
        print("✅ Zoom out complete.")

    def initialize(self):
        self.deploy()
        self.start()
