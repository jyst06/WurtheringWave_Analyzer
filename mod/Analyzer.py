from datetime import datetime

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
        last_five_star_status = False

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
                        if item[1] == 5 and not last_five_star_status:
                            last_five_star = item[0]
                            last_five_star_status = True
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
                        if item[1] == 5 and not last_five_star_status:
                            last_five_star = item[0]
                            last_five_star_status = True
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
                        if item[1] == 5 and not last_five_star_status:
                            last_five_star = item[0]
                            last_five_star_status = True
                    except TypeError:
                        pass

            return {
                "total_pity": total_pity,
                "total_four_star": total_four_star,
                "total_five_star": total_five_star,
                "last_five_star": last_five_star
            }

    def analyze_table_data(self) -> list:
        return_data_list = []
        five_star_history = []
        counter = 0

        for key in self.data:
            if not self.data[key]:
                continue
            for params_list in self.data[key]:
                if type(params_list) is list:
                    if params_list[1] == 5:
                        if not five_star_history:
                            five_star_history.append(key)  # 卡池
                            five_star_history.append(params_list[0])  # 名稱
                            five_star_history.append(params_list[2])  # 日期
                            counter += 1
                            print(f"發現五星:{five_star_history}")
                        else:
                            five_star_history.append(counter - 1)  # 計數
                            return_data_list.append(five_star_history)
                            print(f"儲存計數:{five_star_history}")
                            five_star_history = []
                            counter = 0

                            five_star_history.append(key)  # 卡池
                            five_star_history.append(params_list[0])  # 名稱
                            five_star_history.append(params_list[2])  # 日期
                            counter += 1
                            print(f"發現五星:{five_star_history}")

                    if counter != 0:
                        counter += 1

            if five_star_history:
                five_star_history.append(counter - 1)
                return_data_list.append(five_star_history)
                print(f"儲存計數:{five_star_history}")
                five_star_history = []
                counter = 0

        return_data_list = sorted(return_data_list,
                                  key=lambda x: datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S'), reverse=True)

        return return_data_list