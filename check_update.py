import requests

def get_latest_release():
    response = requests.get("https://api.github.com/repos/jyst06/WurtheringWave_Analyzer/releases")
    latest_release = response.json()
    print(latest_release)

if __name__ == '__main__':
    get_latest_release()