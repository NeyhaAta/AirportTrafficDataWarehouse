"""
Airport Traffic Data Warehouse - Visualization Code
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd


TARGET_AIRPORTS = ["JFK", "LGA", "ISP"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Make column names lowercase and easier to work with."""
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace(".", "_", regex=False)
    )
    return df


def find_sheet_name(xls: pd.ExcelFile, possible_names: list[str]) -> Optional[str]:
    """Find a sheet even if the capitalization is different."""
    lookup = {sheet.lower(): sheet for sheet in xls.sheet_names}
    for name in possible_names:
        if name.lower() in lookup:
            return lookup[name.lower()]
    return None


def read_gold_excel(path: Path) -> pd.DataFrame:
    """Read Gold star-schema tables and return one analysis-ready DataFrame."""
    xls = pd.ExcelFile(path)

    fact_sheet = find_sheet_name(xls, ["fact_flights", "fact flights", "flights", "Fact_Flights"])
    airport_sheet = find_sheet_name(xls, ["dim_airport", "dim airport", "airports", "Dim_Airport"])
    airline_sheet = find_sheet_name(xls, ["dim_airline", "dim airline", "airlines", "Dim_Airline"])
    date_sheet = find_sheet_name(xls, ["dim_date", "dim date", "dates", "Dim_Date"])

    if fact_sheet is None:
        raise ValueError(f"Could not find fact_flights sheet. Sheets found: {xls.sheet_names}")

    fact = normalize_columns(pd.read_excel(path, sheet_name=fact_sheet))
    df = fact.copy()

    if airport_sheet:
        airports = normalize_columns(pd.read_excel(path, sheet_name=airport_sheet))
        if "airport_id" in airports.columns and "departure_airport_id" in df.columns:
            dep_airports = airports.add_prefix("dep_")
            df = df.merge(
                dep_airports,
                left_on="departure_airport_id",
                right_on="dep_airport_id",
                how="left",
            )
        if "airport_id" in airports.columns and "arrival_airport_id" in df.columns:
            arr_airports = airports.add_prefix("arr_")
            df = df.merge(
                arr_airports,
                left_on="arrival_airport_id",
                right_on="arr_airport_id",
                how="left",
            )

    if airline_sheet:
        airlines = normalize_columns(pd.read_excel(path, sheet_name=airline_sheet))
        if "airline_id" in airlines.columns and "airline_id" in df.columns:
            df = df.merge(airlines, on="airline_id", how="left")

    if date_sheet:
        dates = normalize_columns(pd.read_excel(path, sheet_name=date_sheet))
        if "date_id" in dates.columns and "date_id" in df.columns:
            df = df.merge(dates, on="date_id", how="left")

    return df


def read_silver_csv(path: Path) -> pd.DataFrame:
    """Read cleaned Silver CSV if Gold Excel is not being used."""
    return normalize_columns(pd.read_csv(path, low_memory=False))


def load_data(path: Path) -> pd.DataFrame:
    """Load either an Excel Gold workbook or a Silver CSV."""
    if path.suffix.lower() in [".xlsx", ".xls"]:
        df = read_gold_excel(path)
    elif path.suffix.lower() == ".csv":
        df = read_silver_csv(path)
    else:
        raise ValueError("Input must be .xlsx, .xls, or .csv")

    return clean_analysis_fields(df)


def first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str:
    """Return the first column that exists from a list of possible column names."""
    for col in candidates:
        if col in df.columns:
            return col
    raise KeyError(f"None of these columns were found: {candidates}")


def clean_analysis_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Create standard analysis columns no matter whether input is Gold or Silver."""
    df = df.copy()

    # Departure airport code
    dep_airport_col = first_existing_column(
        df,
        ["dep_iata", "departure_iata", "departure_airport_iata", "dep_airport_iata", "iata"],
    )
    df["departure_airport"] = df[dep_airport_col].astype(str).str.upper().str.strip()
    df = df[df["departure_airport"].isin(TARGET_AIRPORTS)]

    # Airline name
    try:
        airline_col = first_existing_column(df, ["airline_name", "name", "airline"])
        df["airline"] = df[airline_col].fillna("Unknown").astype(str).str.strip()
    except KeyError:
        df["airline"] = "Unknown"

    # Flight status
    status_col = first_existing_column(df, ["flight_status", "status"])
    df["flight_status_clean"] = df[status_col].fillna("").astype(str).str.lower().str.strip()
    df["is_cancelled"] = df["flight_status_clean"].eq("cancelled")

    # Date field
    date_col = None
    for candidate in ["full_date", "flight_date", "scheduled_departure", "dep_scheduled"]:
        if candidate in df.columns:
            date_col = candidate
            break
    if date_col is None:
        raise KeyError("No usable date column found.")

    df["flight_date_clean"] = pd.to_datetime(df[date_col], errors="coerce")
    df = df[df["flight_date_clean"].notna()]
    df["month"] = df["flight_date_clean"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["flight_date_clean"].dt.day_name()
    df["season"] = df["flight_date_clean"].dt.month.map(month_to_season)

    # Departure delay
    delay_col = None
    for candidate in ["departure_delay_min", "dep_delay", "departure_delay"]:
        if candidate in df.columns:
            delay_col = candidate
            break
    if delay_col:
        df["departure_delay_min_clean"] = pd.to_numeric(df[delay_col], errors="coerce")
    else:
        df["departure_delay_min_clean"] = pd.NA

    return df


def month_to_season(month: int) -> str:
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    return "Fall"


def add_value_labels(ax, values, fmt="{:,}", padding=3):
    """Put labels above bars."""
    for bar, value in zip(ax.patches, values):
        ax.annotate(
            fmt.format(value),
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            xytext=(0, padding),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
        )


def save_chart(fig, output_dir: Path, filename: str):
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_dir / filename, dpi=200, bbox_inches="tight")
    plt.close(fig)


def chart_departures_by_airport(df: pd.DataFrame, output_dir: Path):
    counts = df["departure_airport"].value_counts().reindex(TARGET_AIRPORTS, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    counts.plot(kind="bar", ax=ax)
    ax.set_title("Total Departures by Airport")
    ax.set_xlabel("Airport")
    ax.set_ylabel("Flights")
    add_value_labels(ax, counts.values)
    save_chart(fig, output_dir, "01_departures_by_airport.png")


def chart_cancellation_rate_by_airport(df: pd.DataFrame, output_dir: Path):
    rates = df.groupby("departure_airport")["is_cancelled"].mean().reindex(TARGET_AIRPORTS) * 100
    fig, ax = plt.subplots(figsize=(8, 5))
    rates.plot(kind="bar", ax=ax)
    ax.set_title("Flight Cancellation Rate by Airport")
    ax.set_xlabel("Airport")
    ax.set_ylabel("Cancellation rate (%)")
    add_value_labels(ax, rates.round(2).values, fmt="{:.2f}%")
    save_chart(fig, output_dir, "02_cancellation_rate_by_airport.png")


def chart_top_airlines(df: pd.DataFrame, output_dir: Path):
    top = df["airline"].value_counts().head(10).sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    top.plot(kind="barh", ax=ax)
    ax.set_title("Top 10 Airlines by Departure Volume")
    ax.set_xlabel("Flights")
    ax.set_ylabel("Airline")
    for bar, value in zip(ax.patches, top.values):
        ax.annotate(f"{value:,}", (bar.get_width(), bar.get_y() + bar.get_height() / 2), va="center", xytext=(4, 0), textcoords="offset points", fontsize=9)
    save_chart(fig, output_dir, "03_top_airlines_by_departures.png")


def chart_departures_by_month(df: pd.DataFrame, output_dir: Path):
    monthly = df.groupby("month").size().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    monthly.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Total Departures by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Flights")
    ax.tick_params(axis="x", rotation=45)
    save_chart(fig, output_dir, "04_departures_by_month.png")


def chart_highest_airline_cancellation_rates(df: pd.DataFrame, output_dir: Path, min_flights: int = 2000):
    grouped = df.groupby("airline").agg(total_flights=("airline", "size"), cancellation_rate=("is_cancelled", "mean"))
    grouped = grouped[grouped["total_flights"] >= min_flights]
    top_rates = (grouped["cancellation_rate"] * 100).sort_values(ascending=False).head(10).sort_values()

    fig, ax = plt.subplots(figsize=(9, 6))
    top_rates.plot(kind="barh", ax=ax)
    ax.set_title(f"Highest Cancellation Rates by Airline (≥ {min_flights:,} flights)")
    ax.set_xlabel("Cancellation rate (%)")
    ax.set_ylabel("Airline")
    for bar, value in zip(ax.patches, top_rates.values):
        ax.annotate(f"{value:.2f}%", (bar.get_width(), bar.get_y() + bar.get_height() / 2), va="center", xytext=(4, 0), textcoords="offset points", fontsize=9)
    save_chart(fig, output_dir, "05_highest_airline_cancellation_rates.png")


def chart_departures_by_season(df: pd.DataFrame, output_dir: Path):
    seasonal = df["season"].value_counts().reindex(SEASON_ORDER, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    seasonal.plot(kind="bar", ax=ax)
    ax.set_title("Departures by Season")
    ax.set_xlabel("Season")
    ax.set_ylabel("Flights")
    add_value_labels(ax, seasonal.values)
    save_chart(fig, output_dir, "06_departures_by_season.png")


def chart_departures_by_day_of_week(df: pd.DataFrame, output_dir: Path):
    day_counts = df["day_of_week"].value_counts().reindex(DAY_ORDER, fill_value=0)
    fig, ax = plt.subplots(figsize=(9, 5))
    day_counts.plot(kind="bar", ax=ax)
    ax.set_title("Departures by Day of Week")
    ax.set_xlabel("Day")
    ax.set_ylabel("Flights")
    ax.set_xticklabels(DAY_LABELS, rotation=0)
    add_value_labels(ax, day_counts.values)
    save_chart(fig, output_dir, "07_departures_by_day_of_week.png")


def chart_average_delay_by_airport(df: pd.DataFrame, output_dir: Path):
    delay = df.groupby("departure_airport")["departure_delay_min_clean"].mean().reindex(TARGET_AIRPORTS)
    fig, ax = plt.subplots(figsize=(8, 5))
    delay.plot(kind="bar", ax=ax)
    ax.set_title("Average Departure Delay by Airport")
    ax.set_xlabel("Airport")
    ax.set_ylabel("Minutes")
    add_value_labels(ax, delay.round(1).values, fmt="{:.1f} min")
    save_chart(fig, output_dir, "08_average_departure_delay_by_airport.png")


def create_kpi_summary(df: pd.DataFrame, output_dir: Path):
    kpis = {
        "total_departures": len(df),
        "total_cancellations": int(df["is_cancelled"].sum()),
        "overall_cancellation_rate_pct": round(df["is_cancelled"].mean() * 100, 2),
        "avg_departure_delay_min": round(float(df["departure_delay_min_clean"].mean()), 2),
    }
    pd.DataFrame([kpis]).to_csv(output_dir / "kpi_summary.csv", index=False)


def main():
    parser = argparse.ArgumentParser(description="Create airport traffic visualizations for CIS 4400 Project 8.")
    parser.add_argument("--input", required=True, help="Path to AviationDW_Gold.xlsx or flights_cleaned.csv")
    parser.add_argument("--output", default="visualizations", help="Folder where charts will be saved")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)

    df = load_data(input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    chart_departures_by_airport(df, output_dir)
    chart_cancellation_rate_by_airport(df, output_dir)
    chart_top_airlines(df, output_dir)
    chart_departures_by_month(df, output_dir)
    chart_highest_airline_cancellation_rates(df, output_dir)
    chart_departures_by_season(df, output_dir)
    chart_departures_by_day_of_week(df, output_dir)
    chart_average_delay_by_airport(df, output_dir)
    create_kpi_summary(df, output_dir)

    print(f"Done. Charts saved in: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
