from pathlib import Path
import pandas as pd

# --------------------------------------------------
# File paths
# --------------------------------------------------

INPUT_FILE = "flights_cleaned.csv"
OUTPUT_DIR = Path("gold_layer")

OUTPUT_DIR.mkdir(exist_ok=True)

print("Reading Silver dataset...")

df = pd.read_csv(INPUT_FILE, low_memory=False)

print(f"Rows loaded: {len(df):,}")


# --------------------------------------------------
# Clean date and time fields
# --------------------------------------------------

df["flight_date"] = pd.to_datetime(
    df["flight_date"],
    errors="coerce"
)

datetime_columns = [
    "dep_scheduled",
    "dep_actual",
    "arr_scheduled",
    "arr_actual"
]

for column in datetime_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce",
        utc=True
    )


# --------------------------------------------------
# DIMENSION 1: DATE
# --------------------------------------------------

print("Creating dim_date...")

dim_date = (
    df[["flight_date"]]
    .dropna()
    .drop_duplicates()
    .sort_values("flight_date")
    .reset_index(drop=True)
)

dim_date["date_id"] = range(1, len(dim_date) + 1)

dim_date["year"] = dim_date["flight_date"].dt.year
dim_date["month"] = dim_date["flight_date"].dt.month
dim_date["month_name"] = dim_date["flight_date"].dt.month_name()
dim_date["day"] = dim_date["flight_date"].dt.day
dim_date["day_of_week"] = dim_date["flight_date"].dt.day_name()
dim_date["is_weekend"] = (
    dim_date["day_of_week"]
    .isin(["Saturday", "Sunday"])
)

dim_date = dim_date[
    [
        "date_id",
        "flight_date",
        "year",
        "month",
        "month_name",
        "day",
        "day_of_week",
        "is_weekend"
    ]
]

dim_date.to_csv(
    OUTPUT_DIR / "dim_date.csv",
    index=False
)


# --------------------------------------------------
# DIMENSION 2: AIRPORT
# --------------------------------------------------

print("Creating dim_airport...")

departure_airports = df[
    [
        "dep_airport",
        "dep_iata",
        "dep_icao"
    ]
].copy()

departure_airports.columns = [
    "airport_name",
    "iata_code",
    "icao_code"
]

arrival_airports = df[
    [
        "arr_airport",
        "arr_iata",
        "arr_icao"
    ]
].copy()

arrival_airports.columns = [
    "airport_name",
    "iata_code",
    "icao_code"
]

dim_airport = pd.concat(
    [departure_airports, arrival_airports],
    ignore_index=True
)

dim_airport = (
    dim_airport
    .drop_duplicates()
    .dropna(subset=["iata_code"])
    .reset_index(drop=True)
)

dim_airport["airport_id"] = range(
    1,
    len(dim_airport) + 1
)

dim_airport = dim_airport[
    [
        "airport_id",
        "airport_name",
        "iata_code",
        "icao_code"
    ]
]

dim_airport.to_csv(
    OUTPUT_DIR / "dim_airport.csv",
    index=False
)


# --------------------------------------------------
# DIMENSION 3: AIRLINE
# --------------------------------------------------

print("Creating dim_airline...")

dim_airline = (
    df[
        [
            "airline_name",
            "airline_iata",
            "airline_icao"
        ]
    ]
    .drop_duplicates()
    .dropna(subset=["airline_name"])
    .reset_index(drop=True)
)

dim_airline["airline_id"] = range(
    1,
    len(dim_airline) + 1
)

dim_airline = dim_airline[
    [
        "airline_id",
        "airline_name",
        "airline_iata",
        "airline_icao"
    ]
]

dim_airline.to_csv(
    OUTPUT_DIR / "dim_airline.csv",
    index=False
)


# --------------------------------------------------
# DIMENSION 4: AIRCRAFT
# --------------------------------------------------

print("Creating dim_aircraft...")

dim_aircraft = (
    df[
        [
            "aircraft_registration",
            "aircraft_iata"
        ]
    ]
    .drop_duplicates()
    .dropna(subset=["aircraft_registration"])
    .reset_index(drop=True)
)

dim_aircraft["aircraft_id"] = range(
    1,
    len(dim_aircraft) + 1
)

dim_aircraft = dim_aircraft[
    [
        "aircraft_id",
        "aircraft_registration",
        "aircraft_iata"
    ]
]

dim_aircraft.to_csv(
    OUTPUT_DIR / "dim_aircraft.csv",
    index=False
)


# --------------------------------------------------
# FACT TABLE
# --------------------------------------------------

print("Creating fact_flights...")

fact_flights = df[
    [
        "flight_date",
        "flight_status",
        "airline_name",
        "aircraft_registration",
        "dep_iata",
        "arr_iata",
        "flight_number",
        "dep_delay",
        "arr_delay",
        "dep_scheduled",
        "dep_actual",
        "arr_scheduled",
        "arr_actual"
    ]
].copy()


# Add date ID
fact_flights = fact_flights.merge(
    dim_date[["date_id", "flight_date"]],
    on="flight_date",
    how="left"
)


# Add airline ID
fact_flights = fact_flights.merge(
    dim_airline[
        [
            "airline_id",
            "airline_name"
        ]
    ],
    on="airline_name",
    how="left"
)


# Add aircraft ID
fact_flights = fact_flights.merge(
    dim_aircraft[
        [
            "aircraft_id",
            "aircraft_registration"
        ]
    ],
    on="aircraft_registration",
    how="left"
)


# Departure airport mapping
departure_mapping = dim_airport[
    [
        "airport_id",
        "iata_code"
    ]
].rename(
    columns={
        "airport_id": "departure_airport_id",
        "iata_code": "dep_iata"
    }
)

fact_flights = fact_flights.merge(
    departure_mapping,
    on="dep_iata",
    how="left"
)


# Arrival airport mapping
arrival_mapping = dim_airport[
    [
        "airport_id",
        "iata_code"
    ]
].rename(
    columns={
        "airport_id": "arrival_airport_id",
        "iata_code": "arr_iata"
    }
)

fact_flights = fact_flights.merge(
    arrival_mapping,
    on="arr_iata",
    how="left"
)


# Create flight ID
fact_flights.insert(
    0,
    "flight_id",
    range(1, len(fact_flights) + 1)
)


# Keep warehouse fields
fact_flights = fact_flights[
    [
        "flight_id",
        "date_id",
        "airline_id",
        "aircraft_id",
        "departure_airport_id",
        "arrival_airport_id",
        "flight_number",
        "flight_status",
        "dep_delay",
        "arr_delay",
        "dep_scheduled",
        "dep_actual",
        "arr_scheduled",
        "arr_actual"
    ]
]

fact_flights.to_csv(
    OUTPUT_DIR / "fact_flights.csv",
    index=False
)


# --------------------------------------------------
# DATA MART 1: KPI BY AIRPORT
# --------------------------------------------------

print("Creating KPI by airport data mart...")

airport_data = df[
    df["dep_iata"].isin(
        ["JFK", "LGA", "ISP"]
    )
].copy()

airport_kpi = (
    airport_data
    .groupby("dep_iata")
    .agg(
        total_departures=("flight_number", "size"),
        average_departure_delay=("dep_delay", "mean"),
        cancelled_flights=(
            "flight_status",
            lambda x: (
                x.astype(str).str.lower() == "cancelled"
            ).sum()
        )
    )
    .reset_index()
)

airport_kpi["cancellation_rate"] = (
    airport_kpi["cancelled_flights"]
    / airport_kpi["total_departures"]
    * 100
)

airport_kpi.to_csv(
    OUTPUT_DIR / "kpi_by_airport.csv",
    index=False
)


# --------------------------------------------------
# DATA MART 2: KPI BY AIRLINE
# --------------------------------------------------

print("Creating KPI by airline data mart...")

airline_kpi = (
    airport_data
    .groupby("airline_name")
    .agg(
        total_departures=("flight_number", "size"),
        average_departure_delay=("dep_delay", "mean"),
        cancelled_flights=(
            "flight_status",
            lambda x: (
                x.astype(str).str.lower() == "cancelled"
            ).sum()
        )
    )
    .reset_index()
)

airline_kpi["cancellation_rate"] = (
    airline_kpi["cancelled_flights"]
    / airline_kpi["total_departures"]
    * 100
)

airline_kpi.to_csv(
    OUTPUT_DIR / "kpi_by_airline.csv",
    index=False
)


# --------------------------------------------------
# DATA MART 3: FLIGHTS BY MONTH
# --------------------------------------------------

print("Creating monthly data mart...")

airport_data["year_month"] = (
    airport_data["flight_date"]
    .dt.to_period("M")
    .astype(str)
)

flights_by_month = (
    airport_data
    .groupby("year_month")
    .size()
    .reset_index(name="total_departures")
)

flights_by_month.to_csv(
    OUTPUT_DIR / "flights_by_month.csv",
    index=False
)


# --------------------------------------------------
# DATA MART 4: SEASON AND DAY OF WEEK
# --------------------------------------------------

print("Creating season and day data mart...")

airport_data["month"] = airport_data["flight_date"].dt.month
airport_data["day_of_week"] = airport_data["flight_date"].dt.day_name()


def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"


airport_data["season"] = (
    airport_data["month"]
    .apply(get_season)
)

flights_by_season_day = (
    airport_data
    .groupby(
        [
            "season",
            "day_of_week"
        ]
    )
    .size()
    .reset_index(name="total_departures")
)

flights_by_season_day.to_csv(
    OUTPUT_DIR / "flights_by_season_day.csv",
    index=False
)


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print()
print("Gold layer created successfully!")
print(f"Files saved in: {OUTPUT_DIR.resolve()}")
