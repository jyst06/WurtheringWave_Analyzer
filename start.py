import requests
import os
from tqdm import tqdm
import subprocess
from tkinter import messagebox
import json


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


def check_latest_release():
    response = requests.get("https://api.github.com/repos/jyst06/WurtheringWave_Analyzer_exe/releases/latest")
    latest_release = response.json()
    print(f"Latest Version:{latest_release['tag_name']}")
    print(latest_release["assets"][0]["browser_download_url"])

    __version__=versionInquire()
    print(f'version={__version__}')

    if __version__ != float(latest_release['tag_name']):
        if messagebox.askyesno("發現新版本",
                               f"新版本 ({latest_release['tag_name']}) 目前可供下載. "
                               f"要下載嗎?\n更新內容 :\n{latest_release['body']}"):

            latest_release = requests.get("https://api.github.com/repos/jyst06/WurtheringWave_Analyzer_exe/releases/latest").json()
            download_exe(latest_release["assets"][0]["browser_download_url"])

    subprocess.run(f'{os.getcwd()}/main.exe "action"="gogo"', stdout=subprocess.PIPE, text=False)


def versionInquire():
    subprocessstr=subprocess.Popen(f'{os.getcwd()}/main.exe "action"="version"', stdout=subprocess.PIPE, text=True)

    returnstr=subprocessstr.communicate()[0]
    subprocessstr.kill()
    returnstr=returnstr.replace("'", '"')
    returnstr=json.loads(returnstr)

    return float(returnstr['action'])

if __name__ == '__main__':
    check_latest_release()
