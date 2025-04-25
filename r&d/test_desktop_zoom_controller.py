from scouter_agent.screen_controller.desktop_zoom_controller import DesktopZoomController
from scouter_agent.infrastructure.capture_devices import CaptureConfig

if __name__ == "__main__":
    # Define consistent config for BlueStacks window
    config = CaptureConfig(
        title="BlueStacks",
        game_res=(720, 1280),     # Adjust if your Bluestacks game resolution differs
        game_anchor="br",         # Assuming bottom-right anchoring
        border_trim=(0.08, 0.16, 0.05, 0.1)
    )

    zoomer = DesktopZoomController(config=config, scroll_steps=2, scroll_amount=-10)
    zoomer.zoom_out()
