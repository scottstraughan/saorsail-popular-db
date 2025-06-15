import requests

url = "https://f-droid.org/repo/index-v2.json"
target_file = "repository.json"

# Download the JSON file
response = requests.get(url)
response.raise_for_status()  # Raise an error for bad status codes

# Save the content to a file
with open(target_file, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"Downloaded and saved JSON to {target_file}")
