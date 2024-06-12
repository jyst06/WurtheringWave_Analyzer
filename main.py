__version__ = "1.8"


import os
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
import webbrowser
from mod.template import Template
from mod.groceries import write_html,transform_url_to_payload
from mod.groceries import get_url_from_log,edit_file_path_config2,read_file_path_config2
from mod.Pool import Pool
from mod.Analyzer import Analyzer


class Ui(ctk.CTk):
    """UI介面"""
    def __init__(self):
        super().__init__()
        self.geometry("300x300")
        self.title(f"鳴潮抽卡分析 v{__version__}")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.path=os.getcwd()
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

        help_button = ctk.CTkButton(button_container, text="教學", command=self.help_video, width=90)
        help_button.grid(pady=10, padx=5, column=0, row=0)

        feedback_button = ctk.CTkButton(button_container, text="反饋", command=self.feed_back, width=90)
        feedback_button.grid(pady=10, padx=5, column=1, row=0)

        github_button = ctk.CTkButton(button_container, text="Github", command=self.open_github, width=90)
        github_button.grid(pady=10, padx=5, column=2, row=0)

    def open_file(self):
        logpath = filedialog.askopenfilename(filetypes=[("Log files", "*.log")])
        if len(logpath)>0:
            url = get_url_from_log(logpath)
            if not url:
                messagebox.showerror("錯誤", f"錯誤: 此檔案內所需無網址")
            else:
                messagebox.showinfo("導入成功", logpath)
                payload = transform_url_to_payload(url)
                for key,value in payload.items():
                    edit_file_path_config2(self.path,key,value)

    def help_video(self):
        webbrowser.open("https://youtu.be/dQHYDs62lS8")

    def feed_back(self):
        webbrowser.open("https://forms.gle/ocmNrxsmGKdC8hrX6")

    def open_github(self):
        webbrowser.open("https://github.com/jyst06?tab=repositories")

    def run_task(self):
        chart_filter = []

        try:
            payload=read_file_path_config2(self.path)
            pool = Pool(payload)
            data = pool.get_all_data()

            if len(data)>0:
                analyzer = Analyzer(data)
                table_data = analyzer.analyze_table_data()
                analyzed_data = analyzer.analyze_all()

                if analyzed_data:
                    for i, key in enumerate(data):
                        if not key:
                            chart_filter.append(i+1)

                    if chart_filter:
                        template = Template(chart_filter)
                    else:
                        template = Template()

                    html_str = template(analyzed_data, table_data)

                    write_html(html_str,path=self.path)

                    webbrowser.open("result.html")

                else:
                    messagebox.showerror("錯誤", f"錯誤: 請查看數據是否錯誤")
            else:
                messagebox.showerror("錯誤", f"錯誤: 請導入所需檔案")

        except Exception as e:
            messagebox.showerror("錯誤", f"錯誤: {e}")


    def loop(self):
        self.mainloop()


def listtodcit(importvar):
    vardict={}
    del importvar[0]
    if len(importvar)>0:
        for i in importvar:
            i2=i.split('=')
            vardict[i2[0]]=i2[1]
    return vardict

def main():
    app = Ui()
    app.loop()


if __name__ == '__main__':
    vardcit=listtodcit(sys.argv)
    if vardcit.get('action',None)=='gogo':
        main()
