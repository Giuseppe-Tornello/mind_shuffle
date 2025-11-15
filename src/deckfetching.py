import requests

def get_raw_github(link:str) -> list | bool:
    response = requests.get(link)
    if response.status_code != 200:
        
        return False
    
    try:
        user = response.json()
        return user
    
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error fetching JSON: {e}")
        return False

