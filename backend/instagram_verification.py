import requests

def verify_instagram_username(username):
    url = f"https://www.instagram.com/{username}/"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        raise Exception(f"Verification error: {str(e)}")
