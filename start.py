import requests
import os
from tqdm import tqdm
import subprocess
from tkinter import messagebox
import configparser


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


def versionInquire():
    config = configparser.ConfigParser()
    config.optionxform = str
    path=os.getcwd()
    config.read(f"{path}/config.ini", encoding='utf-8')

    return float(config.get("var", "version"))


def edit_file_path_config(value) -> None:
    """修改配置"""
    config = configparser.ConfigParser()
    config.optionxform = str
    path=os.getcwd()
    config.read(f"{path}/config.ini", encoding='utf-8')
    config.set("var", "version", f'{value}')
    with open("config.ini", "w", encoding='utf-8') as config_file:
        config.write(config_file)


def check_latest_release():
    latest_release = requests.get("https://api.github.com/repos/m216884792/WurtheringWave_Analyzer/releases/latest").json()
    print(f"Latest Version:{latest_release['tag_name']}")

    __version__=versionInquire()
    print(f'version={__version__}')
    print(latest_release['tag_name'])
    if __version__ != float(latest_release['tag_name']):
        if messagebox.askyesno("發現新版本",
                               f"新版本 ({latest_release['tag_name']}) 目前可供下載. "
                               f"要下載嗎?\n更新內容 :\n{latest_release['body']}"):

            download_exe(latest_release["assets"][0]["browser_download_url"])
            edit_file_path_config(float(latest_release['tag_name']))

    subprocess.run(f'{os.getcwd()}/main.exe "action"="gogo"', stdout=subprocess.PIPE, text=False)


if __name__ == '__main__':
    check_latest_release()
