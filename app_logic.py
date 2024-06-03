import threading
from app_data import AppData
from constants import MONTHS
from logging_conf import logger
import jira_log_manager as jm
import custom_exceptions as ce


class AppLogic:
    def __init__(self, app_data: AppData):
        self._app_data: AppData = app_data
        self.check_api_token_validity()

    def load_worklog_handler(self) -> None:
        logger.info("Start button pushed!")
        _file_path: str = self._app_data.selected_file_path
        _jira_map_file: str = self._app_data.jira_map_file
        _selected_month: int = MONTHS[self._app_data.selected_month]
        _selected_user: str = self._app_data.selected_user

        logger.info(f"Excel file path: {_file_path}")
        logger.info(f"Selected month: {_selected_month}")
        logger.info(f"Selected user: {_selected_user}")

        _load_worklog_thread = threading.Thread(
            target=jm.load_worklog,
            args=(
                self._app_data.jira,
                _file_path,
                _jira_map_file,
                _selected_month,
                _selected_user,
            ),
        )

        _load_worklog_thread.start()

    def check_api_token_validity(self) -> None:
        try:
            self._app_data.instantiate_jira_class()
            logger.info(
                f"Successfully connected to Jira as user {self._app_data.get_username()}"
            )
            self._app_data.is_api_token_valid = True
        except ce.JiraConnectionError as e:
            logger.error(e)
            self._app_data.is_api_token_valid = False
