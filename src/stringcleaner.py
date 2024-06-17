"""处理非法字符串"""

from platform import system
from string import whitespace
from time import time

from emoji import replace_emoji

from src.customizer import illegal_nickname

__all__ = ['Cleaner']


class Cleaner:
    def __init__(self):
        """
        替换字符串中包含的非法字符，默认根据系统类型生成对应的非法字符字典，也可以自行设置非法字符字典
        """
        self.rule = self.default_rule()  # 默认非法字符字典

    @staticmethod
    def default_rule():
        """根据系统类型生成默认非法字符字典"""
        if (s := system()) in ("Windows", "Darwin"):
            rule = {
                "/": "",
                "\\": "",
                "|": "",
                "<": "",
                ">": "",
                "\"": "",
                "?": "",
                ":": "",
                "*": "",
                "\x00": "",
            }  # Windows 系统和 Mac 系统
        elif s == "Linux":
            rule = {
                "/": "",
                "\x00": "",
            }  # Linux 系统
        else:
            print("不受支持的操作系统类型，可能无法正常去除非法字符！")
            rule = {}
        cache = {i: "" for i in whitespace[1:]}  # 补充换行符等非法字符
        return rule | cache

    def filter(self, text: str) -> str:
        """
        去除非法字符

        :param text: 待处理的字符串
        :return: 替换后的字符串，如果替换后字符串为空，则返回 None
        """
        for i in self.rule:
            text = text.replace(i, self.rule[i])
        return text

    def filter_name(
            self,
            text: str,
            inquire=True,
            default: str = "") -> str:
        """过滤文件夹名称中的非法字符"""
        text = self.filter(text)

        text = replace_emoji(text)

        text = text.strip().strip(".")

        return (text or illegal_nickname() or default or str(
            time())[:10]) if inquire else (text or default)

    @staticmethod
    def clear_spaces(string: str):
        """将连续的空格转换为单个空格"""
        return " ".join(string.split())
