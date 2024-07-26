"""Contstants."""

from pathlib import Path

working_dir: Path = Path(__file__).resolve().parent

CONFIG_FILE_PATH: str = working_dir / "resources/config.json"
JIRA_ICON_PATH: str = working_dir / "resources/jira_logo.ico"
CHECK_ICON_PATH: str = working_dir / "resources/check.png"
CROSS_ICON_PATH: str = working_dir / "resources/cross.png"
CLOUD_CA_CERT_PATH: str = working_dir / "resources\Forcepoint Cloud CA.cer"
SELF_HOSTED_CA_CERT_PATH: str = working_dir / "resources\Brembo Root CA.crt"


MONTHS: dict[str, int] = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


TEMP_FOLDER_NAME = "jira_worklog_temp"

JIRA_MODE: dict[int, str] = {
    0: "Cloud",  # Default choice
    1: "Self-Hosted",
}

# Constants
HOUR_TO_SECONDS = 3600
