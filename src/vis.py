"""可视化模块"""

from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import pandas as pd

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class vis:
    def __init__(self):
        return

    def run(self):
        self.histogram()
        self.pie_chart()
        self.cal_score_1()
        self.cal_score_2()
        self.cal_score_all()
        self.word_cloud()

    @staticmethod
    def histogram():
        # 数据
        categories = ['0-100', '100-500', '500-1000', '1000-2500', '2500-5000', '5000-10000', '10000以上']
        values = [25, 190, 602, 1541, 1227, 847, 593]

        # 绘制柱状图
        plt.bar(categories, values, color='red')

        # 设置标题和标签
        plt.title('游戏区点赞数分布情况（万）')
        plt.xlabel('区间')
        plt.ylabel('点赞数')

        # 显示图形
        plt.show()

    @staticmethod
    def pie_chart():
        filenames = ['2023-12-19 12.04.52_视频搜索_瓦洛兰特_综合排序_不限.xlsx',
                     '2023-12-19 14.28.48_视频搜索_英雄联盟_综合排序_不限.xlsx',
                     '2023-12-19 14.45.21_视频搜索_王者荣耀_综合排序_不限.xlsx']
        gamenames = ['瓦洛兰特', '英雄联盟', '王者荣誉']
        for i in range(3):
            ori_df = pd.read_excel(f"data/{filenames[i]}")
            video_counts = ori_df['视频类型'].value_counts()
            labels = ['精彩高燃解说类', '技巧妙招策略类', '搞笑奇怪逗乐类', '热点桥段模仿类', '愉悦特效混剪类',
                      '周边资讯盘点类']
            sizes = [video_counts[i] for i in range(1, 7)]
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
            max_index = sizes.index(max(sizes))
            explode = [0.1 if i == max_index else 0 for i in range(len(sizes))]
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.legend(labels, loc='best')
            plt.title(f'{gamenames[i]}--视频类型分布')
            plt.axis('equal')
            plt.show()

    @staticmethod
    def cal_score_1():
        # 数据
        categories = ['精彩解说高燃类', '技巧妙招策略类', '搞笑奇怪逗乐类', '热点桥段模仿类', '愉悦特效混剪类',
                      '周边咨询判盘点类']
        values = [29896.35, 14887.63, 43621.83, 33641.51, 44358.01, 18391.1]
        colors = ['#DC143C', '#FFD700', '#00BFFF', '#008000', '#4169E1', '#48D1CC']

        # 绘制柱状图
        bars = plt.bar(categories, values, color=colors)

        # 在每个柱形上显示具体的值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height / 2, str(height), ha='center', va='center')

        # 设置标题和标签
        plt.title('Moba类综合互动指数')
        plt.xlabel('类别')
        plt.ylabel('指数')

        # 显示图形
        plt.show()

    @staticmethod
    def cal_score_2():
        # 数据
        categories = ['精彩解说高燃类', '技巧妙招策略类', '搞笑奇怪逗乐类', '热点桥段模仿类', '愉悦特效混剪类',
                      '周边咨询判盘点类']
        values = [9421.34, 10734.29, 13903.74, 18054.52, 3567.43, 6484.97]
        colors = ['#DC143C', '#FFD700', '#00BFFF', '#008000', '#4169E1', '#48D1CC']

        # 绘制柱状图
        bars = plt.bar(categories, values, color=colors)

        # 在每个柱形上显示具体的值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height / 2, str(height), ha='center', va='center')

        # 设置标题和标签
        plt.title('FPS类综合互动指数')
        plt.xlabel('类别')
        plt.ylabel('指数')

        # 显示图形
        plt.show()

    @staticmethod
    def cal_score_all():
        # 数据
        categories = ['精彩解说高燃类', '技巧妙招策略类', '搞笑奇怪逗乐类', '热点桥段模仿类', '愉悦特效混剪类',
                      '周边咨询判盘点类']
        values = [9924.44, 9586.29, 13903.74, 15260.52, 4051.4, 6725.97]
        colors = ['#DC143C', '#FFD700', '#00BFFF', '#008000', '#4169E1', '#48D1CC']

        # 绘制柱状图
        bars = plt.bar(categories, values, color=colors)

        # 在每个柱形上显示具体的值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height / 2, str(height), ha='center', va='center')

        # 设置标题和标签
        plt.title('所有游戏类型综合互动指数')
        plt.xlabel('类别')
        plt.ylabel('指数')

        # 显示图形
        plt.show()

    @staticmethod
    def word_cloud():
        image_path = 'other/word_cloud.png'
        img = mpimg.imread(image_path)
        plt.imshow(img)
        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    vis.word_cloud()
