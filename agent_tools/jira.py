import os
import random
from langchain_core.tools import StructuredTool
from datetime import datetime, timedelta
from typing import Annotated
from jira.client import JIRA, Issue, ResultList

JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN", "")
JIRA_PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "")

jira = JIRA(
    options={"server": "https://tripledotstudios.atlassian.net", "verify": True},
    basic_auth=(JIRA_EMAIL, JIRA_TOKEN),
)


def _jira_issues(days: Annotated[int | str, "Number of days"]) -> str:
    """Retrieves completed JIRA issues from the last `days` days."""
    try:
        days = int(days)
    except ValueError:
        days = 14
    ISSUES_PAGE_SIZE = 50
    MAX_ISSUES = 10
    start_at = 0
    result = []
    end_date = datetime.now() - timedelta(days=24)
    start_date = end_date - timedelta(days=days)
    search_query = f'project = "{JIRA_PROJECT_KEY}" and updated >= {start_date:%Y-%m-%d} and updated <= {end_date:%Y-%m-%d} and status CHANGED TO "Done"'
    api_issues: ResultList[Issue] = jira.search_issues(
        jql_str=search_query, startAt=start_at, maxResults=ISSUES_PAGE_SIZE
    )  # type: ignore
    while start_at < api_issues.total:
        for issue in api_issues:
            result.append(f"{issue.key}: {issue.fields.summary} by {issue.fields.assignee}")
        start_at += ISSUES_PAGE_SIZE
        api_issues = jira.search_issues(
            jql_str=search_query, startAt=start_at, maxResults=ISSUES_PAGE_SIZE
        )  # type: ignore
    return "\n".join(random.sample(result, min(MAX_ISSUES, len(result)))) or "No issues found"


jira_issues = StructuredTool.from_function(_jira_issues)
