import requests
import os
from tqdm import tqdm


def download_exe(url):
    local_filename = url.split('/')[-1]

    with requests.get(url, stream=True) as r, open(local_filename, 'wb') as f:
        file_size = int(r.headers.get('content-length', 0))
        chunk_size = 8192
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=local_filename, ncols=100) as pbar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(len(chunk))

    if not os.path.exists("main.exe"):
        os.rename(local_filename, "main.exe")


if __name__ == '__main__':
    response = requests.get("https://api.github.com/repos/jyst06/WurtheringWave_Analyzer_exe/releases/latest")
    latest_release = response.json()
    download_exe(latest_release["assets"][0]["browser_download_url"])
