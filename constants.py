# Contstants
CONFIG_FILE = r"./resources/config.json"

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

USERS_LIST: list[str] = [
    "Longoni Samuele",
    "Papi Lorenzo",
    "Perrino Francesco",
    "Di Palma Federico",
    "Marasco Leonardo",
    "Iuculano Matilde",
    "Panzeri Samuele",
]

HOST_NAME = "itstezmec01"

JIRA_ICON_PATH = "./resources/jira_logo.ico"
CHECK_ICON_PATH = "./resources/check.png"
CROSS_ICON_PATH = "./resources/cross.png"

TEMP_FOLDER_NAME = "jira_worklog_temp"
SERVER_URL = "https://itstezmec01/jira/"

# Constants
HOUR_TO_SECONDS = 3600

# Mapping file
JIRA_MAP_FILE = (
    r"C:\Users\conteo49\OneDrive - Brembo\Jira Worklog Tool\jira issue mapping.xlsx"
)