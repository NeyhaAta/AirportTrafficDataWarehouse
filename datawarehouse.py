!pip install -q azure-storage-blob
from azure.storage.blob import BlobServiceClient
from google.colab import userdata

AZURE_CONN_STRING = userdata.get('AZURE_CONN_STRING')
SOURCE_CONTAINER = "curateddata"
DEST_CONTAINER = "datawarehouse"

blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STRING)
source = blob_service.get_container_client(SOURCE_CONTAINER)
dest = blob_service.get_container_client(DEST_CONTAINER)

try:
    dest.create_container()
    print(f"Created container '{DEST_CONTAINER}'")
except Exception:
    print(f"Container '{DEST_CONTAINER}' already exists")

blob_list = list(source.list_blobs())
print(f"Found {len(blob_list)} files in '{SOURCE_CONTAINER}'")

for blob in blob_list:
    dest.get_blob_client(blob.name).start_copy_from_url(source.get_blob_client(blob.name).url)
    print(f"Copied {blob.name}")

print("Done. All files copied to 'datawarehouse'.")
