import requests
from datetime import datetime, timedelta

def get_comits():
    USERNAME = "your user name"
    DAYS_BACK = 7

    headers = {
        "Authorization": f"token your_token",  # replace with your token
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/users/{USERNAME}/events"
    params = {"per_page": 100}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        events = response.json()

        pushes = []   # list of push events
        commits = []  # list of all commits

        for event in events:
            if event["type"] == "PushEvent":
                pushes.append(event)  # count per push

                for commit in event["payload"]["commits"]:
                    commits.append({
                        "repo": event["repo"]["name"],
                        "message": commit.get("message", "No message"),
                        "sha": commit.get("sha", "N/A"),
                        "url": commit.get("url", "N/A"),
                        "date": event.get("created_at", "N/A")
                    })

        commits.sort(key=lambda x: x["date"], reverse=True)
        return pushes, commits  # return pushes and commits separately

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return [], []
#i tried my best for the comments
