import requests
from tkinter import  messagebox
from .groceries import edit_file_path_config

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
                    if not four_star_pity_counter_status:
                        four_star_pity_counter = counter
                        four_star_pity_counter_status = True

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
            messagebox.showerror("錯誤", "URL不可用，請重新進入遊戲抽卡紀錄!")
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