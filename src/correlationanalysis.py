"""相关性分析模块"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression

from src.customizer import (
    INFO, 
    ERROR
)


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
THRESHOLDS = 0.7  # 阈值


class CorrelationAnalysis:

    def __init__(self, 
                console,
                filepath,
                x: str, 
                y: str) -> None:
        self.x = x  # 自变量名称
        self.y = y  # 因变量名称
        self.console = console
        self.filepath = filepath  # 文件路径
        self.xv = None
        self.yv = None
        self.point_sz = 3

    def run(self) -> None:
        self.work()

    def work(self) -> None:
        try:
            df = pd.read_excel(self.filepath)
        except:
            self.console.print(f"文件{self.filepath}不存在", style=ERROR)
            return
        try:
            x = np.array(df[self.x]).reshape(-1, 1)  # m*1
            self.xv = x
        except:
            self.console.print(f"变量{self.x}不存在", style=ERROR)
            return
        try:
            y = np.array(df[self.y]).reshape(-1, 1)  # m*1
            self.yv = y
        except:
            self.console.print(f"变量{self.y}不存在", style=ERROR)
            return
        x_mean = int(x.mean())
        y_mean = int(y.mean())
        x -= x_mean
        y -= y_mean
        ppmcc = np.sum(x * y) / (np.sqrt(np.dot(x.T, x)) * np.sqrt(np.dot(y.T, y)))[0][0]
        self.console.print(f'变量"{self.x}"与变量"{self.y}"之间的ppmcc值为：{ppmcc}', style=INFO)
        self.vis(ppmcc)

    def vis(self, ppmcc) -> None:
        if ppmcc < THRESHOLDS:
            return
        if self.console.input("当前两个变量存在强相关关系，是否进行回归？(YES/NO)：").upper() == "YES":
            lin_reg = LinearRegression()
            lin_reg.fit(self.xv, self.yv)
            x_pred = np.linspace(self.xv.min(), self.xv.max(), 2).reshape(2, 1)
            y_pred = x_pred * lin_reg.coef_ + lin_reg.intercept_
            plt.scatter(self.xv, 
                        self.yv, 
                        label='用户数据', 
                        s=self.point_sz)
            plt.plot(x_pred, y_pred, 'r--', label=f"权重参数={lin_reg.coef_[0][0]}\n偏置参数={lin_reg.intercept_[0]}")
            plt.xlabel(self.x)
            plt.ylabel(self.y)
            plt.title(f"{self.x}与{self.y}的线性回归")
            plt.legend()
            plt.show()



            