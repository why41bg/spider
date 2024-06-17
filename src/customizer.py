"""自定义参数"""

from random import randint
from time import sleep


# 彩色交互提示颜色设置，支持标准颜色名称、Hex、RGB 格式
PROMPT = "b turquoise2"  # 蓝色
GENERAL = "b bright_white" 
ERROR = "b bright_red"
WARNING = "b bright_yellow"
INFO = "b bright_green"

# Cookie 更新间隔，单位：秒
COOKIE_UPDATE_INTERVAL = 15 * 60

def wait():
    """
    设置网络请求间隔时间
    """
    # 随机延时
    sleep(randint(15, 35) * 0.1)
    # 固定延时
    # sleep(2)
    # 取消延时
    # pass

def illegal_nickname():
    return input("非法文件夹名称，请输入临时的账号标识：")
