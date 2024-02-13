from app_data import AppData
from constants import MONTHS
import logging
import jira_log_manager as jm


class AppLogic:
    def __init__(self, app_data: AppData):
        self._app_data = app_data
        self.check_api_token_validity()

    def load_worklog_handler(self) -> None:
        logging.info("Start button pushed!")
        _file_path: str = self._app_data.selected_file_path
        _selected_month: int = MONTHS[self._app_data.selected_month]
        _selected_user: str = self._app_data.selected_file_path

        logging.info(f"Excel file path: {_file_path}")
        logging.info(f"Selected month: {_selected_month}")
        logging.info(f"Selected user: {_selected_user}")

        jm.load_worklog(
            self._app_data.jira,
            _file_path,
            _selected_month,
            _selected_user
        )

        logging.info("Worklog loaded!")

    def check_api_token_validity(self):
        try:
            self._app_data.instantiate_jira_class()
            logging.info(f"Successfully connected to Jira as user {self._app_data.get_username()}")
            self._app_data.is_api_token_valid = True
        except Exception as e:  # TODO
            print(e)
            logging.error("Unable to connect to Jira. Please update the API token and try again.")
            self._app_data.is_api_token_valid = False
