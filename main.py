__version__ = "1.0"

import re
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser
from template import Template
import configparser

def write_html(html: str) -> None:
    """寫入html"""
    with open("result.html", "w", encoding="utf-8") as f:
        f.write(html)


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
    config.read("config.ini", encoding='utf-8')
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
    return_params = {"cardPoolType": 1}  # cardPoolType {1:角色活動,2:武器活動,3:角色常駐,4:武器常駐,5:新手池,6:新手定向}

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
        self.permanent_characters = ["維里奈", "卡卡羅", "凌陽", "安可", "鑒心"]
        self.data = {}

    def get_data(self, page: int, event_pool: bool = False) -> list | bool:
        self.payload["cardPoolType"] = page
        response = requests.post(self.api_url, json=self.payload)

        if response.status_code == 200:
            return_data = []
            counter = 0  # 總計數
            four_star_counter = 0  # 四星數量計數
            five_star_counter = 0  # 五星數量計數
            four_star_pity_counter = 0  # 四星保底計數
            five_star_pity_counter = 0  # 五星保底計數
            four_star_pity_counter_status = False  # 四星保底計數狀態
            five_star_pity_counter_status = False  # 五星保底計數狀態
            permanent_character_counter = 0  # 常駐角色計數

            data = response.json()["data"]

            print("Request successful!")

            if not data:
                return False

            for item in data:
                return_data.append([item['name'], item['qualityLevel'], item['time']])
                if item['qualityLevel'] == 5:
                    five_star_counter += 1
                    if item['name'] in self.permanent_characters:
                        permanent_character_counter += 1
                    if not five_star_pity_counter_status:
                        five_star_pity_counter = counter
                        five_star_pity_counter_status = True
                if item['qualityLevel'] == 4:
                    four_star_counter += 1
                    if not four_star_pity_counter_status:
                        four_star_pity_counter = counter
                        four_star_pity_counter_status = True

                counter += 1

            if not five_star_pity_counter_status:
                five_star_pity_counter = counter

            if event_pool:
                return_data.append(permanent_character_counter)  # 常駐角色計數(活動卡池才有) 位置[-6]
            return_data.append(four_star_pity_counter)  # 四星保底計數 位置[-5]
            return_data.append(five_star_pity_counter)  # 五星保底計數 位置[-4]
            return_data.append(four_star_counter)  # 四星總數量計數 位置[-3]
            return_data.append(five_star_counter)  # 五星總數量計數 位置[-2]
            return_data.append(counter)  # 總抽數 位置[-1]

            return return_data
        else:
            print("Request failed!")
            messagebox.showerror("錯誤", "URL已過期，請重新進入遊戲抽卡紀錄!")
            edit_file_path_config("none")
            raise Exception("Request failed!")

    def get_all_data(self) -> dict:
        queue = ["角色活動", "武器活動", "角色常駐", "武器常駐", "新手池", "新手定向"]

        for i, title in enumerate(queue):
            if "角色活動" in title:
                current_data = self.get_data(i+1, True)
            else:
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
        self.rank = None
        self.data = data
        self.analyzed_value = {
            "評級": "",
            "運氣分數": 0,
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
            "角色活動五星": 0,
            "角色活動四星": 0,
            "角色活動三星": 0,
            "武器活動五星": 0,
            "武器活動四星": 0,
            "武器活動三星": 0,
            "角色常駐五星": 0,
            "角色常駐四星": 0,
            "角色常駐三星": 0,
            "武器常駐五星": 0,
            "武器常駐四星": 0,
            "武器常駐三星": 0,
            "新手五星": 0,
            "新手四星": 0,
            "新手三星": 0,
            "新手定向五星": 0,
            "新手定向四星": 0,
            "新手定向三星": 0,
        }
        self.weight_ratio = {
            "歪角倍率": 0.75,
            "四星倍率": 1.1,
            "五星倍率": 1.2,
            "四星倍率升階": 0.15,
            "五星倍率升階": 0.15
        }

    def analyze_all(self) -> dict:
        queue_list = ["角色活動", "武器活動", "角色常駐", "武器常駐", "新手", "新手定向"]
        quality_list = ["五星", "四星", "三星"]
        pity_list = ["五星第", "四星第"]
        last_five_star_label = "上一個五星"
        score_info = self.analyze_score()
        all_info = self.get_pool_info("all")
        character_event_info = self.get_pool_info("角色活動")
        weapon_event_info = self.get_pool_info("武器活動")
        character_permanent_info = self.get_pool_info("角色常駐")
        weapon_permanent_info = self.get_pool_info("武器常駐")
        new_player_info = self.get_pool_info("新手池")
        new_player_lock_info = self.get_pool_info("新手定向")
        info_queue_list = [character_event_info, weapon_event_info, character_permanent_info,
                           weapon_permanent_info, new_player_info, new_player_lock_info]

        self.analyzed_value["評級"] = score_info[1]
        self.analyzed_value["運氣分數"] = score_info[0]
        self.analyzed_value["總抽數"] = all_info["total_pity"]
        self.analyzed_value["五星數"] = all_info["total_five_star"]

        for index, title in enumerate(queue_list):
            self.analyzed_value[title+quality_list[0]] = info_queue_list[index]["total_five_star"]
            self.analyzed_value[title+quality_list[1]] = info_queue_list[index]["total_four_star"]
            self.analyzed_value[title+quality_list[2]] = (info_queue_list[index]["total_pity"] -
                                                          info_queue_list[index]["total_five_star"] -
                                                          info_queue_list[index]["total_four_star"])

        for i in range(4):
            self.analyzed_value[queue_list[i]+pity_list[0]] = info_queue_list[i]["five_star_pity"]
            self.analyzed_value[queue_list[i]+pity_list[1]] = info_queue_list[i]["four_star_pity"]
            self.analyzed_value[queue_list[i]+last_five_star_label] = info_queue_list[i]["last_five_star"]

        return self.analyzed_value

    def analyze_score(self) -> tuple[int, str]:
        all_info = self.get_pool_info("all")
        print("所有數據:", all_info)
        four_star_score = 0
        five_star_score = 0

        five_star_avg = all_info["total_pity"] / all_info["total_five_star"]
        print("五星平均出貨:", five_star_avg)
        if five_star_avg != 0:
            five_star_range = 80 - five_star_avg
            five_star_bonus_stage = five_star_range // 10
            five_star_score = (five_star_range * (self.weight_ratio["五星倍率"] +
                               (1 + five_star_bonus_stage * self.weight_ratio["五星倍率升階"])))

        four_star_avg = all_info["total_pity"] / all_info["total_four_star"]
        print("四星平均出貨:", four_star_avg)
        if four_star_avg != 0:
            four_star_range = 10 - four_star_avg
            four_star_bonus_stage = four_star_range // 1.5
            four_star_score = (four_star_range * (self.weight_ratio["四星倍率"] +
                               (1 + four_star_bonus_stage * self.weight_ratio["四星倍率升階"])))

        self.score += round(five_star_score + four_star_score)

        if all_info["total_loss_event_five_star"] > 0:
            for _ in range(all_info["total_loss_event_five_star"]):
                self.score *= self.weight_ratio["歪角倍率"]

        if int(self.score) > 185:
            self.rank = "史詩級歐皇"
        elif int(self.score) > 150:
            self.rank = "大歐皇"
        elif int(self.score) > 120:
            self.rank = "歐洲人"
        elif int(self.score) > 100:
            self.rank = "普普通通"
        elif int(self.score) > 80:
            self.rank = "非洲人"
        elif int(self.score) > 60:
            self.rank = "非洲酋長"
        else:
            self.rank = "史詩級非洲"

        print("分數:", int(self.score))
        print("等級:", self.rank)

        return int(self.score), self.rank

    def get_pool_info(self, info_type: str) -> dict:
        """
        :param info_type: "all"
        :return: {"total_pity": int,"total_four_star": int , "total_five_star": int, "total_loss_event_five_star": int}

        :param info_type: "角色活動"
        :return: {
                "total_pity": int,"total_four_star": int , "total_five_star": int, "total_loss_event_five_star": int,
                "four_star_pity": int, "five_star_pity": int, "last_five_star": str
                }

        :param info_type: "武器活動", "角色常駐", "武器常駐"
        :return: {
                "total_pity": int,"total_four_star": int , "total_five_star": int, "four_star_pity": int,
                "five_star_pity": int, "last_five_star": str
                }

        :param info_type: "新手池", "新手定向"
        :return: {
                "total_pity": int,"total_four_star": int , "total_five_star": int, "last_five_star": str
                }
        """
        four_star_pity = 0
        five_star_pity = 0
        total_pity = 0
        total_four_star = 0
        total_five_star = 0
        total_loss_event_five_star = 0
        last_five_star = ""

        if info_type == "all":
            for key in self.data:
                if self.data[key]:
                    total_pity += self.data[key][-1]
                    total_four_star += self.data[key][-3]
                    total_five_star += self.data[key][-2]
                    if key in ["角色活動"]:
                        total_loss_event_five_star += self.data[key][-6]

            return {
                "total_pity": total_pity,
                "total_four_star": total_four_star,
                "total_five_star": total_five_star,
                "total_loss_event_five_star": total_loss_event_five_star
            }

        elif info_type in ["角色活動"]:
            if self.data[info_type]:
                total_loss_event_five_star = self.data[info_type][-6]
                four_star_pity = self.data[info_type][-5]
                five_star_pity = self.data[info_type][-4]
                total_four_star = self.data[info_type][-3]
                total_five_star = self.data[info_type][-2]
                total_pity = self.data[info_type][-1]

                for item in self.data[info_type]:
                    try:
                        if item[1] == 5:
                            last_five_star = item[0]
                    except TypeError:
                        pass

            return {
                "total_pity": total_pity,
                "total_four_star": total_four_star,
                "total_five_star": total_five_star,
                "total_loss_event_five_star": total_loss_event_five_star,
                "four_star_pity": four_star_pity,
                "five_star_pity": five_star_pity,
                "last_five_star": last_five_star
            }

        elif info_type in ["角色常駐", "武器常駐", "武器活動"]:
            if self.data[info_type]:
                four_star_pity = self.data[info_type][-5]
                five_star_pity = self.data[info_type][-4]
                total_four_star = self.data[info_type][-3]
                total_five_star = self.data[info_type][-2]
                total_pity = self.data[info_type][-1]

                for item in self.data[info_type]:
                    try:
                        if item[1] == 5:
                            last_five_star = item[0]
                    except TypeError:
                        pass

            return {
                "total_pity": total_pity,
                "total_four_star": total_four_star,
                "total_five_star": total_five_star,
                "four_star_pity": four_star_pity,
                "five_star_pity": five_star_pity,
                "last_five_star": last_five_star
            }

        elif info_type in ["新手池", "新手定向"]:
            if self.data[info_type]:
                total_four_star = self.data[info_type][-3]
                total_five_star = self.data[info_type][-2]
                total_pity = self.data[info_type][-1]

                for item in self.data[info_type]:
                    try:
                        if item[1] == 5:
                            last_five_star = item[0]
                    except TypeError:
                        pass

            return {
                "total_pity": total_pity,
                "total_four_star": total_four_star,
                "total_five_star": total_five_star,
                "last_five_star": last_five_star
            }


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
        webbrowser.open("https://youtu.be/dQHYDs62lS8")

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

            analyzed_data = Analyzer(data).analyze_all()

            for i, key in enumerate(data):
                if not key:
                    chart_filter.append(i+1)

            if chart_filter:
                template = Template(chart_filter)
            else:
                template = Template()

            html_str = template(analyzed_data)

            write_html(html_str)

            webbrowser.open("result.html")

        else:
            messagebox.showerror("錯誤", "請先選擇log文件!")

    def loop(self):
        self.mainloop()


def main():
    app = Ui()
    app.loop()

if __name__ == '__main__':
    main()