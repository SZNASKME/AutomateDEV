import requests
import base64

# Authentication
email = "suphawit.s@askme.co.th"
api_token = "ATATT3xFfGF0-MO1mnHuir7cobtaiAbqO-UBEv11hz3MpIUoL_LJX5WdyrkyvGTLkMorIoATOEbde"
auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()

# API endpoint
url = "https://askme-mtest.atlassian.net/rest/servicedeskapi/customer"

# Headers
headers = {
    "Authorization": f"Basic {auth}",
    "Content-Type": "application/json"
}

# Payload
payload = {
    "emailAddress": "martrkd@gmail.com",
    "displayName": "Mart"
}

# Send POST request
response = requests.post(url, headers=headers, json=payload)

# Check response
print(response.status_code, response.text)
