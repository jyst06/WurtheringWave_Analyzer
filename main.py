import re
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser
from template import Template
import configparser

def read_file_path_config() -> str | None:
    """讀取路徑"""
    config = configparser.ConfigParser()
    config.read("config.ini", encoding='utf-8')
    path_config = config.get("path", "log_path")
    if path_config == "none":
        return None
    else:
        return path_config


def edit_file_path_config(path: str) -> None:
    """修改配置路徑"""
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.set("path", "log_path", path)
    with open("config.ini", "w", encoding='utf-8') as config_file:
        config.write(config_file)


def get_url_from_log(filepath: str) -> str:
    """從遊戲log文件解析出請求URL"""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if "OpenWebView" in line:
                url_match = re.search(r'"url":"([^"]+)"', line)

                return url_match.group(1)


def transform_url_to_payload(url: str) -> dict:
    """URL轉換為payload參數"""
    transform_name = {
        "svr_id": "serverId",
        "record_id": "recordId",
        "lang": "languageCode",
        "resources_id": "cardPoolId",
        "player_id": "playerId"
    }
    return_params = {"cardPoolType": 1} # cardPoolType {1:角色活動,2:武器活動,3:角色常駐,4:武器常駐,5:新手池,6:新手定向}

    query_params = url.split("?")[-1]
    params = query_params.split("&")
    for param in params:
        key, value = param.split("=")
        if key in transform_name:
            return_params[transform_name[key]] = value

    return return_params


class Pool:
    """用於取得卡池紀錄"""
    def __init__(self, payload: dict):
        self.payload = payload
        self.api_url = "https://gmserver-api.aki-game2.net/gacha/record/query"
        self.data = {}

    def get_data(self, page: int) -> list | bool:
        self.payload["cardPoolType"] = page
        response = requests.post(self.api_url, json=self.payload)

        if response.status_code == 200:
            return_data = []
            counter = 0 # 總計數
            five_star_counter = 0 # 五星計數
            print("Request successful!")
            data = response.json()["data"]

            if not data:
                return False

            for item in data:
                return_data.append([item['name'], item['qualityLevel'], item['time']])
                if five_star_counter == 0:
                    if item['qualityLevel'] == 5:
                        five_star_counter = counter
                counter += 1

            if five_star_counter == 0:
                five_star_counter = counter

            return_data.append(counter) # [-2]
            return_data.append(five_star_counter) # [-1]

            return return_data
        else:
            print("Request failed!")
            messagebox.showerror("錯誤", "URL已過期，請重新進入遊戲抽卡紀錄!")
            edit_file_path_config("none")
            raise Exception("Request failed!")

    def get_all_data(self) -> dict:
        queue = ["角色活動", "武器活動", "角色常駐", "武器常駐", "新手池", "新手定向"]

        for i, title in enumerate(queue):
            current_data = self.get_data(i+1)
            if current_data:
                self.data[title] = current_data
            else:
                self.data[title] = False

        return self.data


class Analyzer:
    """分析抽卡結果"""
    def __init__(self, data: dict):
        self.score = 100
        self.data = data
        self.analyzed_value = {
            "評級": "",
            "總抽數": 0,
            "五星數": 0,
            "角色活動五星第": 0,
            "角色活動四星第": 0,
            "角色活動上一個五星": "",
            "武器活動五星第": 0,
            "武器活動四星第": 0,
            "武器活動上一個五星": "",
            "角色常駐五星第": 0,
            "角色常駐四星第": 0,
            "角色常駐上一個五星": "",
            "武器常駐五星第": 0,
            "武器常駐四星第": 0,
            "武器常駐上一個五星": "",
            "新手五星": 0,
            "新手四星": 0,
            "新手三星": 0,
            "新手自選五星": 0,
            "新手自選四星": 0,
            "新手自選三星": 0,
        }

    def analyze_all(self) -> dict:
        pass

    def analyze_score(self):
        pass


class Ui(ctk.CTk):
    """UI介面"""
    def __init__(self):
        super().__init__()
        self.geometry("300x300")
        self.title("鳴潮抽卡分析")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.pack_items()

    def pack_items(self):
        step1_label = ctk.CTkLabel(self, text="第一步", font=("Arial", 16))
        step1_label.pack(pady=10)

        open_file_button = ctk.CTkButton(self, text="log檔導入", command=self.open_file)
        open_file_button.pack(pady=10)

        step2_label = ctk.CTkLabel(self, text="第二步", font=("Arial", 16))
        step2_label.pack(pady=10)

        run_button = ctk.CTkButton(self, text="顯示結果", command=self.run_task)
        run_button.pack(pady=10)

        button_container = ctk.CTkFrame(self)
        button_container.pack(side="bottom")

        help_button = ctk.CTkButton(button_container, text="教學", command=self.help_video)
        help_button.pack(side="left", pady=10, padx=10)

        github_button = ctk.CTkButton(button_container, text="Github", command=self.open_github)
        github_button.pack(side="right", pady=10, padx=10)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
        edit_file_path_config(path)

    def help_video(self):
        webbrowser.open("")

    def open_github(self):
        webbrowser.open("https://github.com/jyst06?tab=repositories")

    def run_task(self):
        chart_filter = []
        file_path = read_file_path_config()
        if file_path:
            url = get_url_from_log(file_path)
            payload = transform_url_to_payload(url)

            pool = Pool(payload)
            data = pool.get_all_data()
            print(data)

            analyzed_data = Analyzer(data).analyze_all()

            for i, key in enumerate(data):
                if not key:
                    chart_filter.append(i+1)

            if chart_filter:
                template = Template(chart_filter)
            else:
                template = Template()

            template(analyzed_data)

        else:
            messagebox.showerror("錯誤", "請先選擇log文件!")

    def loop(self):
        self.mainloop()


def main():
    app = Ui()
    app.loop()


if __name__ == '__main__':
    main()