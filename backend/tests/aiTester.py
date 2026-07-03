import os
import requests
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
ACCOUNT_ID = "7de9757d21d3ddddb48d3a17a7fd7f7b"
AUTH_TOKEN = os.environ.get("CLOUDFLARE_AUTH_TOKEN")

# Step 1: Accept model license agreement
agree_response = requests.post(
  f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3.2-11b-vision-instruct",
    headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
    json={"prompt": "agree"}
)
print("Agreement response:", agree_response.json())

# Step 2: Now send the actual prompt
prompt = "Tell me all about PEP-8"
response = requests.post(
  f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3.2-11b-vision-instruct",
    headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
    json={
      "messages": [
        {"role": "system", "content": "You are a friendly assistant"},
        {"role": "user", "content": prompt}
      ]
    }
)
result = response.json()
print("Result:", result)