import requests
import time
import os

API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

url = "https://api.semanticscholar.org/graph/v1/paper/ARXIV:2101.00001"

headers = {
    "x-api-key": API_KEY
}

time.sleep(2)  # Add a delay of 1 second between requests to avoid rate limiting

response = requests.get(url, headers=headers)

time.sleep(2)  # Add a delay of 1 second between requests to avoid rate limiting

print("Status:", response.status_code)

time.sleep(2)  # Add a delay of 1 second between requests to avoid rate limiting

print("Response:", response.text)