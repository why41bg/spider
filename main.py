"""主程序入口"""

from pathlib import Path
from shutil import rmtree
from threading import Thread
from rich.console import Console
from time import sleep

from src.customizer import (GENERAL, PROMPT, COOKIE_UPDATE_INTERVAL)
from src.parseck import Cookie
from src.configuration import Settings
from src.configuration import Parameter
from src.parameter import Headers
from src.parameter import NewXBogus
from src.maincomplete import TikTok
from src.maincomplete import prompt
from src.dataanalysis import DataAnalysis
from src.vis import vis


def start_cookie_task(function):
    def inner(self, *args, **kwargs):
        if not self.task:
            self.periodic_tasks()
            self.task = True
        return function(self, *args, **kwargs)

    return inner


class RichConsole(Console):
    def print(self, *args, style=GENERAL, highlight=False, **kwargs):
        super().print(*args, style=style, highlight=highlight, **kwargs)

    def input(self, prompt="", *args, **kwargs):
        return super().input(f"[{PROMPT}]{prompt}[/{PROMPT}]", *args, **kwargs)


class TikTokSpider:
    PROJECT_ROOT = Path(__file__).resolve().parent  # 获取项目根目录

    # print(PROJECT_ROOT)  # debug

    def __init__(self):
        self.console = RichConsole()  # 自定义终端
        self.settings = Settings(self.PROJECT_ROOT, self.console)  # 在本目录下生成配置文件
        self.user_agent, self.ua_code = Headers.generate_user_agent()  # 从UA池中随便生成UA
        self.x_bogus = NewXBogus()  # 生成X_B参数
        self.cookie = Cookie(self.settings, self.console)
        self.parameter = None
        self.running = True  # 运行状态
        self.task = False

    def check_config(self):
        """检查配置文件"""
        folder = ("./src/config", "./cache", "./cache/temp")
        for i in folder:
            self.PROJECT_ROOT.joinpath(i).mkdir(exist_ok=True)

    def main_menu(self):
        while self.running:
            defaultMode = prompt(
                "Main Shell",
                ("手动设置Cookie",
                 "启动抖音爬虫程序",
                 "启动数据分析程序",
                 "数据可视化展示"),
                self.console, )
            self.compatible(defaultMode)

    def write_cookie(self):
        """写入cookie"""
        self.cookie.run()
        self.check_settings()
        self.parameter.update_cookie()

    @start_cookie_task
    def complete(self):
        """爬虫启动"""
        example = TikTok(self.parameter)
        example.run()
        self.running = example.running  # 状态绑定

    def data_analysis(self):
        example = DataAnalysis(self.PROJECT_ROOT, self.console)  # 数据分析大师
        example.run()
        self.running = example.running  # 状态绑定

    def compatible(self, mode: str):
        if mode in {"Q", "q", ""}:
            self.running = False  # kill shell
        elif mode == "1":
            self.write_cookie()
        elif mode == "2":
            self.complete()
        elif mode == "3":
            self.data_analysis()
        elif mode == "4":
            example = vis()
            example.run()

    def check_settings(self):
        self.parameter = Parameter(
            self.settings,
            self.cookie,
            main_path=self.PROJECT_ROOT,
            user_agent=self.user_agent,
            ua_code=self.ua_code,
            xb=self.x_bogus,
            console=self.console,
            **self.settings.read(),
        )

    def run(self):
        # shell启动前例行检查
        self.check_settings()
        # 启动shell
        self.main_menu()
        self.console.print("程序结束运行")

    def delete_temp(self):
        rmtree(self.PROJECT_ROOT.joinpath("./cache/temp").resolve())

    def periodic_update_cookie(self):
        while True:
            self.parameter.update_cookie()
            sleep(COOKIE_UPDATE_INTERVAL)

    def periodic_tasks(self):
        thread = Thread(target=self.periodic_update_cookie, daemon=True)
        thread.start()


if __name__ == '__main__':
    TikTokSpider().run()
