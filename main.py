import logging_conf
from app_data import AppData
from app_gui import App
from app_logic import AppLogic


def main() -> None:
    # Create the Gui
    app_data = AppData()
    app_logic = AppLogic(app_data)
    gui = App(app_data, app_logic)

    gui.show_window()


if __name__ == "__main__":
    # Logger configuration
    logging_conf.setup_logging()

    main()
