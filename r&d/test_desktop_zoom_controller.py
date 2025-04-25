from scouter_agent.screen_controller.desktop_zoom_controller import DesktopZoomController


if __name__ == "__main__":
    zoomer = DesktopZoomController(scroll_steps=1, scroll_amount=150)
    zoomer.zoom_out()
