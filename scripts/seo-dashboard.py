#!/usr/bin/env python3
"""GA4 + Search Console のSEO指標を Google スプレッドシートに自動集計する。

時系列タブ（Daily / Weekly / Monthly）とスナップショットタブ
（TOPページ / 検索クエリ / 流入元 / 人気レシピ / イベント）を毎回まるごと更新する。
GitHub Actions から毎日実行する想定。何度再実行しても結果は同じ（冪等）。

必要な環境変数:
  GA4_CREDENTIALS_JSON … サービスアカウント鍵JSON（既存の週次ジョブと共用）
  SHEETS_ID            … 出力先スプレッドシートのID
"""

import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy,
)
from googleapiclient.discovery import build

GA4_PROPERTY_ID = "529409641"
SC_SITE_URL = "https://www.obaachan-recipe.com/"
HISTORY_START = "2026-03-01"   # この日以降を集計対象にする
SNAPSHOT_DAYS = 28             # スナップショット系タブの集計期間
JST = timezone(timedelta(hours=9))

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]

RECIPE_DETAIL_RE = re.compile(r"^/recipes/[^/]+/?$")

TS_HEADER_DAILY = [
    "日付", "PV", "ユーザー", "新規", "リピーター", "セッション",
    "エンゲージ率%", "平均滞在(秒)",
    "検索クリック", "検索表示回数", "検索CTR%", "平均掲載順位",
    "自然検索", "SNS", "直接", "参照",
]
# 週次・月次のユーザーは日次の合計（＝延べ。ユニークではない点に注意）
TS_HEADER_AGG = ["期間"] + TS_HEADER_DAILY[1:2] + ["ユーザー(延べ)"] + TS_HEADER_DAILY[3:]


def get_credentials():
    raw = os.environ.get("GA4_CREDENTIALS_JSON")
    if not raw:
        sys.exit("Error: GA4_CREDENTIALS_JSON が未設定です")
    return service_account.Credentials.from_service_account_info(
        json.loads(raw), scopes=SCOPES
    )


def get_sheets_id():
    sid = os.environ.get("SHEETS_ID")
    if not sid:
        sys.exit("Error: SHEETS_ID が未設定です")
    return sid


# ───────────────────────── GA4 ─────────────────────────

def _iso(d8):
    return f"{d8[0:4]}-{d8[4:6]}-{d8[6:8]}"


def channel_bucket(name):
    n = (name or "").lower()
    if "social" in n:
        return "social"
    if n == "direct":
        return "direct"
    if "organic search" in n:
        return "organic_search"
    if "referral" in n:
        return "referral"
    return "other"


def ga4_daily(client, start, end):
    """日付ごとのコア指標 {iso_date: {...}}"""
    req = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="userEngagementDuration"),
        ],
    )
    resp = client.run_report(req)
    out = {}
    for row in resp.rows:
        v = [m.value for m in row.metric_values]
        out[_iso(row.dimension_values[0].value)] = {
            "pv": int(v[0]),
            "users": int(v[1]),
            "new_users": int(v[2]),
            "sessions": int(v[3]),
            "engaged_sessions": int(v[4]),
            "engagement_duration": float(v[5]),
        }
    return out


def ga4_daily_channels(client, start, end):
    """日付×チャネルのセッション数 {iso_date: {bucket: sessions}}"""
    req = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="date"), Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions")],
    )
    resp = client.run_report(req)
    out = {}
    for row in resp.rows:
        d = _iso(row.dimension_values[0].value)
        bucket = channel_bucket(row.dimension_values[1].value)
        sessions = int(row.metric_values[0].value)
        out.setdefault(d, {})
        out[d][bucket] = out[d].get(bucket, 0) + sessions
    return out


def ga4_top_pages(client, start, end, limit=100):
    req = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="activeUsers"),
            Metric(name="userEngagementDuration"),
        ],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=limit,
    )
    resp = client.run_report(req)
    pages = []
    for row in resp.rows:
        path = row.dimension_values[0].value
        title = row.dimension_values[1].value
        pv = int(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        dur = float(row.metric_values[2].value)
        avg = round(dur / users, 1) if users else 0
        pages.append({"path": path, "title": title, "pv": pv, "users": users, "avg": avg})
    return pages


def ga4_channels(client, start, end):
    req = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="sessionDefaultChannelGroup"), Dimension(name="sessionSourceMedium")],
        metrics=[Metric(name="sessions"), Metric(name="activeUsers")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=50,
    )
    resp = client.run_report(req)
    rows = []
    for row in resp.rows:
        rows.append([
            row.dimension_values[0].value,
            row.dimension_values[1].value,
            int(row.metric_values[0].value),
            int(row.metric_values[1].value),
        ])
    return rows


def ga4_events(client, start, end):
    req = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="eventCount"), desc=True)],
        limit=50,
    )
    resp = client.run_report(req)
    return [[row.dimension_values[0].value, int(row.metric_values[0].value)] for row in resp.rows]


# ───────────────────── Search Console ─────────────────────

def sc_daily(sc, start, end):
    body = {"startDate": start, "endDate": end, "dimensions": ["date"], "rowLimit": 25000}
    resp = sc.searchanalytics().query(siteUrl=SC_SITE_URL, body=body).execute()
    out = {}
    for row in resp.get("rows", []):
        out[row["keys"][0]] = {
            "clicks": int(row["clicks"]),
            "impressions": int(row["impressions"]),
            "position": float(row["position"]),
        }
    return out


def sc_top(sc, start, end, dimension, limit=30):
    body = {"startDate": start, "endDate": end, "dimensions": [dimension], "rowLimit": limit}
    resp = sc.searchanalytics().query(siteUrl=SC_SITE_URL, body=body).execute()
    rows = []
    for r in resp.get("rows", []):
        rows.append([
            r["keys"][0],
            int(r["clicks"]),
            int(r["impressions"]),
            round(r["ctr"] * 100, 2),
            round(r["position"], 1),
        ])
    return rows


# ───────────────────── 集計（時系列） ─────────────────────

def _blank_bucket():
    return {
        "pv": 0, "users": 0, "new_users": 0, "sessions": 0,
        "engaged_sessions": 0, "engagement_duration": 0.0,
        "clicks": 0, "impressions": 0, "pos_weight": 0.0,
        "organic_search": 0, "social": 0, "direct": 0, "referral": 0,
    }


def _add(bucket, ga, ch, sc):
    if ga:
        bucket["pv"] += ga["pv"]
        bucket["users"] += ga["users"]
        bucket["new_users"] += ga["new_users"]
        bucket["sessions"] += ga["sessions"]
        bucket["engaged_sessions"] += ga["engaged_sessions"]
        bucket["engagement_duration"] += ga["engagement_duration"]
    if ch:
        for k in ("organic_search", "social", "direct", "referral"):
            bucket[k] += ch.get(k, 0)
    if sc:
        bucket["clicks"] += sc["clicks"]
        bucket["impressions"] += sc["impressions"]
        bucket["pos_weight"] += sc["position"] * sc["impressions"]


def _finalize(label, b):
    eng_rate = round(b["engaged_sessions"] / b["sessions"] * 100, 1) if b["sessions"] else 0
    avg_eng = round(b["engagement_duration"] / b["users"], 1) if b["users"] else 0
    ctr = round(b["clicks"] / b["impressions"] * 100, 2) if b["impressions"] else 0
    pos = round(b["pos_weight"] / b["impressions"], 1) if b["impressions"] else 0
    return [
        label, b["pv"], b["users"], b["new_users"], b["users"] - b["new_users"],
        b["sessions"], eng_rate, avg_eng,
        b["clicks"], b["impressions"], ctr, pos,
        b["organic_search"], b["social"], b["direct"], b["referral"],
    ]


def build_timeseries(daily_ga, daily_ch, daily_sc):
    dates = sorted(set(daily_ga) | set(daily_sc) | set(daily_ch))
    daily_rows, weekly, monthly = [], {}, {}
    for d in dates:
        dt = date.fromisoformat(d)
        ga, ch, sc = daily_ga.get(d), daily_ch.get(d), daily_sc.get(d)

        b = _blank_bucket()
        _add(b, ga, ch, sc)
        daily_rows.append(_finalize(d, b))

        iso_y, iso_w, _ = dt.isocalendar()
        mon = dt - timedelta(days=dt.weekday())
        sun = mon + timedelta(days=6)
        wkey = f"{iso_y}-W{iso_w:02d}"
        wlabel = f"{wkey} ({mon.month}/{mon.day}〜{sun.month}/{sun.day})"
        weekly.setdefault(wkey, [wlabel, _blank_bucket()])
        _add(weekly[wkey][1], ga, ch, sc)

        mkey = f"{dt.year}-{dt.month:02d}"
        monthly.setdefault(mkey, _blank_bucket())
        _add(monthly[mkey], ga, ch, sc)

    weekly_rows = [_finalize(weekly[k][0], weekly[k][1]) for k in sorted(weekly)]
    monthly_rows = [_finalize(k, monthly[k]) for k in sorted(monthly)]
    return daily_rows, weekly_rows, monthly_rows


# ───────────────────────── Sheets ─────────────────────────

def get_tabs(svc, sid):
    meta = svc.spreadsheets().get(spreadsheetId=sid).execute()
    return {s["properties"]["title"] for s in meta["sheets"]}


def ensure_tab(svc, sid, title, existing):
    if title in existing:
        return
    svc.spreadsheets().batchUpdate(
        spreadsheetId=sid,
        body={"requests": [{"addSheet": {"properties": {"title": title}}}]},
    ).execute()
    existing.add(title)


def write_tab(svc, sid, title, header, rows, existing):
    """ヘッダ＋データを A 列から書き直す（既存データ列はクリア。右側の手書きメモ列は残す）"""
    ensure_tab(svc, sid, title, existing)
    last_col = chr(ord("A") + len(header) - 1)
    svc.spreadsheets().values().clear(
        spreadsheetId=sid, range=f"'{title}'!A1:{last_col}"
    ).execute()
    svc.spreadsheets().values().update(
        spreadsheetId=sid,
        range=f"'{title}'!A1",
        valueInputOption="RAW",
        body={"values": [header] + rows},
    ).execute()


def main():
    creds = get_credentials()
    sid = get_sheets_id()
    ga = BetaAnalyticsDataClient(credentials=creds)
    sc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    svc = build("sheets", "v4", credentials=creds, cache_discovery=False)

    yesterday = (datetime.now(JST).date() - timedelta(days=1)).isoformat()
    snap_start = (datetime.now(JST).date() - timedelta(days=SNAPSHOT_DAYS)).isoformat()

    print(f"集計期間: {HISTORY_START} 〜 {yesterday} / スナップショット: 直近{SNAPSHOT_DAYS}日")

    daily_ga = ga4_daily(ga, HISTORY_START, yesterday)
    daily_ch = ga4_daily_channels(ga, HISTORY_START, yesterday)
    daily_sc = sc_daily(sc, HISTORY_START, yesterday)
    daily_rows, weekly_rows, monthly_rows = build_timeseries(daily_ga, daily_ch, daily_sc)

    top_pages = ga4_top_pages(ga, snap_start, yesterday)
    recipe_pages = [p for p in top_pages if RECIPE_DETAIL_RE.match(p["path"])][:30]
    recipe_rows = [
        [i + 1, p["path"], p["title"], p["pv"], p["users"], p["avg"]]
        for i, p in enumerate(recipe_pages)
    ]
    page_rows = [
        [i + 1, p["path"], p["title"], p["pv"], p["users"], p["avg"]]
        for i, p in enumerate(top_pages[:30])
    ]
    query_rows = [[i + 1] + r for i, r in enumerate(sc_top(sc, snap_start, yesterday, "query"))]
    sc_page_rows = [[i + 1] + r for i, r in enumerate(sc_top(sc, snap_start, yesterday, "page"))]
    channel_rows = ga4_channels(ga, snap_start, yesterday)
    event_rows = ga4_events(ga, snap_start, yesterday)

    existing = get_tabs(svc, sid)
    write_tab(svc, sid, "Daily", TS_HEADER_DAILY, daily_rows, existing)
    write_tab(svc, sid, "Weekly", TS_HEADER_AGG, weekly_rows, existing)
    write_tab(svc, sid, "Monthly", TS_HEADER_AGG, monthly_rows, existing)
    write_tab(svc, sid, "TOPページ_28日",
              ["#", "パス", "タイトル", "PV", "ユーザー", "平均滞在(秒)"], page_rows, existing)
    write_tab(svc, sid, "人気レシピ_28日",
              ["#", "パス", "タイトル", "PV", "ユーザー", "平均滞在(秒)"], recipe_rows, existing)
    write_tab(svc, sid, "検索クエリ_28日",
              ["#", "クエリ", "クリック", "表示回数", "CTR%", "掲載順位"], query_rows, existing)
    write_tab(svc, sid, "検索LP_28日",
              ["#", "ページ", "クリック", "表示回数", "CTR%", "掲載順位"], sc_page_rows, existing)
    write_tab(svc, sid, "流入元_28日",
              ["チャネル", "参照元/メディア", "セッション", "ユーザー"], channel_rows, existing)
    write_tab(svc, sid, "イベント_28日", ["イベント名", "回数"], event_rows, existing)
    write_tab(svc, sid, "メタ", ["項目", "値"], [
        ["最終更新(JST)", datetime.now(JST).strftime("%Y-%m-%d %H:%M")],
        ["集計対象開始", HISTORY_START],
        ["集計対象終了", yesterday],
        ["スナップショット期間", f"直近{SNAPSHOT_DAYS}日"],
        ["注記", "Weekly/Monthlyのユーザーは日次合計(延べ)。ユニークではない"],
    ], existing)

    print(f"完了: Daily {len(daily_rows)}行 / Weekly {len(weekly_rows)}行 / Monthly {len(monthly_rows)}行")


if __name__ == "__main__":
    main()
