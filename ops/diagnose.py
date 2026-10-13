import json
from urllib.request import urlopen

with urlopen('http://127.0.0.1:8090/health',timeout=5) as response:
    print(json.load(response))
