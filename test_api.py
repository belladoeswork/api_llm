from dotenv import load_dotenv
import os
import requests

load_dotenv()

url = "http://localhost:8000/generate?prompt= Tell me about Fastapi"

headers = {"x-key": os.getenv("API_KEY"), "content-type": "application/json"}

response = requests.post(url, headers=headers)

print(response.json())