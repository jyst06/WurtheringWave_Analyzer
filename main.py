import re
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser

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
                return_data.append([item['name'], item['qualityLevel']])
                if five_star_counter == 0:
                    if item['qualityLevel'] == 5:
                        five_star_counter = counter
                counter += 1

            return_data.append(counter) # [-2]
            return_data.append(five_star_counter) # [-1]

            return return_data
        else:
            print("Request failed!")
            return False

    def get_all_data(self):
        queue = ["角色活動", "武器活動", "角色常駐", "武器常駐", "新手池", "新手定向"]

        for i, title in enumerate(queue):
            current_data = self.get_data(i+1)
            if current_data:
                self.data[title] = current_data
            else:
                self.data[title] = False


class Analyzer:
    """分析抽卡結果"""
    def __init__(self):
        pass


class Template:
    """網頁模板"""
    def __init__(self):
        self.filling_value = dict(

        )


class Ui(ctk.CTk):
    """UI介面"""
    def __init__(self):
        super().__init__()
        self.geometry("300x300")
        self.title("鳴潮抽卡分析")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.pack_items()

        self.file_path = None

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
        self.file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])

    def help_video(self):
        webbrowser.open("")

    def open_github(self):
        webbrowser.open("https://github.com/jyst06?tab=repositories")

    def run_task(self):
        if self.file_path:
            url = get_url_from_log(self.file_path)
            payload = transform_url_to_payload(url)

            pool = Pool(payload)
            data = pool.get_all_data()
        else:
            messagebox.showerror("錯誤", "請先選擇log文件")

    def loop(self):
        self.mainloop()


def main():
    app = Ui()
    app.loop()


if __name__ == '__main__':
    main()