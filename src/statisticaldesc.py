"""统计描述模块"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import mplcursors
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class StatDesc:
    def __init__(self, 
                dir_path,
                console,
                user_filename: str = None, 
                vedio_filename: str = None
                ) -> None:
        self.user_filename = user_filename
        self.vedio_filename = vedio_filename
        self.upath = dir_path.joinpath(f"./{user_filename}")
        self.vpath = dir_path.joinpath(f"./{vedio_filename}")
        self.console = console
        self.point_sz = 3

    def run(self) -> None:
        if self.user_filename:
            self.udata_vis()
        if self.vedio_filename:
            self.vdata_vis()

    def udata_vis(self) -> None:
        self.udata_linreg()
        self.udata_dbscn()

    def udata_dbscn(self, eps:float = 0.03, min_samples:int = 40) -> None:
        data = pd.read_excel(self.upath)
        X = data[['粉丝数量', '获赞数量']].values
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        dbscan.fit(X_scaled)
        labels = dbscan.labels_
        fig, ax = plt.subplots()
        scatter = ax.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', s=self.point_sz)
        plt.title('异常账号检测结果')
        plt.xlabel('粉丝数量')
        plt.ylabel('获赞数量')
        cursor = mplcursors.cursor(scatter, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            x, y = sel.target
            label = f"粉丝数量: {x}\n获赞数量: {y}"
            sel.annotation.set_text(label)
        plt.show()

    def udata_linreg(self) -> None:
        df = pd.read_excel(self.upath)
        x_v = np.array(df['粉丝数量']).reshape(-1, 1)
        y_v = np.array(df['获赞数量']).reshape(-1, 1)
        lin_reg = LinearRegression()
        lin_reg.fit(x_v, y_v)
        x_pred = np.linspace(x_v.min(), x_v.max(), 2).reshape(-1, 1)
        y_pred = x_pred * lin_reg.coef_ + lin_reg.intercept_
        plt.scatter(x_v, 
                    y_v, 
                    label="用户数据",
                    s=self.point_sz)
        plt.plot(x_pred, y_pred, 'r--', label=f"权重参数={lin_reg.coef_[0][0]}\n偏置参数={lin_reg.intercept_[0]}")
        plt.xlabel("粉丝数量")
        plt.ylabel("获赞数量")
        plt.title("粉丝数量与获赞数量的线性回归")
        plt.legend()
        plt.show()

    def vdata_vis(self) -> None:
        vdata_df = pd.read_excel(self.vpath)
        x = self.convert_time(vdata_df['视频时长'])
        # 时长与点赞数的关系
        y = vdata_df['点赞数量']
        plt.scatter(x, y, s=self.point_sz)
        plt.xlabel("视频时长（s）")
        plt.ylabel("视频点赞数")
        plt.title("视频时长与视频点赞数的关系")
        plt.show()
        # 时长与评论数的关系
        y = vdata_df['评论数量']
        plt.scatter(x, y, s=self.point_sz)
        plt.xlabel("视频时长（s）")
        plt.ylabel("视频评论数")
        plt.title("视频时长与视频评论数的关系")
        plt.show()

    def convert_time(self, times) -> list:
        res = [times[i].split(':') for i in range(len(times))]
        for i in range(len(res)):
            res[i] = int(res[i][0]) * 3600 + int(res[i][1]) * 60 + int(res[i][2])
        return res