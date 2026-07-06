!pip install -q azure-storage-blob

import io
import pandas as pd
from azure.storage.blob import BlobServiceClient
from google.colab import userdata

# ==== CONFIG ====
AZURE_CONN_STRING = userdata.get('AZURE_CONN_STRING')  # Fetch from Colab Secrets

SOURCE_CONTAINER = "cleandata"          # container with your cleaned data
SOURCE_BLOB_NAME = "flights_cleaned.csv"
DEST_CONTAINER = "curateddata"
# ================

blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STRING)

# --- Pull cleaned CSV directly from the container ---
source_container_client = blob_service.get_container_client(SOURCE_CONTAINER)
blob_client = source_container_client.get_blob_client(SOURCE_BLOB_NAME)
csv_data = blob_client.download_blob().readall()
df = pd.read_csv(
    io.BytesIO(csv_data),
    parse_dates=["flight_date", "dep_scheduled", "dep_actual", "arr_scheduled", "arr_actual"],
    low_memory=False
)
print(f"Loaded {len(df)} rows from {SOURCE_CONTAINER}/{SOURCE_BLOB_NAME}")

# --- dim_date ---
dim_date = df[["flight_date"]].drop_duplicates().reset_index(drop=True)
dim_date["date_id"] = dim_date.index + 1
dim_date["full_date"] = dim_date["flight_date"]
dim_date["year"] = dim_date["full_date"].dt.year
dim_date["month"] = dim_date["full_date"].dt.month
dim_date["month_name"] = dim_date["full_date"].dt.month_name()
dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek
dim_date["day"] = dim_date["full_date"].dt.day
dim_date["is_weekend"] = dim_date["day_of_week"].isin([5, 6]).astype(int)
dim_date = dim_date[["date_id", "full_date", "year", "month", "month_name", "day_of_week", "day", "is_weekend"]]
print(f"Built dim_date: {len(dim_date)} rows")

# --- dim_airline ---
dim_airline = df[["airline_name", "airline_iata", "airline_icao"]].drop_duplicates(
    subset=["airline_iata", "airline_icao"], keep="first"
).reset_index(drop=True)
dim_airline["airline_id"] = dim_airline.index + 1
dim_airline = dim_airline.rename(columns={"airline_iata": "iata", "airline_icao": "icao"})
dim_airline = dim_airline[["airline_id", "airline_name", "iata", "icao"]]
print(f"Built dim_airline: {len(dim_airline)} rows")

# --- dim_aircraft ---
dim_aircraft = df[["aircraft_registration", "aircraft_iata"]].drop_duplicates(
    subset=["aircraft_registration", "aircraft_iata"], keep="first"
).reset_index(drop=True)
dim_aircraft["aircraft_id"] = dim_aircraft.index + 1
dim_aircraft["icao_type"] = None
dim_aircraft["icao24"] = None
dim_aircraft = dim_aircraft.rename(columns={"aircraft_registration": "regristration", "aircraft_iata": "iata_type"})
dim_aircraft = dim_aircraft[["aircraft_id", "regristration", "iata_type", "icao_type", "icao24"]]
print(f"Built dim_aircraft: {len(dim_aircraft)} rows")

# --- dim_airport (union of departure + arrival airports) ---
dep_airports = df[["dep_airport", "dep_iata", "dep_icao"]].rename(
    columns={"dep_airport": "airport_name", "dep_iata": "iata", "dep_icao": "icao"})
arr_airports = df[["arr_airport", "arr_iata", "arr_icao"]].rename(
    columns={"arr_airport": "airport_name", "arr_iata": "iata", "arr_icao": "icao"})

dim_airport = pd.concat([dep_airports, arr_airports])
# Dedupe on iata/icao only -- these are the keys we join fact_flights on,
# so dim_airport must have exactly one row per iata/icao pair (avoids fan-out).
dim_airport = dim_airport.drop_duplicates(subset=["iata", "icao"], keep="first").reset_index(drop=True)
dim_airport["airport_id"] = dim_airport.index + 1
dim_airport["city"] = None
dim_airport["timezone_airport"] = None
dim_airport["country"] = None
dim_airport = dim_airport[["airport_id", "iata", "icao", "airport_name", "city", "timezone_airport", "country"]]
print(f"Built dim_airport: {len(dim_airport)} rows")

# --- fact_flights (join back to dims for surrogate keys) ---
fact = df.copy()
fact["flight_id"] = fact.index + 1

fact = fact.merge(dim_date[["date_id", "full_date"]], left_on="flight_date", right_on="full_date", how="left")
fact = fact.merge(dim_airline[["airline_id", "iata", "icao"]],
                   left_on=["airline_iata", "airline_icao"],
                   right_on=["iata", "icao"], how="left", suffixes=("", "_airline"))
fact = fact.merge(dim_aircraft[["aircraft_id", "regristration", "iata_type"]],
                   left_on=["aircraft_registration", "aircraft_iata"],
                   right_on=["regristration", "iata_type"], how="left")
fact = fact.merge(dim_airport[["airport_id", "iata", "icao"]],
                   left_on=["dep_iata", "dep_icao"], right_on=["iata", "icao"], how="left") \
           .rename(columns={"airport_id": "departure_airport_id"})
fact = fact.merge(dim_airport[["airport_id", "iata", "icao"]],
                   left_on=["arr_iata", "arr_icao"], right_on=["iata", "icao"], how="left",
                   suffixes=("", "_arr")) \
           .rename(columns={"airport_id": "arrival_airport_id"})

fact_flights = fact.rename(columns={
    "dep_delay": "departure_delay_min",
    "arr_delay": "arrival_delay_min",
    "dep_scheduled": "scheduled_departure",
    "dep_actual": "actual_departure",
    "arr_scheduled": "scheduled_arrival",
    "arr_actual": "actual_arrival",
    "dep_terminal": "departure_terminal",
    "dep_gate": "departure_gate",
    "arr_terminal": "arrival_terminal",
    "arr_gate": "arrival_gate",
    "arr_baggage": "baggage_claim",
})[["flight_id", "date_id", "airline_id", "aircraft_id", "departure_airport_id", "arrival_airport_id",
    "flight_number", "flight_status", "departure_delay_min", "arrival_delay_min",
    "scheduled_departure", "actual_departure", "scheduled_arrival", "actual_arrival",
    "departure_terminal", "departure_gate", "arrival_terminal", "arrival_gate", "baggage_claim"]]

print(f"Built fact_flights: {len(fact_flights)} rows (source had {len(df)} rows)")
if len(fact_flights) != len(df):
    print("WARNING: row count mismatch -- check for duplicate/unmatched keys in the dims above.")

# --- Upload all 5 tables to the curated container ---
dest_container_client = blob_service.get_container_client(DEST_CONTAINER)
try:
    dest_container_client.create_container()
except Exception:
    pass  # already exists

tables = {
    "dim_date.csv": dim_date,
    "dim_airline.csv": dim_airline,
    "dim_aircraft.csv": dim_aircraft,
    "dim_airport.csv": dim_airport,
    "fact_flights.csv": fact_flights,
}

for filename, table_df in tables.items():
    buffer = io.StringIO()
    table_df.to_csv(buffer, index=False)
    dest_container_client.upload_blob(name=filename, data=buffer.getvalue(), overwrite=True)
    print(f"Uploaded {filename} ({len(table_df)} rows)")
