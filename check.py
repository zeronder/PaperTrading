import requests

url = "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"

data = requests.get(url).json()

for item in data:
    if (
        item.get("exch_seg") == "MCX"
        and item.get("name") == "GOLD"
        and item.get("instrumenttype") == "FUTCOM"
    ):
        print(item)