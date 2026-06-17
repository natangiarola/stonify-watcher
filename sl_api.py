import requests

def check_sl(project_id, b_token):
    url = f"https://speedlabel-v3-web-api.fifthgeartech.com/api/private/jobs/{project_id}/summary"
    headers = {"Authorization": f"Bearer {b_token}"}

    response = requests.get(url, headers=headers)
    data = response.json()

    if "buckets" in data:
        if data["buckets"] == []:
            return False
        else:
            return True
    else:
        return None

