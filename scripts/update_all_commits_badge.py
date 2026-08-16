"""Update the Shields endpoint JSON for the profile's all-commits badge."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
GITHUB_USER = os.environ.get("GITHUB_USER", "ldanh270")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BADGE_PATH = REPOSITORY_ROOT / ".github" / "badges" / "all-commits.json"
START_YEAR = 2008

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
    }
  }
}
"""


def query_commit_count(start: datetime, end: datetime) -> int:
    """Return GitHub's contribution commit count for one time range."""
    payload = {
        "query": QUERY,
        "variables": {
            "login": GITHUB_USER,
            "from": start.isoformat().replace("+00:00", "Z"),
            "to": end.isoformat().replace("+00:00", "Z"),
        },
    }
    request = Request(
        GITHUB_GRAPHQL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "ldanh270-all-commits-badge",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub GraphQL request failed ({error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"GitHub GraphQL request failed: {error.reason}") from error

    if result.get("errors"):
        messages = "; ".join(error.get("message", "Unknown GraphQL error") for error in result["errors"])
        raise RuntimeError(messages)

    user = result.get("data", {}).get("user")
    if user is None:
        raise RuntimeError(f"GitHub user not found: {GITHUB_USER}")

    return int(user["contributionsCollection"]["totalCommitContributions"])


def main() -> None:
    if not GITHUB_TOKEN:
        raise SystemExit("GITHUB_TOKEN or GH_TOKEN is required")

    now = datetime.now(timezone.utc)
    total_commits = 0
    for year in range(START_YEAR, now.year + 1):
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = min(datetime(year + 1, 1, 1, tzinfo=timezone.utc), now)
        if start < end:
            total_commits += query_commit_count(start, end)

    badge = {
        "schemaVersion": 1,
        "label": "All Commits",
        "message": f"{total_commits:,}",
        "color": "green",
        "namedLogo": "github",
        "logoColor": "white",
    }
    BADGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BADGE_PATH.write_text(json.dumps(badge, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {BADGE_PATH} with {total_commits:,} all-time commits.")


if __name__ == "__main__":
    main()
