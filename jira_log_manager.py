import datetime
import getpass
from typing import Any

import customtkinter as ctk
import pandas as pd
from jira import JIRA, exceptions

from constants import HOUR_TO_SECONDS
from logging_conf import logger

# TODO: it is usefull to keep dataframe colums as datetime instead of strings?


def get_user_id() -> str:
    """Get the username of the current user.

    Returns:
        str: The username of the current user.
    """
    return getpass.getuser()


def parse_jira_map_file(jira_map_file) -> pd.DataFrame:
    # First, read the Multi-index rows
    multiindex_rows: pd.DataFrame = pd.read_excel(
        jira_map_file,
        header=None,
        index_col=None,
        usecols="A:C",
        skiprows=1,
    ).dropna(how="all", axis=0)

    # fill in Null values in rows
    multiindex_rows.iloc[:, 0:2] = multiindex_rows.iloc[:, 0:2].ffill()

    jira_map: pd.DataFrame = (
        pd.read_excel(
            jira_map_file,
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


def log_work_in_issue(
    jira,
    issue,
    issue_series,
) -> None:
    # Check if the worklog has been already log, in case ignore it
    this_author_worklogs_days: list[str] = [
        datetime.datetime.strptime(worklog.started, "%Y-%m-%dT%H:%M:%S.%f%z").strftime(
            "%Y-%m-%d"
        )
        for worklog in jira.worklogs(issue)
        if worklog.author.name == jira.myself()["name"]
    ]

    for day, time_spent in issue_series.items():
        if day.strftime("%Y-%m-%d") not in this_author_worklogs_days:
            try:
                jira.add_worklog(
                    issue=issue,
                    timeSpentSeconds=HOUR_TO_SECONDS * time_spent,
                    started=day,
                )
            except exceptions.JIRAError:
                logger.warning(
                    "Cannot log work for the issue %s, issue is closed.", issue
                )
        else:
            logger.info("Work already logged for issue %s for %s", issue, day)


def log_work_in_batches(
    jira: JIRA, df_month_to_log: pd.DataFrame, jira_map: pd.DataFrame, progress_bar_var
) -> None:
    """Log work hours in batches to JIRA issues based on provided dataframes.

    Parameters:
    jira (JIRA): An authenticated JIRA client instance.
    df_month_to_log (pd.DataFrame): DataFrame containing the hours of the selected month to be logged.
    jira_map (pd.DataFrame): DataFrame mapping the DataFrame indices to JIRA issue keys.
    """
    try:
        # Fetch the current user's name from JIRA
        author_name: str = jira.myself()["emailAddress"].lower()
    except Exception as e:
        logger.error(f"Failed to fetch author name: {e}")
        raise

    total_worklog_number: int = df_month_to_log.shape[0]
    progress_bar_value: float = 0.0
    step_size: float = 1 / total_worklog_number

    # Iterate over each issue and its corresponding work log group
    for issue, group in df_month_to_log.groupby(jira_map):
        try:
            # Transform group into a Series and collapse more rows mapped with the same issue
            group: pd.Series = group.sum()

            # Fetch existing worklogs for the issue
            existing_worklogs = jira.worklogs(issue)

            # Get a set of days on which the author has already logged work
            this_author_worklogs_days: set[str] = {
                datetime.datetime.strptime(
                    worklog.started, "%Y-%m-%dT%H:%M:%S.%f%z"
                ).strftime("%Y-%m-%d")
                for worklog in existing_worklogs
                if worklog.author.emailAddress.lower() == author_name
            }

            # Create a list of worklog entries to be added
            worklog_entries: list[dict[str, Any]] = [
                {
                    "timeSpentSeconds": int(hours * HOUR_TO_SECONDS),
                    "started": day,
                }
                for day, hours in group.items()
                if hours and day.strftime("%Y-%m-%d") not in this_author_worklogs_days
            ]

            # If there are any worklog entries to add, attempt to log them in JIRA
            if worklog_entries:
                try:
                    for entry in worklog_entries:
                        jira.add_worklog(issue=issue, **entry)
                    logger.info(
                        f"Logged {len(worklog_entries)} worklog(s) for issue {issue}"
                    )

                except exceptions.JIRAError:
                    logger.warning(
                        f"Cannot log work for the issue {issue}, issue might be closed."
                    )
            else:
                # Log information if work has already been logged for these days
                for day in group.index:
                    if day.strftime("%Y-%m-%d") in this_author_worklogs_days:
                        logger.info(
                            f"Work already logged for issue {issue} on {day.strftime('%Y-%m-%d')}"
                        )

        except exceptions.JIRAError as e:
            logger.warning(f"Failed to fetch worklogs for issue {issue}: {e}")

        finally:
            # Increase progress bar step
            progress_bar_value = progress_bar_value + step_size
            progress_bar_var.set(progress_bar_value)


def load_worklog(
    jira: JIRA,
    excel_report: str,
    jira_map_file: str,
    req_month: int,
    req_person: str,
    progress_bar_var: ctk.DoubleVar,
) -> None:
    # Read the supporting mapping file
    jira_map: pd.DataFrame = parse_jira_map_file(jira_map_file)

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
    ].dropna(how="all", axis=0)

    # Take the Jira issue associated with the row and signalize the ones with no map
    row_without_jira_issue: list[tuple] = list(
        set(df_month.index) - set(jira_map.index)
    )
    logger.info(
        "Rows without Jira issues: "
        + "\n".join([str(i) for i in row_without_jira_issue])
    )

    df_month_to_log: pd.DataFrame = df_month[
        df_month.index.isin(jira_map.index.to_list())
    ]

    # Batch log the related workload if not nan
    log_work_in_batches(jira, df_month_to_log, jira_map, progress_bar_var)

    # For each day, log the related workload if not nan
    # df_month_to_log.apply(lambda x: log_work_in_issue(jira,issue=jira_map[x.name],issue_series=x.dropna()),axis=1)

    logger.info("Worklog loaded!")
