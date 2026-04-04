#!/usr/bin/env python3
"""GA4 の recipe_view イベントデータを recipes.json の view_count に反映する"""

import json
import os
import sys
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    FilterExpression,
    Filter,
)
from google.oauth2 import service_account

PROPERTY_ID = "529409641"
RECIPES_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "recipes.json")


def get_credentials():
    creds_json = os.environ.get("GA4_CREDENTIALS_JSON")
    if not creds_json:
        print("Error: GA4_CREDENTIALS_JSON not set")
        sys.exit(1)
    info = json.loads(creds_json)
    return service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )


def fetch_view_counts(credentials):
    """GA4 Data API から recipe_view の recipe_id 別カウントを全期間で取得"""
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date="2020-01-01", end_date="today")],
        dimensions=[Dimension(name="customEvent:recipe_id")],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(
            filter=Filter(
                field_name="eventName",
                string_filter=Filter.StringFilter(
                    value="recipe_view",
                    match_type=Filter.StringFilter.MatchType.EXACT,
                ),
            )
        ),
        limit=10000,
    )
    response = client.run_report(request)
    counts = {}
    for row in response.rows:
        recipe_id = row.dimension_values[0].value
        count = int(row.metric_values[0].value)
        counts[recipe_id] = count
    return counts


def update_recipes(view_counts):
    """recipes.json の view_count を更新。変更があれば True を返す"""
    with open(RECIPES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for recipe in data["recipes"]:
        rid = recipe["id"]
        new_count = view_counts.get(rid, 0)
        old_count = recipe.get("view_count", 0)
        if new_count != old_count:
            recipe["view_count"] = new_count
            changed = True
            print(f"  {rid}: {old_count} -> {new_count}")

    if changed:
        with open(RECIPES_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"Updated {RECIPES_PATH}")
    else:
        print("No changes needed.")

    return changed


def set_output(key, value):
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"{key}={value}\n")


def main():
    credentials = get_credentials()
    view_counts = fetch_view_counts(credentials)
    print(f"Fetched view counts for {len(view_counts)} recipes from GA4")
    changed = update_recipes(view_counts)
    set_output("changed", "true" if changed else "false")


if __name__ == "__main__":
    main()
