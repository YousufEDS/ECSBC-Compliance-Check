import requests

url = "https://api.vectorshift.ai/v1/pipeline/6954c79ba76af4b71858e962/run"

payload = { "inputs": { "Input": "Hi" } }
headers = {
    "Authorization": "Bearer sk_UUzE2PgugFATCpHwS8mAenzgMowmV6RpSg02UhTMhTYY7w8z",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print("\n" + response.text)