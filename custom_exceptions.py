class JiraConnectionError(Exception):
    def __init__(self, message):
        _message: str = f"{message}. Unable to connect to Jira. Please update the API token or verify the internet connection and try again."
        super().__init__(_message)


class NetworkConnectionError(JiraConnectionError):
    def __init__(self, message):
        super().__init__(message)


class AIAError(NetworkConnectionError):
    def __init__(self, message):
        super().__init__(message)
