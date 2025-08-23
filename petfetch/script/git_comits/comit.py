import requests
from datetime import datetime, timedelta

#put your user name here
USERNAME = "KishaWeb"
DAYS_BACK = 1

headers = {
    "Accept": "application/vnd.github.v3+json"
}

since_date = (datetime.now() - timedelta(days=DAYS_BACK)).isoformat()

url = f"https://api.github.com/users/{USERNAME}/events"
params = {"per_page": 100}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    events = response.json()

    # Filter for push events (commits)
    commits = []
    for event in events:
        if event["type"] == "PushEvent":
            for commit in event["payload"]["commits"]:
                commits.append({
                    "repo": event["repo"]["name"],
                    "message": commit.get("message", "No message"),
                    "sha": commit.get("sha", "N/A"),
                    "url": commit.get("url", "N/A"),
                    "date": event.get("created_at", "N/A")
                })

    commits.sort(key=lambda x: x["date"], reverse=True)

    print(f"Latest commits by {USERNAME}:")
    for i, commit in enumerate(commits[:10], 1):
        print(f"{i}. {commit['repo']}: {commit['message']} ({commit['date']})")
        print(f"   SHA: {commit['sha']}")
        print(f"   URL: {commit['url']}\n")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
