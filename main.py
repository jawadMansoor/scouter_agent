from scouter_agent.application.services.map_scouter_service import MapScouterService
from scouter_agent.infrastructure.map_navigator import MapNavigator
from scouter_agent.infrastructure.map_explorer import MapExplorer
from scouter_agent.screen_controller.screen_gestures import swipe
import asyncio


def main():
    navigator = MapNavigator(swipe_executor=swipe)
    explorer = MapExplorer(navigator=navigator, total_rows=10, total_columns=10)
    service = MapScouterService(explorer)

    asyncio.run(service.run())

if __name__ == "__main__":
    main()
