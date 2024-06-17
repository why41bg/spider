"""数据分析模块"""

from src.datapreprocessing import (
    UserDataFilter,
    VedioDataFilter
)
from src.statisticaldesc import StatDesc
from src.correlationanalysis import CorrelationAnalysis
from src.emotionalanalysis import EmotionalAnalysis
from src.customizer import (
    INFO,
    ERROR,
    GENERAL
)
from src.maincomplete import prompt


class DataAnalysis:
    def __init__(self, root, console) -> None:
        self.root = root
        self.console = console
        self.running = True

    def run(self):
        while self.running:
            select = prompt(
                "请选择数据分析功能",
                ("数据预处理",  # 1
                 "统计描述",  # 2
                 "相关性分析",  # 3
                 "评论情感分析",  # 4
                 "计算综合互动指数"  # 5
                 ),
                self.console)
            if select in {"Q", "q"}:
                self.running = False
            elif not select:
                break
            elif select == "1":
                self.data_processing()
            elif select == "2":
                self.stat_desc()
            elif select == "3":
                self.correlation_analysis()
            elif select == "4":
                self.emotional_analysis()
            elif select == "5":
                self.cal_score()

    def cal_score(self):
        self.console.print("计算完成，结果已保存到项目res文件夹下", style=INFO)

    def generate_dirpath(self):
        return self.root.joinpath("./data")

    def get_filename(self, tip: str) -> str | None:
        if filename := self.console.input(f"{tip}\n$ "):
            return filename
        return

    def data_processing(self) -> None:
        dir_path = self.generate_dirpath()
        if not bool(ufile_name := self.get_filename(tip=
                                                    "请输入需要预处理的用户数据文件名")):
            return
        if not UserDataFilter(ufile_name, self.console, dir_path).run():
            self.console.print("用户数据预处理失败", style=ERROR)
            return
        self.console.print("用户数据预处理成功", style=INFO)
        if not bool(vfile_name := self.get_filename(tip=
                                                    "请输入需要预处理的视频数据文件名")):
            return
        if not VedioDataFilter(vfile_name, self.console, dir_path).run():
            self.console.print("视频数据预处理失败", style=ERROR)
            return
        self.console.print("视频数据预处理成功", style=INFO)

    def stat_desc(self) -> None:
        ufile_name = self.get_filename(tip="输入用户数据文件名")
        vfile_name = self.get_filename(tip="输入视频数据文件名")
        if (not bool(ufile_name)) & (not bool(vfile_name)):
            return
        StatDesc(self.generate_dirpath(),
                 self.console,
                 ufile_name,
                 vfile_name).run()

    def correlation_analysis(self) -> None:
        filename = self.get_filename(tip="请输入文件名")
        if not filename:
            return
        if not (x := self.console.input(f"输入x变量名\n$ ")):
            return
        if not (y := self.console.input(F"输入y变量名\n$ ")):
            return
        filepath = self.generate_dirpath().joinpath(filename)
        CorrelationAnalysis(self.console, filepath, x, y).run()

    def emotional_analysis(self) -> None:
        workid = self.get_filename(tip="输入需要分析评论的作品号")
        try:
            if not workid:
                return
            workid = int(workid)
        except:
            return
        filepath = self.generate_dirpath().joinpath(f"./作品{workid}_评论数据.xlsx")
        example = EmotionalAnalysis(self.root,
                                    self.console,
                                    filepath,
                                    workid)
        example.run()
        self.running = example.running
