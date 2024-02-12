import logging
import os
import tempfile
from pathlib import Path
import customtkinter as ctk
import json

from jira import JIRA

from constants import CONFIG_FILE, TEMP_FOLDER_NAME, HOST_NAME
from get_certificate_chain_download import SSLCertificateChainDownloader
from jira_log_manager import SERVER_URL


def get_ssl_certificate():
    # TODO: gestire eccezioni in caso di fallimento nel download

    # Get up-dated ssl certificates
    out_temp_dir: str = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
    downloader = SSLCertificateChainDownloader(output_directory=out_temp_dir)
    result = downloader.run({"host": HOST_NAME, "remove_ca_files": True})
    # Extracting the path from the result
    certificate_path = Path(result.get('files')[0]) if 'files' in result and result.get('files') else None
    return certificate_path


def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "appearance_theme": "system",
            "api_key": "",
            "selected_user": "",
            "selected_month": "",
            "excel_file_path": ""
        }


class AppData:
    def __init__(self):
        self._config = load_config()

        self._ssl_certificate_path = get_ssl_certificate()
        self._is_api_token_valid = False
        self._num_available_licenses = 0

        self.selected_file_path_var = None
        self.selected_month_var = None
        self.selected_user_var = None

        self._jira = None

    def instantiate_jira_class(self):
        self._jira = JIRA(server=SERVER_URL,
                          token_auth=self.api_key_token,
                          options={"verify": self.ssl_certificate_path})

    def instantiate_view_variables(self):
        self.selected_user_var = ctk.StringVar()
        self.selected_user_var.set(self.selected_user)
        self.selected_user_var.trace_add("write", self.update_selected_user)

        self.selected_month_var = ctk.StringVar()
        self.selected_month_var.set(self.selected_month)
        self.selected_month_var.trace_add("write", self.update_selected_month)

        self.selected_file_path_var = ctk.StringVar()
        self.selected_file_path_var.set(self.selected_file_path)
        self.selected_file_path_var.trace_add("write", self.update_selected_file_path)

    def update_selected_user(self, var, index, mode):
        self.selected_user = self.selected_user_var.get()

    def update_selected_month(self, var, index, mode):
        self.selected_month = self.selected_month_var.get()

    def update_selected_file_path(self, var, index, mode):
        self.selected_file_path = self.selected_file_path_var.get()

    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding="utf-8") as file:
            json.dump(self._config, file)

    @property
    def selected_user(self) -> str:
        return self._config["selected_user"]

    @selected_user.setter
    def selected_user(self, new_value: str) -> None:
        self._config["selected_user"] = new_value

    @property
    def selected_month(self) -> str:
        return self._config["selected_month"]

    @selected_month.setter
    def selected_month(self, new_value: str) -> None:
        self._config["selected_month"] = new_value

    @property
    def selected_file_path(self) -> str:
        return self._config["selected_file_path"]

    @selected_file_path.setter
    def selected_file_path(self, new_value: str) -> None:
        self._config["selected_file_path"] = new_value

    @property
    def is_api_token_valid(self) -> bool:
        return self._is_api_token_valid

    @is_api_token_valid.setter
    def is_api_token_valid(self, value: bool):
        self._is_api_token_valid = value

    @property
    def appearance_theme(self) -> str:
        return self._config["appearance_theme"]

    @property
    def api_key_token(self) -> str:
        return self._config["api_key_token"]

    @api_key_token.setter
    def api_key_token(self, value):
        self._config["api_key_token"] = value

    @property
    def ssl_certificate_path(self) -> Path:
        return self._ssl_certificate_path

    def get_username(self) -> str:
        return self._jira.myself()['name']
