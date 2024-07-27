import requests
import json

url = 'http://localhost:28888/contest/to_start'
headers = {"Content-type": "application/json"}
data = {}
response = requests.post(url,
                        data=json.dumps(data),
                        headers=headers)
status = json.load(response.text)
print(status)
