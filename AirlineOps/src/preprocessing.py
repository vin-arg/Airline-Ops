import pandas as pd

DELAY_CAUSES = [
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "SecurityDelay",
    "LateAircraftDelay",
]

DELAY_LABELS = {
    "CarrierDelay": "Carrier",
    "WeatherDelay": "Weather",
    "NASDelay": "NAS / ATC",
    "SecurityDelay": "Security",
    "LateAircraftDelay": "Late Aircraft",
}

CANCEL_CODES = {
    "A": "Carrier",
    "B": "Weather",
    "C": "NAS / ATC",
    "D": "Security",
}

DAY_LABELS = {
    1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"
}

MONTH_LABELS = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], format="%m-%d-%Y", errors="coerce")
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    df["Route"] = df["Origin"].astype(str) + " → " + df["Dest"].astype(str)
    df["OnTime"] = ((df["ArrDelay"] <= 0) & (df["Cancelled"] == 0)).astype("int8")
    df["CancelLabel"] = df["CancellationCode"].map(CANCEL_CODES).fillna("N/A")
    return df


def kpis(df: pd.DataFrame) -> dict:
    total = len(df)
    on_time_rate = df["OnTime"].mean() * 100
    cancel_rate = df["Cancelled"].mean() * 100
    delayed = df.loc[(df["ArrDelay"] > 0) & (df["Cancelled"] == 0), "ArrDelay"]
    avg_delay = delayed.mean() if not delayed.empty else 0.0
    return {
        "total_flights": total,
        "on_time_rate": on_time_rate,
        "cancel_rate": cancel_rate,
        "avg_delay": avg_delay,
    }


def delay_causes_summary(df: pd.DataFrame) -> pd.DataFrame:
    totals = df[DELAY_CAUSES].sum().reset_index()
    totals.columns = ["Cause", "Minutes"]
    totals["Cause"] = totals["Cause"].map(DELAY_LABELS)
    totals = totals[totals["Minutes"] > 0]
    return totals.sort_values("Minutes", ascending=False)


def carrier_performance(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby(["UniqueCarrier", "Airline"], observed=True)
        .agg(
            Flights=("ArrDelay", "count"),
            OnTimeRate=("OnTime", "mean"),
            AvgArrDelay=("ArrDelay", "mean"),
            CancellationRate=("Cancelled", "mean"),
        )
        .reset_index()
    )
    grp["OnTimeRate"] = (grp["OnTimeRate"] * 100).round(1)
    grp["CancellationRate"] = (grp["CancellationRate"] * 100).round(2)
    grp["AvgArrDelay"] = grp["AvgArrDelay"].round(1)
    grp["Airline"] = grp["Airline"].astype(str)
    return grp.sort_values("OnTimeRate", ascending=False)


def top_delayed_routes(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    grp = (
        df.groupby("Route")
        .agg(
            Flights=("ArrDelay", "count"),
            AvgDelay=("ArrDelay", "mean"),
            CancellationRate=("Cancelled", "mean"),
        )
        .reset_index()
    )
    grp = grp[grp["Flights"] >= 50]
    grp["AvgDelay"] = grp["AvgDelay"].round(1)
    grp["CancellationRate"] = (grp["CancellationRate"] * 100).round(2)
    return grp.nlargest(n, "AvgDelay")


def cancellation_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    cancelled = df[df["Cancelled"] == 1]
    counts = cancelled["CancelLabel"].value_counts().reset_index()
    counts.columns = ["Reason", "Flights"]
    return counts[counts["Reason"] != "N/A"]


def airport_disruptions(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    grp = (
        df.groupby(["Origin", "Org_Airport"], observed=True)
        .agg(
            Flights=("DepDelay", "count"),
            AvgDepDelay=("DepDelay", "mean"),
            CancellationRate=("Cancelled", "mean"),
        )
        .reset_index()
    )
    grp = grp[grp["Flights"] >= 100]
    grp["AvgDepDelay"] = grp["AvgDepDelay"].round(1)
    grp["CancellationRate"] = (grp["CancellationRate"] * 100).round(2)
    grp["Org_Airport"] = grp["Org_Airport"].astype(str)
    return grp.nlargest(n, "AvgDepDelay")


def delay_by_day(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("DayOfWeek")
        .agg(AvgDelay=("ArrDelay", "mean"), Flights=("ArrDelay", "count"))
        .reset_index()
    )
    grp["Day"] = grp["DayOfWeek"].map(DAY_LABELS)
    grp["AvgDelay"] = grp["AvgDelay"].round(1)
    return grp


def delay_by_month(df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        df.groupby("Month")
        .agg(AvgDelay=("ArrDelay", "mean"), Flights=("ArrDelay", "count"))
        .reset_index()
    )
    grp["MonthName"] = grp["Month"].map(MONTH_LABELS)
    grp["AvgDelay"] = grp["AvgDelay"].round(1)
    return grp
