import datetime
import logging
from jira import JIRA, exceptions
import pandas as pd
import getpass

from constants import JIRA_MAP_FILE, HOUR_TO_SECONDS


# TODO: it is usefull to keep dataframe colums as datetime instead of strings?


def get_user_id() -> str:
    """
    Get the username of the current user.

    Returns:
        str: The username of the current user.
    """

    return getpass.getuser()


def parse_jira_map_file() -> pd.DataFrame:

    # First, read the Multi-index rows
    multiindex_rows: pd.DataFrame = pd.read_excel(
        JIRA_MAP_FILE,
        header=None,
        index_col=None,
        usecols="A:C",
        skiprows=1,
    ).dropna(how="all", axis=0)

    # fill in Null values in rows
    multiindex_rows.iloc[:, 0:2] = multiindex_rows.iloc[:, 0:2].ffill()

    jira_map: pd.DataFrame = (
        pd.read_excel(
            JIRA_MAP_FILE,
            index_col=None,
        )
    ).dropna(how="all", axis=0)

    # create multiindex column names and drop first 3 columns
    jira_map = jira_map.iloc[:, 3:]
    jira_map.index = pd.MultiIndex.from_arrays(multiindex_rows.values.T)

    # Remove empty rows
    jira_map.dropna(how="all", axis=0, inplace=True)

    # Sort multiindex and create a Series
    jira_map = jira_map.sort_index(level=2).squeeze(axis=1).dropna()

    return jira_map


def parse_input_excel_report(excel_path, req_person) -> pd.DataFrame:

    # First, read the Multi-index rows
    multiindex_rows: pd.DataFrame = pd.read_excel(
        excel_path,
        sheet_name=req_person,
        header=None,
        index_col=None,
        usecols="B:D",
        skiprows=7,
    ).dropna(how="all", axis=0)

    # fill in Null values in rows
    multiindex_rows.iloc[:, 0:2] = multiindex_rows.iloc[:, 0:2].ffill()

    # Read excel report without the last column "TOTALE"
    df: pd.DataFrame = (
        pd.read_excel(
            excel_path,
            header=1,
            index_col=None,
            skiprows=[2, 3, 4, 5, 6],
            sheet_name=req_person,
            usecols=lambda x: x != "TOTALE",
        )
        .dropna(how="all", axis=0)
        .dropna(how="all", axis=1)
    )

    # Just name of header
    df.columns.name = "Date"

    # drop first 3 columns that will be substituted by the new index
    df = df.iloc[:, 3:]

    # create multiindex column names
    df.index = pd.MultiIndex.from_arrays(multiindex_rows.values.T)

    # Remove empty colums and rows
    df.dropna(how="all", axis=0, inplace=True)
    df.dropna(how="all", axis=1, inplace=True)

    return df


def log_work_in_issue(jira, issue, issue_series) -> None:

    # Check if the worklog has been already log, in case ignore it
    this_author_worklogs_days: list[str] = [
        datetime.datetime.strptime(worklog.started, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
            "%Y-%m-%d"
        )
        for worklog in jira.worklogs(issue)
        if worklog.author.name == jira.myself()['name']
    ]  # nome del sistema TODO]

    for day, time_spent in issue_series.items():
        if day.strftime("%Y-%m-%d") not in this_author_worklogs_days:
            try:
                jira.add_worklog(
                    issue=issue,
                    timeSpentSeconds=HOUR_TO_SECONDS * time_spent,
                    started=day,
                )
            except exceptions.JIRAError:
                logging.warning(
                    "Cannot log work for the issue %s, issue is closed.", issue
                )


def load_worklog(
    jira: JIRA, excel_report: str, req_month: int, req_person: str
) -> None:

    #  Who has authenticated
    logging.info(jira.myself()['name'])

    # Read the supporting mapping file
    jira_map: pd.DataFrame = parse_jira_map_file()

    # Read the report Excel file
    df: pd.DataFrame = parse_input_excel_report(excel_report, req_person)

    # Keep only the requested month and drop the rest
    first_day_of_req_month: datetime.datetime = datetime.datetime(
        2024, req_month, 1, 0, 0
    )
    last_day_of_req_month: datetime.datetime = (
        first_day_of_req_month + pd.offsets.MonthEnd()
    )
    # first_day_of_req_month.strftime("%Y-%m-%d %H:%M:%S")

    df_month: pd.DataFrame = df.loc[
        :,
        first_day_of_req_month:last_day_of_req_month,
    ]

    # Take the Jira issue associated with the row and signalize the ones with no map
    row_without_jira_issue: list[tuple] = list(
        set(df_month.index) - set(jira_map.index)
    )
    logging.info(str(row_without_jira_issue).strip("[]"))

    df_month_to_log: pd.DataFrame = df_month[
        df_month.index.isin(jira_map.index.to_list())
    ]

    # For each day log the related workload if not nan
    df_month_to_log.apply(
        lambda x: log_work_in_issue(
            jira, issue=jira_map[x.name], issue_series=x.dropna()
        ),
        axis=1,
    )
