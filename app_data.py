import json
import os
import tempfile
from pathlib import Path

import customtkinter as ctk
from jira import JIRA

from constants import CONFIG_FILE_PATH, TEMP_FOLDER_NAME
from get_certificate_chain_download import SSLCertificateChainDownloader


def get_ssl_certificate(host_name: str) -> Path:
    # TODO: gestire eccezioni in caso di fallimento nel download

    # Get up-dated ssl certificates

    out_temp_dir: str = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
    downloader = SSLCertificateChainDownloader(output_directory=out_temp_dir)
    result: dict[str, list[str]] = downloader.run(
        {"host": host_name, "remove_ca_files": True}
    )
    # Extracting the path from the result
    certificate_path = (
        Path(result.get("files")[0])
        if "files" in result and result.get("files")
        else None
    )
    return certificate_path


class AppData:
    def __init__(self):
        self.load_config()

        self._ssl_certificate_path: Path = None
        self._is_api_token_valid = False
        self._num_available_licenses = 0

        self.selected_file_path_var = None
        self.selected_month_var = None
        self.selected_user_var = None

        self._jira = None

    def instantiate_jira_class(self) -> None:
        self._ssl_certificate_path: Path = get_ssl_certificate(
            self._config["host_name"]
        )
        self._jira = JIRA(
            server=self._config["server_url"],
            token_auth=self.api_key_token,
            options={"verify": self._ssl_certificate_path},
        )

    def instantiate_view_variables(self) -> None:
        self.selected_user_var = ctk.StringVar()
        self.selected_user_var.set(self.selected_user)
        self.selected_user_var.trace_add("write", self.update_selected_user)

        self.selected_month_var = ctk.StringVar()
        self.selected_month_var.set(self.selected_month)
        self.selected_month_var.trace_add("write", self.update_selected_month)

        self.selected_file_path_var = ctk.StringVar()
        self.selected_file_path_var.set(self.selected_file_path)
        self.selected_file_path_var.trace_add("write", self.update_selected_file_path)

    def update_selected_user(self, var, index, mode) -> None:
        self.selected_user = self.selected_user_var.get()

    def update_selected_month(self, var, index, mode) -> None:
        self.selected_month = self.selected_month_var.get()

    def update_selected_file_path(self, var, index, mode) -> None:
        self.selected_file_path = self.selected_file_path_var.get()

    def load_config(self) -> None:
        try:
            with open(CONFIG_FILE_PATH, encoding="utf-8") as file:
                self._config = json.load(file)
        except FileNotFoundError:
            self._config: dict[str, str] = {
                "appearance_theme": "system",
                "api_key": "",
                "selected_user": "",
                "selected_month": "",
                "excel_file_path": "",
                "jira_map_file": "",
            }

    def save_config(self) -> None:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as file:
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
        return self._jira.myself()["name"]

    @property
    def jira(self):
        return self._jira

    @property
    def jira_map_file(self) -> str:
        return self._config["jira_map_file"]

    @property
    def config(self) -> dict[str, str]:
        return self._config
