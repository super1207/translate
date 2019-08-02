from configparser import ConfigParser
import tkinter as tk
class Config:
    '''用于读取配置文件
    '''
    def __init__(self):
        try:
            cf = ConfigParser()
            cf.read("tra_config.ini", encoding="utf-8")
            self.MK_APIKEY = cf.get("OCRMAKER", "MK_APIKEY")
            self.APP_ID = cf.get("BAIDUOCR", "APP_ID")
            self.API_KEY = cf.get("BAIDUOCR", "API_KEY")
            self.SECRET_KEY = cf.get("BAIDUOCR", "SECRET_KEY")
            # printf(self.APP_ID)
            if self.APP_ID == '123456789':
                root = tk.Tk()
                root.withdraw()
                tk.messagebox.showinfo(title="亲~", message="你可能没有设置正确的配置文件，所以，将使用默认的配置。")
                root.destroy()
                raise Exception("配置文件错误")
            root = tk.Tk()
            root.withdraw()
            tk.messagebox.showinfo(title="亲~", message="配置文件载入成功")
            root.destroy()
        except:
            self.MK_APIKEY = '5cbc1fd77788957'
            self.APP_ID = "15588329"
            self.API_KEY = "ns0HW7W2QbUZGvMUklFiIUiW"
            self.SECRET_KEY = "EsenI27FLCYBwaRSIIqwO9lTsYdCFr9B"

    def save(self):
        cf = ConfigParser()
        cf.add_section("VERSION")
        cf.set("VERSION", "VERSION", "4.x")
        cf.add_section("OCRMAKER")
        cf.set("OCRMAKER", "MK_APIKEY", self.MK_APIKEY)
        cf.add_section("BAIDUOCR")
        cf.set("BAIDUOCR", "APP_ID", '123456789')  # self.APP_ID
        cf.set("BAIDUOCR", "API_KEY", '123456789')  # self.API_KEY
        cf.set("BAIDUOCR", "SECRET_KEY", '123456789')  # self.SECRET_KEY
        with open("tra_config.ini", "w+") as f:
            cf.write(f)
