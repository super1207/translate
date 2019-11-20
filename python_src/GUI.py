import os
import re
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from configparser import ConfigParser
from io import BytesIO
from tkinter import ttk
from urllib import parse
import webbrowser
import json
import glob
import random
import sys
import logging
import base64

import js2py
import requests
from aip import AipOcr
from PIL import Image, ImageGrab
from requests_toolbelt import MultipartEncoder
from ctypes import create_string_buffer,string_at,WinDLL
import _thread
from systray import SysTrayIcon


from formatcpp import formatcpp
from pasteUbuntu import pasteUbuntu
from Config import Config
from google import google



def resource_path(relative_path):
    '''用于获取pyinstaller打包后的资源路径
    '''
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource
        base_path = sys._MEIPASS  # sys将会在pyinstaller打包后被引入
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class plus_traslate:
    '''在这里处理外部dll插件的翻译事件
    '''
    def translate(self, word, to):
        name = self.s.comboxlist0.get() # 获取当前的插件名字
        for i in self.s.dlllist:
            s = create_string_buffer(''.encode(), 9000) #in dll is 8192
            i.name(s)
            if string_at(s).decode('utf-8') == name:
                dll = i
        s = create_string_buffer(''.encode(), 9000)  ##in dll is 8192
        dll.mainfun(s) # 执行翻译功能
        return string_at(s).decode('utf-8')

class section:
    '''用于支持右键复制粘贴
    '''
    def onPaste(self):
        try:
            self.s.delete('sel.first', 'sel.last')
        except:
            pass
        self.text = self.s.clipboard_get()
        pos = self.s.index(tk.INSERT)
        self.s.insert(pos,str(self.text))
 
    def onCopy(self):
        self.s.clipboard_clear()
        self.text = str(self.s.get('sel.first', 'sel.last'))
        self.s.clipboard_append(self.text)
 
    def onCut(self):
        self.onCopy()
        self.s.delete('sel.first', 'sel.last')


class GUI:
    '''界面逻辑'''
    def aboutClick(self):
        '''关于按钮被点击'''
        self.logger.debug("aboutClick call")
        tk.messagebox.showinfo(title='关于', message='''这个工具会监控剪切板中的图片或文字，将其翻译成中文或英文
    支持含有中文，英文，韩文，日文的图片
    推荐使用win+shift+s(WIN10)或者QQ截图(ctrl+alt+a)工具截图''')

    def getAppId(self):
        '''获取APPID按钮被点击
        '''
        self.logger.debug("getAppId call")
        tk.messagebox.showinfo(title='APP_ID', message='''
        APP_ID = ''' + self.APP_ID)

    def upClick(self):
        '''检查更新按钮被点击
        '''
        self.logger.debug("upClick call")
        webbrowser.open_new_tab('''https://github.com/super1207/translate''')

    def useConfig(self):
        '''生成配置文件
        '''
        self.logger.debug("useConfig call")
        try:
            self.cf.save()
            tk.messagebox.showinfo(
                title='生成配置文件成功', message='''已在当前目录下生成配置文件tra_config.ini，你可以通过修改它来修改软件中的一些关键参数，例如百度OCR的KEY''')
        except Exception as e:
            tk.messagebox.showerror(title='生成配置文件失败', message=str(e))

    def apithread(self,apiText,i):
        '''这里处理和外部dll之间的通讯
        '''
        self.logger.debug("apithread call")
        def fun(i):
            try:
                exec(apiText)
            except Exception as e:
                self.window.state('normal')
                self.window.wm_attributes('-topmost', 1)
                self.outText.delete("1.0", 'end')
                self.outText.insert(tkinter.END, "出现异常:\n" + str(e))
        _thread.start_new_thread(fun,(i,))

    def translateBtnClick(self):
        '''翻译按钮被点击
        '''
        self.logger.debug("translateBtnClick call")
        def deal():
            try:
                intputstring = str(self.inputText.get('1.0', 'end'))
                self.outText.delete('1.0', 'end')
                self.outText.insert(tk.END, '正在处理。。。')
                outstring = self.getfy().translate(intputstring, self.gettl())
                self.outText.delete('1.0', 'end')
                self.outText.insert(tk.END, outstring)
            except Exception as e:
                self.window.state('normal')
                self.window.wm_attributes('-topmost', 1)
                self.outText.delete("1.0", 'end')
                self.outText.insert(tkinter.END, "出现异常:\n" + str(e))

        _thread.start_new_thread(deal, ())

    def getFromTXT(self):
        '''从TXT文件获取信息
        '''
        self.logger.debug("getFromTXT call")
        try:
            fn = tk.filedialog.askopenfilename(filetypes=[('text files', '.txt')])
            if fn != '':
                with open(fn, 'rb') as f:
                    self.inputText.delete('1.0', 'end')
                    self.inputText.insert(tk.END, f.read().decode('utf-8'))
                    self.translateBtnClick()
        except Exception as e:
            self.window.state('normal')
            self.window.wm_attributes('-topmost', 1)
            self.outText.delete("1.0", 'end')
            self.outText.insert(tkinter.END, "出现异常:\n" + str(e))

    def getFromImage(self):
        '''从图像文件获取信息
        '''
        self.logger.debug("getFromImage call")
        def deal(T1, T2, im):
            try:
                T1.delete("1.0", 'end')
                T1.insert(tkinter.END, '正在ocr...')
                text = self.OCRAPI(im)
                T1.delete("1.0", 'end')
                T1.insert(tkinter.END, text)
                T2.delete("1.0", 'end')
                T2.insert(tkinter.END, "正在翻译...")
                text2 = self.getfy().translate(text, self.gettl())
                T2.delete("1.0", 'end')
                T2.insert(tkinter.END, text2)
            except Exception as e:
                self.window.state('normal')
                self.window.wm_attributes('-topmost', 1)
                self.outText.delete("1.0", 'end')
                self.outText.insert(tkinter.END, "出现异常:\n" + str(e))

        fn = tk.filedialog.askopenfilename(
            filetypes=[('Image', '*.png;*.jpg;*.bmp')])
        if fn != '':
            image = Image.open(fn)
            _thread.start_new_thread(deal, (self.inputText, self.outText, image))

    def clearBtnClick(self):
        '''清屏按钮被点击
        '''
        self.logger.debug("clearBtnClick call")
        self.outText.delete('1.0', 'end')
        self.inputText.delete('1.0', 'end')

    def baiduOCR(self, image):
        '''百度OCR
        '''
        self.logger.debug("baiduOCR call")
        """ 你的 APPID AK SK """
        try:
            client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        except:
            raise Exception("百度OCR模块出错，请先检查网络，然后重试，如果任然出现这条信息，请联系作者~")
        output = BytesIO()
        image.save(output, "PNG")
        image = output.getvalue()
        output.close()

        """ 如果有可选参数 """
        options = {"detect_language": "true"}
        """ 带参数调用通用文字识别, 图片参数为本地图片 """
        try:
            out = client.basicGeneral(image, options)
        except:
            raise Exception("百度OCR模块出错，请先检查网络，然后重试，如果任然出现这条信息，请联系作者~")
        # print(out)
        return '\n'.join([w['words'] for w in out['words_result']])

    def getfy(self):
        '''获取翻译对象
        '''
        self.logger.debug("getfy call")
        s = self.comboxlist0.get()
        if s == "使用谷歌翻译":
            return google()
        elif s == "使用百度翻译":
            return baidu()
        elif s == "C/C++代码运行":
            return runcpp()
        elif s == "C/C++代码美化":
            return formatcpp()
        elif s == "发布临时文字":
            return pasteUbuntu()
        else:
            k = plus_traslate() # 从dll插件获取
            k.s = self
            return k

    def gettl(self):
        '''获取翻译参数
        '''
        self.logger.debug("gettl call")
        s = self.comboxlist.get()
        if s == "翻译为中文(简体)":
            return 'zh-CN'
        elif s == "翻译为中文(繁体)":
            return 'zh-TW'
        elif s == "翻译为英文":
            return 'en'
        elif s == "翻译为日文":
            return 'ja'
        else:
            return 'ko'

    def thread_fun(self, root, T1, T2):
        '''监听剪切板
        '''
        self.logger.debug("thread_fun call")
        LastPic = 100
        try:
            tmp_value = self.window.clipboard_get()
        except:
            tmp_value = ""
        im = ImageGrab.grabclipboard()
        if isinstance(im, Image.Image):
            width, height = im.size
            LastPic = width + height
        while True:
            try:
                time.sleep(1)
                if not self.cb1var.get():
                    continue
                im = ImageGrab.grabclipboard()
                if isinstance(im, Image.Image):
                    width, height = im.size
                    if width + height != LastPic:
                        LastPic = width + height
                        root.state('normal')
                        root.wm_attributes('-topmost', 1)
                        self.inputText.delete("1.0", 'end')
                        self.inputText.insert(tkinter.END, '正在ocr...')
                        text = self.OCRAPI(im)
                        self.inputText.delete("1.0", 'end')
                        self.inputText.insert(tkinter.END, text)
                        root.state('normal')
                        root.wm_attributes('-topmost', 1)
                        if self.comboxlist0.get() != "识别数学公式":
                            self.outText.delete("1.0", 'end')
                            self.outText.insert(tkinter.END, "正在翻译...")
                            text2 = self.getfy().translate(text, self.gettl())
                            self.outText.delete("1.0", 'end')
                            self.outText.insert(tkinter.END, text2)
                        else:
                            self.outText.delete("1.0", 'end')
                            self.outText.insert(tkinter.END, text)
                else:
                    try:
                        value = self.window.clipboard_get()
                    except:
                        continue
                    if value != tmp_value:
                        tmp_value = value
                        root.state('normal')
                        root.wm_attributes('-topmost', 1)
                        self.inputText.delete("1.0", 'end')
                        self.inputText.insert(tkinter.END, value)
                        self.translateBtnClick()
            except Exception as e:
                root.state('normal')
                root.wm_attributes('-topmost', 1)
                self.outText.delete("1.0", 'end')
                self.outText.insert(tkinter.END, "出现异常:\n" + str(e))

    def center_window(self,root, width, height):
        '''用于移动界面
        '''
        self.logger.debug("center_window call")
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height,
                                (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def comboxlist1_OCR(self, e):
        '''用于OCR引擎选择
        '''
        self.logger.debug("comboxlist1_OCR call")
        def deal(s):
            global OCRLANGUAGE
            OCRLANGUAGE = s
            f.destroy()

        if self.comboxlist1.get() == "使用OCRMAKER":
            tk.messagebox.showinfo(title="亲~", message='''OCRMAKER必须指定要识别的图片的语言,
            若你的图片中包含多种语言，请使用百度OCR''')
            f = tk.Toplevel()
            f.wm_attributes('-topmost', 1)
            f.grab_set()
            f.iconbitmap(self.filename)
            self.center_window(f, 50, 150)
            Btn1 = tk.Button(f, width=30, text="简体中文", bg='Lavender', command=lambda: deal('chs'))
            Btn2 = tk.Button(f, width=30, text="繁体中文", bg='Lavender', command=lambda: deal('cht'))
            Btn3 = tk.Button(f, width=30, text="英文", bg='Lavender', command=lambda: deal('eng'))
            Btn4 = tk.Button(f, width=30, text="日文", bg='Lavender', command=lambda: deal('jpn'))
            Btn5 = tk.Button(f, width=30, text="韩文", bg='Lavender', command=lambda: deal('kor'))
            Btn1.pack()
            Btn2.pack()
            Btn3.pack()
            Btn4.pack()
            Btn5.pack()
            f.mainloop()

    def comboxlist0_msg(self, e):
        '''用于功能选择
        '''
        self.logger.debug("comboxlist0_msg call")
        if self.comboxlist0.get() == 'C/C++代码美化':
            self.translateBtn['text'] = "美化"
            self.comboxlist['state'] = 'readonly'
            self.comboxlist["values"] = ("C/C++代码美化",)
            self.comboxlist.current(0)
        elif self.comboxlist0.get() == "使用谷歌翻译":
            self.translateBtn['text'] = "翻译"
            self.comboxlist['state'] = 'readonly'
            self.comboxlist["values"] = ("翻译为中文(简体)", "翻译为中文(繁体)",
                                         "翻译为英文", "翻译为日文", "翻译为韩文")
            self.comboxlist.current(0)
        elif self.comboxlist0.get() == "发布临时文字":
            self.translateBtn['text'] = "生成"
            self.comboxlist['state'] = 'readonly'
            self.comboxlist["values"] = "发布临时文字"
            self.comboxlist.current(0)
        else:
            name = self.comboxlist0.get()
            for i in self.dlllist:
                s = create_string_buffer(''.encode(), 9000)  #in dll is 8192
                i.name(s)
                if string_at(s).decode('utf-8') == name:
                    try:
                        self.apithread("i.choose()",i)
                        break
                    except:
                        pass
            # self.translateBtn['text'] = "处理"
            # self.comboxlist['state'] = 'disabled'

    def apiloop(self,arg):
        '''用于处理外部dll的线程函数'''
        self.logger.debug("apiloop call")
        while True:
            time.sleep(0.01)
            try:
                s = create_string_buffer(''.encode(), 8192) #in dll is 8192
                ret = self.maindll.getcmd(s)
                if ret == 1:
                    s = string_at(s).decode('utf-8')
                    exec(s)
            except Exception as e:
                self.logger.debug(str(e))
                self.window.state('normal')
                self.window.wm_attributes('-topmost', 1)
                self.outText.delete("1.0", 'end')
                self.outText.insert(tkinter.END, "出现异常:\n" + str(e))

    def makeOCR(self, image, OCRLANGUAGE):
        '''makeOCR接口
        '''
        self.logger.debug("makeOCR call")
        url = 'http://api.ocr.space/parse/image'
        headers = {
            'Host': 'api.ocr.space',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.102 Safari/537.36 '
        }
        output = BytesIO()
        image.save(output, "PNG")
        image = output.getvalue()
        output.close()
        file_payload = {
            'file': ('goo.jpg', image, 'image/jpge'),
            'url': "",
            'language': OCRLANGUAGE,
            'apikey': self.MK_APIKEY,
            'isOverlayRequired': 'true',
        }
        m = MultipartEncoder(file_payload)
        headers['Content-Type'] = m.content_type
        response = requests.post(url, headers=headers, data=m)
        return response.json()['ParsedResults'][0]['ParsedText']


    def OCRAPI(self, Image):
        '''用于调用OCR
        '''
        self.logger.debug("OCRAPI call")
        if self.comboxlist1.current() == 0:
            return self.baiduOCR(Image)
        else:
            return self.makeOCR(Image, OCRLANGUAGE)

    def on_closing(self):
        self.logger.debug("on_closing call")
        self.window.withdraw()

    def showwin(self,systray):
        self.logger.debug("showwin call")
        self.window.state('normal')
        self.window.wm_attributes('-topmost', 1)
    
    def on_quit_callback(self,systray):
        self.logger.debug("on_quit_callback call")
        self.window.quit()

    def __init__(self):
        '''GUI的初始化
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.info("开始记录日志")
        try:
            self.logger.info("开始检查网络连接")
            # requests.get("https://www.baidu.com", verify=False) # 访问百度以验证网络是否通畅
            # self.logger.info("网络连接成功")
            self.logger.info("开始加载配置文件")
            self.cf = Config()
            self.APP_ID = self.cf.APP_ID
            self.API_KEY = self.cf.API_KEY
            self.SECRET_KEY = self.cf.SECRET_KEY
            self.MK_APIKEY = self.cf.MK_APIKEY

            self.logger.info("开始加载窗体")
            self.window = tk.Tk()
            self.window.title('截图翻译工具(V4.5)')
            self.window.attributes("-alpha", 0.9)
            self.window['background'] = 'PowderBlue'

            self.filename = resource_path(os.path.join("res", "bitbug_favicon.ico"))

            self.window.iconbitmap(self.filename)

            self.window.resizable(0, 0)

            self.menubar = tk.Menu(self.window)

            self.filemenu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label='导入文件', menu=self.filemenu)
            self.filemenu.add_command(label='从文本文件导入', command=self.getFromTXT)
            self.filemenu.add_command(label='从图像文件导入', command=self.getFromImage)

            self.setmenu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label='设置', menu=self.setmenu)
            self.setmenu.add_command(label='查看APP_ID', command=self.getAppId)
            self.setmenu.add_command(label='生成配置文件', command=self.useConfig)

            self.helpmenu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label='帮助', menu=self.helpmenu)
            self.helpmenu.add_command(label='关于', command=self.aboutClick)
            self.helpmenu.add_command(label='更新与反馈', command=self.upClick)

            self.window.config(menu=self.menubar)

            tk.Label(self.window, text="原文:", background='PowderBlue').grid(
                row=0, column=0, sticky=tk.W)

            self.comboxlist0 = ttk.Combobox(self.window)
            self.comboxlist0["values"] = ("使用谷歌翻译", "C/C++代码美化",
                                          "发布临时文字")
            self.comboxlist0.bind("<<ComboboxSelected>>", self.comboxlist0_msg)

            self.comboxlist0["state"] = "readonly"
            self.comboxlist0.current(0)
            self.comboxlist0.grid(row=0, column=0, columnspan=2, padx=38, sticky=tk.W)

            self.comboxlist = ttk.Combobox(self.window)
            self.comboxlist["values"] = ("翻译为中文(简体)", "翻译为中文(繁体)",
                                         "翻译为英文", "翻译为日文", "翻译为韩文")
            self.comboxlist["state"] = "readonly"
            self.comboxlist.current(0)
            self.comboxlist.grid(row=0, column=1, sticky=tk.E)

            self.inputText = tk.Text(self.window, height=12, width=50)
            self.inputText.grid(row=1, column=0, columnspan=2, padx=8, pady=8)

            self.inputTextsection = section()
            self.inputTextsection.s = self.inputText
            self.inputTextmenu = tk.Menu(self.window, tearoff=0)
            self.inputTextmenu.add_command(label="复制", command=self.inputTextsection.onCopy)
            self.inputTextmenu.add_separator()
            self.inputTextmenu.add_command(label="粘贴", command=self.inputTextsection.onPaste)
            self.inputTextmenu.add_separator()
            self.inputTextmenu.add_command(label="剪切", command=self.inputTextsection.onCut)
            self.inputText.bind("<Button-3>", lambda event: self.inputTextmenu.post(event.x_root, event.y_root))


            tk.Label(self.window, text="译文:", background='PowderBlue').grid(
                row=2, column=0, sticky=tk.W)

            self.translateBtn = tk.Button(
                self.window, text="翻译", bg='Lavender', command=self.translateBtnClick)
            self.translateBtn.grid(row=2, column=0, padx=40, sticky=tk.W)

            self.OCRLANGUAGE = 'eng'
            self.comboxlist1 = ttk.Combobox(self.window)
            self.comboxlist1["values"] = ("使用百度OCR", "使用OCRMAKER")
            self.comboxlist1.bind("<<ComboboxSelected>>", self.comboxlist1_OCR)
            self.comboxlist1["state"] = "readonly"
            self.comboxlist1.current(0)
            self.comboxlist1.grid(row=2, column=0, padx=80, columnspan=2, sticky=tk.W)

            self.clearBtn = tk.Button(
                self.window, text="清屏", bg='Lavender', command=self.clearBtnClick)
            self.clearBtn.grid(row=2, column=1, padx=90, sticky=tk.E)

            self.cb1var = tk.IntVar()
            self.cb1var.set(1)
            self.cb1 = tkinter.Checkbutton(
                self.window, text='监听剪切板', background='PowderBlue', variable=self.cb1var)
            self.cb1.grid(row=2, column=0, columnspan=2, sticky=tk.E)

            self.outText = tk.Text(self.window, height=12, width=50)
            self.outText.grid(row=3, column=0, columnspan=2, padx=8, pady=8)

            self.outTextsection = section()
            self.outTextsection.s = self.outText
            self.outTextmenu = tk.Menu(self.window, tearoff=0)
            self.outTextmenu.add_command(label="复制", command=self.outTextsection.onCopy)
            self.outTextmenu.add_separator()
            self.outTextmenu.add_command(label="粘贴", command=self.outTextsection.onPaste)
            self.outTextmenu.add_separator()
            self.outTextmenu.add_command(label="剪切", command=self.outTextsection.onCut)
            self.outText.bind("<Button-3>", lambda event: self.outTextmenu.post(event.x_root, event.y_root))
            # self.window.bind(sequence="<Key>", func=self.outTexeP)

            self.window.state('normal')
            self.window.wm_attributes('-topmost', 1)

            self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.menu_options = (("显示", None, self.showwin),)
            systray = SysTrayIcon(self.filename, "截图翻译工具", self.menu_options, on_quit=self.on_quit_callback)
            systray.start()
            self.logger.info("窗体加载成功")

            self.logger.info("开始加载插件模块")
            self.maindll = WinDLL(resource_path(os.path.join("res", "pymain.dll")))
            dlllist = [i for i in glob.glob(r"*.dll") if i[0]=='p' and i[1] == 'y']
            self.logger.info("搜寻到如下插件{0}" .format(str(dlllist)))
            self.logger.info("开始载入dll")
            self.dlllist = []
            s = create_string_buffer(''.encode(), 8192) #in dll is 8192
            for i in dlllist:
                self.logger.info("正在载入{0}".format(i))
                dll = WinDLL(os.path.join(os.getcwd(), i))
                self.dlllist.append(dll)
                self.logger.info("载入{0}成功".format(i))
                self.logger.info("正在获取{0}的名字".format(i))
                s = create_string_buffer(''.encode(), 9000) #in dll is 8192
                dll.name(s)
                s = string_at(s).decode('utf-8')
                self.logger.info("{0}的名字为:{1}".format(i,s))
                self.comboxlist0["values"] = self.comboxlist0["values"] + (s,)

            self.logger.info("开始启动插件事件监听线程")
            _thread.start_new_thread(self.apiloop, ("",))  # 用于插件的监听
            self.logger.info("插件事件监听线程启动成功")
            self.logger.info("开始启动剪切板事件监听线程")
            _thread.start_new_thread(self.thread_fun, (self.window, self.inputText, self.outText))
            self.logger.info("剪切板事件监听线程启动成功")
            self.logger.info("进入窗体消息循环")
            self.window.mainloop()
        except Exception as e:
            self.logger.error(str(e))
            tk.messagebox.showerror(
                title="致命错误",
                message="请将具体信息发送给开发者:\n网页:https://github.com/super1207/translate\n错误信息:" + str(e))


if __name__ == '__main__':
    if os.path.exists('debug.log'):
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s -%(levelname)s - %(name)s - %(funcName)s - %(lineno)d - %(message)s',filename='debug.log')
    elif os.path.exists('info.log'):
        logging.basicConfig(level = logging.INFO,format = '%(asctime)s -%(levelname)s - %(name)s - %(funcName)s - %(lineno)d - %(message)s',filename='debug.log')
    else:
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s -%(levelname)s - %(name)s - %(funcName)s - %(lineno)d - %(message)s')
    a = GUI()
