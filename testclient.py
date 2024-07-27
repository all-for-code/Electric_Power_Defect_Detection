import requests
import json, time

data = {"state":json.dumps({"contestantId":"2", "checkoutNum":78,"faultNum":7})}
url = 'http://10.85.158.117:18317/pcr/contest/submit_state'
response = requests.post(url,
                        data=data)

status = json.loads(response.text)
print(status)