import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from jira.exceptions import JIRAError

import custom_exceptions as ce
import jira_log_manager as jm
from app_data import AppData
from constants import MONTHS
from logging_conf import logger


class AppLogic:
    def __init__(self, app_data: AppData):
        self._app_data: AppData = app_data
        self.JIRA_INITIALIZATION_MAP = {
            0: self._app_data.instantiate_jira_class_cloud,  # Default choice
            1: self._app_data.instantiate_jira_class_self_hosted,
        }
        # asyncio.run(self._app_logic.check_api_token_validity(self, update_icon))

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
                self._app_data.progress_bar_var,
            ),
        )

        _load_worklog_thread.start()

    async def check_api_token_validity(self, update_icon_callback) -> None:
        try:
            self.JIRA_INITIALIZATION_MAP[self._app_data.jira_mode]()
            logger.info(
                f"Successfully connected to Jira as user {self._app_data.get_username()}"
            )
            self._app_data.is_api_token_valid = True
        except (ce.JiraConnectionError, JIRAError, AttributeError) as e:
            logger.error(f"Error connecting to Jira: {e}")
            self._app_data.is_api_token_valid = False
        finally:
            update_icon_callback()
