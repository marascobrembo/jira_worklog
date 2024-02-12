import logging

from app_data import AppData
from app_logic import AppLogic
from app_gui import App


def main() -> None:
    # Basic logger configuration
    logging.basicConfig(
        filename="issue_not_map.log",
        filemode="w",
        level=logging.INFO,
    )

    # Create the Gui
    app_data = AppData()
    app_logic = AppLogic(app_data)
    gui = App(app_data, app_logic)

    gui.show_window()


if __name__ == "__main__":
    main()
