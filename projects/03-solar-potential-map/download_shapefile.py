import requests
import zipfile
import os

# Kenya counties shapefile from GADM (free, reliable source)
url = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_KEN_shp.zip"

print("Downloading Kenya shapefile...")

response = requests.get(url, stream=True)
zip_path = "data/kenya_shapefile.zip"

with open(zip_path, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print("Extracting...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("data/kenya_shapefile")

print("✅ Done — shapefile saved to data/kenya_shapefile/")
os.remove(zip_path)