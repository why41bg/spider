"""数据预处理模块"""

import pandas as pd

from src.customizer import (
    INFO,
    ERROR
)

__all__ = [
    "UserDataFilter",
    "VedioDataFilter"
]

class UserDataFilter:
    def __init__(self, filename, console, dir_path) -> None:
        self.filename = filename
        self.console = console
        self.dir_path = dir_path
        self.success = True

    def filter(self) -> None:
        file_path = self.dir_path.joinpath(self.filename)
        try:
            user_df = pd.read_excel(file_path)
        except:
            self.console.print(f"路径出错：{file_path}", style=ERROR)
            self.success = False
            return
        user_df_filter = user_df[user_df["粉丝数量"] > 10000]
        save_path = self.generate_save_path()
        if user_df_filter.to_excel(save_path, index=False):
            self.console.print("保存用户文件失败", style=ERROR)
            self.success = False
            return
        self.console.print(f"用户文件已保存至 {save_path}", style=INFO)

    def generate_save_path(self):
        return self.dir_path.joinpath("./user_data_proced.xlsx")

    def run(self) -> bool:
        self.filter()
        return self.success


class VedioDataFilter:
    def __init__(self, filename, console, dir_path) -> None:
        self.filename = filename
        self.console = console
        self.dir_path = dir_path
        self.success = True

    def filter(self) -> None:
        file_path = self.dir_path.joinpath(self.filename)
        try:
            vedio_df = pd.read_excel(file_path)
        except:
            self.console.print(f"路径出错：{file_path}", style=ERROR)
            self.success = False
            return
        vedio_df_filter = vedio_df[vedio_df["点赞数量"] > 1000]
        save_path = self.generate_save_path()
        if vedio_df_filter.to_excel(save_path, index=False):
            self.console.print("保存视频文件失败", style=ERROR)
            self.success = False
            return
        self.console.print(f"视频文件已保存至 {save_path}", style=INFO)
        
    def generate_save_path(self):
        return self.dir_path.joinpath("./vedio_data_proced.xlsx")

    def run(self) -> bool:
        self.filter()
        return self.success