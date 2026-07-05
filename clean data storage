!pip install -q azure-storage-blob
import json
import io
import pandas as pd
from azure.storage.blob import BlobServiceClient
from google.colab import userdata

# ---- CONFIG ----
# Recommended: store this in Colab's "Secrets" (key icon in left sidebar)
# rather than pasting it directly in the notebook.
AZURE_CONN_STRING = userdata.get('AZURE_CONN_STRING') # Fetch from Colab Secrets

RAW_CONTAINER_NAME = "my-container"                # <-- change this to your raw container's name
STAGING_CONTAINER_NAME = "cleandata"        # <-- change this to your destination container's name
RAW_PREFIX = ""                            # <-- folder/prefix inside the raw container, if any
OUTPUT_LOCAL_PATH = "/content/flights_cleaned.csv"
OUTPUT_BLOB_NAME = "flights_cleaned.csv"

blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STRING)

# ---- 1. Pull every JSON file from the raw container ----
raw_container_client = blob_service.get_container_client(RAW_CONTAINER_NAME)
blob_list = list(raw_container_client.list_blobs(name_starts_with=RAW_PREFIX))

all_records = []
for blob_props in blob_list:
    if not blob_props.name.endswith(".json"):
        continue
    blob_client = raw_container_client.get_blob_client(blob_props.name)
    content = blob_client.download_blob().readall().decode("utf-8")
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print(f"Skipping malformed file: {blob_props.name}")
        continue
    if isinstance(data, list):
        all_records.extend(data)
    else:
        all_records.append(data)

print(f"Loaded {len(all_records)} raw records from {len(blob_list)} files")

# ---- 2. Flatten nested JSON into flat columns ----
def flatten_record(r):
    dep = r.get("departure") or {}
    arr = r.get("arrival") or {}
    airline = r.get("airline") or {}
    flight = r.get("flight") or {}
    aircraft = r.get("aircraft") or {}

    return {
        "flight_date": r.get("flight_date"),
        "flight_status": r.get("flight_status"),
        "airline_name": airline.get("name"),
        "airline_iata": airline.get("iata"),
        "airline_icao": airline.get("icao"),
        "flight_number": flight.get("number"),
        "flight_iata": flight.get("iata"),
        "flight_icao": flight.get("icao"),
        "aircraft_registration": aircraft.get("registration"),
        "aircraft_iata": aircraft.get("iata"),
        "dep_airport": dep.get("airport"),
        "dep_iata": dep.get("iata"),
        "dep_icao": dep.get("icao"),
        "dep_terminal": dep.get("terminal"),
        "dep_gate": dep.get("gate"),
        "dep_delay": dep.get("delay"),
        "dep_scheduled": dep.get("scheduled"),
        "dep_actual": dep.get("actual"),
        "arr_airport": arr.get("airport"),
        "arr_iata": arr.get("iata"),
        "arr_icao": arr.get("icao"),
        "arr_terminal": arr.get("terminal"),
        "arr_gate": arr.get("gate"),
        "arr_baggage": arr.get("baggage"),
        "arr_delay": arr.get("delay"),
        "arr_scheduled": arr.get("scheduled"),
        "arr_actual": arr.get("actual"),
    }

flat_records = [flatten_record(r) for r in all_records]
df = pd.DataFrame(flat_records)
print(f"Flattened into DataFrame: {df.shape}")

# ---- 3. Drop records missing required fields ----
required_fields = ["flight_date", "flight_iata", "dep_iata", "arr_iata"]
before = len(df)
df = df.dropna(subset=required_fields)
print(f"Dropped {before - len(df)} records missing required fields")

# ---- 4. Deduplicate on business key ----
# Same flight, same day, same scheduled departure = same flight event,
# even if delay/status fields differ slightly between polls.
business_key = ["flight_date", "flight_iata", "dep_scheduled"]
before = len(df)
df = df.sort_values("dep_actual", na_position="last")  # keep most complete/latest record
df = df.drop_duplicates(subset=business_key, keep="last")
print(f"Removed {before - len(df)} duplicate records")

# ---- 5. Normalize types ----
for col in ["dep_scheduled", "dep_actual", "arr_scheduled", "arr_actual"]:
    df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

for col in ["dep_delay", "arr_delay"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# ---- 6. Trim text fields ----
text_cols = df.select_dtypes(include="object").columns
for col in text_cols:
    df[col] = df[col].astype(str).str.strip().replace({"None": None, "nan": None})

# ---- 7. Final sanity check ----
print(f"Final cleaned dataset: {df.shape}")
print(df.head())

# ---- 8. Save locally, then upload to next stage ----
df.to_csv(OUTPUT_LOCAL_PATH, index=False)
print(f"Saved cleaned file to {OUTPUT_LOCAL_PATH}")

# ---- 9. Push cleaned file to the Azure staging container ----
staging_container_client = blob_service.get_container_client(STAGING_CONTAINER_NAME)

with open(OUTPUT_LOCAL_PATH, "rb") as f:
    staging_container_client.upload_blob(name=OUTPUT_BLOB_NAME, data=f, overwrite=True)

print(f"Uploaded {OUTPUT_BLOB_NAME} to Azure container '{STAGING_CONTAINER_NAME}'")
