Public GCS bucket → Azure Blob Storage (Google Colab)
Copies objects from a public Google Cloud Storage bucket (no GCP credentials) straight into an Azure Blob container — streaming, nothing is written to the Colab disk.

You specify the bucket, the path, the storage account, and the container in Cell 2.

How to use

Run Cell 1 to install the Azure SDK.
Put your Azure secret in the Colab secret manager (🔑 in the left sidebar) — name it AZURE_STORAGE_KEY (account key) or AZURE_STORAGE_CONNECTION_STRING, and toggle Notebook access on. If neither is set you'll be prompted securely in Cell 3.
Fill in Cell 2 (bucket / path / account / container).
Run Cell 4 as a --dry-run first to check the file list, then Cell 5 to copy.

# Cell 1 — install dependencies (requests ships with Colab)
!pip install -q azure-storage-blob
     

# Cell 2 — configuration  (edit these)
GCS_BUCKET  = "msba-online-data"   #@param {type:"string"}
GCS_PATH    = "CIS4400/project08/flightdata"            #@param {type:"string"}  object-name prefix to copy
ACCOUNT     = "stairtrafficdev"  #@param {type:"string"}  Azure storage account name
CONTAINER   = "my-container"   #@param {type:"string"}
DEST_PREFIX = ""            #@param {type:"string"}  prefix for blob names
WORKERS     = 6            #@param {type:"integer"}
OVERWRITE   = False        #@param {type:"boolean"}
LIMIT       = 0            #@param {type:"integer"}  0 = all objects
     

# Cell 3 — Azure credential (Colab secret first, else secure prompt). GCS needs no auth.
import os

AZ_CONN = AZ_KEY = None
try:
    from google.colab import userdata
    try: AZ_CONN = userdata.get('AZURE_STORAGE_CONNECTION_STRING')
    except Exception: pass
    try: AZ_KEY = userdata.get('AZURE_STORAGE_KEY')
    except Exception: pass
except Exception:
    pass

AZ_CONN = AZ_CONN or os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZ_KEY  = AZ_KEY  or os.environ.get('AZURE_STORAGE_KEY')

if not AZ_CONN and not AZ_KEY:
    import getpass
    AZ_KEY = getpass.getpass(f'Paste the account KEY for storage account "{ACCOUNT}": ')

assert AZ_CONN or AZ_KEY, 'No Azure credential provided.'
print('Azure credential loaded.')
     

# Cell 4 — the transfer logic (streams GCS URL -> Azure blob, no local file)
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
from azure.storage.blob import BlobServiceClient

GCS_API = "https://storage.googleapis.com/storage/v1/b"   # JSON list API
GCS_DL  = "https://storage.googleapis.com"                # XML download endpoint

def list_gcs_objects(bucket, prefix, session):
    """Yield (name, size_bytes) for every object under prefix in a PUBLIC bucket."""
    page_token = None
    while True:
        params = {"prefix": prefix, "maxResults": 1000}
        if page_token: params["pageToken"] = page_token
        r = session.get(f"{GCS_API}/{quote(bucket, safe='')}/o", params=params, timeout=60)
        if r.status_code in (401, 403):
            raise PermissionError(f"Bucket '{bucket}' does not allow anonymous listing (HTTP {r.status_code}).")
        r.raise_for_status()
        data = r.json()
        for item in data.get("items", []):
            name = item["name"]
            if name.endswith("/"): continue   # directory placeholder
            yield name, int(item.get("size", 0))
        page_token = data.get("nextPageToken")
        if not page_token: break

def make_blob_name(name, gcs_path, dest_prefix):
    rel = name[len(gcs_path):].lstrip("/") if name.startswith(gcs_path) else name
    return (dest_prefix.rstrip("/") + "/" + rel) if dest_prefix else rel

def transfer(name, size, bucket, gcs_path, dest_prefix, container_client, session, overwrite):
    blob_name = make_blob_name(name, gcs_path, dest_prefix)
    blob_client = container_client.get_blob_client(blob_name)
    url = f"{GCS_DL}/{quote(bucket, safe='')}/{quote(name, safe='/')}"
    try:
        if not overwrite and blob_client.exists():
            return "skip-exists", blob_name
        with session.get(url, stream=True, timeout=600) as resp:
            if resp.status_code == 404:
                return "missing", blob_name
            resp.raise_for_status()
            resp.raw.decode_content = True
            length = resp.headers.get("Content-Length")
            blob_client.upload_blob(resp.raw, overwrite=True,
                                    length=int(length) if length else (size or None),
                                    max_concurrency=1)
        mb = (int(length) if length else size) / (1 << 20)
        return f"ok ({mb:.1f} MB)", blob_name
    except Exception as exc:
        return f"error: {exc}", blob_name

def build_container_client(account, container, az_conn, az_key):
    if az_conn:
        service = BlobServiceClient.from_connection_string(az_conn)
    else:
        service = BlobServiceClient(account_url=f"https://{account}.blob.core.windows.net",
                                    credential=az_key)
    cc = service.get_container_client(container)
    try:
        cc.create_container(); print(f"Created container '{container}'.")
    except Exception:
        pass
    return cc

# List the bucket and preview (acts as a dry-run).
session = requests.Session()
session.headers.update({"User-Agent": "gcs-to-azure/colab"})
print(f"Listing gs://{GCS_BUCKET}/{GCS_PATH} ...")
OBJECTS = list(list_gcs_objects(GCS_BUCKET, GCS_PATH, session))
if LIMIT: OBJECTS = OBJECTS[:LIMIT]
total_mb = sum(s for _, s in OBJECTS) / (1 << 20)
print(f"Found {len(OBJECTS)} objects, {total_mb:.1f} MB total.\n")
for name, sz in OBJECTS[:20]:
    print(f"  {name}  ->  {make_blob_name(name, GCS_PATH, DEST_PREFIX)}  ({sz/(1<<20):.1f} MB)")
if len(OBJECTS) > 20:
    print(f"  ... and {len(OBJECTS) - 20} more")
print("\nReview the list above, then run Cell 5 to copy.")
     

# Cell 5 — run the copy (GCS -> Azure)
container_client = build_container_client(ACCOUNT, CONTAINER, AZ_CONN, AZ_KEY)
print(f"Streaming -> azure://{ACCOUNT}/{CONTAINER}/{DEST_PREFIX}\n")

counts = {"ok": 0, "skip-exists": 0, "missing": 0, "error": 0}
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = [pool.submit(transfer, name, sz, GCS_BUCKET, GCS_PATH, DEST_PREFIX,
                           container_client, session, OVERWRITE)
               for name, sz in OBJECTS]
    for fut in as_completed(futures):
        status, blob_name = fut.result()
        key = ("ok" if status.startswith("ok")
               else "error" if status.startswith("error") else status)
        counts[key] = counts.get(key, 0) + 1
        print(f"  [{status:>16}] {blob_name}")

print("\nDone.")
print(f"  copied         : {counts['ok']}")
print(f"  already present: {counts['skip-exists']}")
print(f"  missing (404)  : {counts['missing']}")
print(f"  errors         : {counts['error']}")
     

# Cell 6 (optional) — verify what landed in the container
cc = build_container_client(ACCOUNT, CONTAINER, AZ_CONN, AZ_KEY)
blobs = list(cc.list_blobs(name_starts_with=DEST_PREFIX))
total_mb = sum(b.size for b in blobs) / (1 << 20)
print(f"{len(blobs)} blobs under '{DEST_PREFIX}', {total_mb:.1f} MB total\n")
for b in blobs[:50]:
    print(f"  {b.name}  ({b.size/(1<<20):.1f} MB)")
