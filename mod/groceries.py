import configparser
import re


def edit_file_path_config(path: str,path2=None) -> None:
    """修改配置路徑"""
    config = configparser.ConfigParser()
    config.read(f"{path2}/config.ini", encoding='utf-8')
    config.set("path", "log_path", path)
    with open("config.ini", "w", encoding='utf-8') as config_file:
        config.write(config_file)

def edit_file_path_config2(path, key,value) -> None:
    """修改配置"""
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(f"{path}/config.ini", encoding='utf-8')
    config.set("var", f"{key}", f'{value}')
    with open("config.ini", "w", encoding='utf-8') as config_file:
        config.write(config_file)

def read_file_path_config(path) -> str | None:
    """讀取路徑"""
    config = configparser.ConfigParser()
    config.read(f"{path}/config.ini", encoding='utf-8')
    path_config = config.get("path", "log_path")
    
    if path_config == "none":
        return None
    else:
        return path_config

def read_file_path_config2(path):
    vardcit={}
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(f"{path}/config.ini", encoding='utf-8')
    for key, value in config.items('var'):
        vardcit[key]=value

    return vardcit

def write_html(html: str,path=None) -> None:
    """寫入html"""
    with open(f"{path}/result.html", "w", encoding="utf-8") as f:
        f.write(html)

def get_url_from_log(filepath: str) -> str:
    """從遊戲log文件解析出請求URL"""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if "https://aki-gm-resources-oversea.aki-game.net/aki/gacha/index.html#/record" in line:
                url_match = re.search(r'"url":"([^"]+)"', line)

                print(f"Base URL:{url_match.group(1)}")
                return url_match.group(1)
    return None

def transform_url_to_payload(url: str) -> dict:
    """URL轉換為payload參數"""
    transform_name = {
        "svr_id": "serverId",
        "record_id": "recordId",
        "lang": "languageCode",
        "resources_id": "cardPoolId",
        "player_id": "playerId"
    }
    return_params = {"cardPoolType": 1}  # cardPoolType {1:角色活動,2:武器活動,3:角色常駐,4:武器常駐,5:新手池,6:新手定向}

    query_params = url.split("?")[-1]
    params = query_params.split("&")
    for param in params:
        key, value = param.split("=")
        if key in transform_name:
            return_params[transform_name[key]] = value

    return return_params

