"""炒饭蜘蛛侠控制台模块"""

from datetime import datetime

from src.customizer import (
    WARNING,
    INFO
)
from src.dataacquirer import (
    Search,
    Link,
    Comment,
)

from src.dataextractor import Extractor
from src.recorder import RecordManager


__all__ = [
    "prompt",
    "TikTok",
]


def prompt(
        title: str,
        choose: tuple | list,
        console,
        separate=None) -> str:
    screen = f"{title}:\n"
    row = 0
    for i, j in enumerate(choose):
        screen += f"{i + 1}. {j}\n"
        if separate and row in separate:
            screen += f"{'=' * 25}\n"
        row += 1
    return console.input(screen+"$ ")


def check_storage_format(function):
    def inner(self, *args, **kwargs):
        if self.parameter.storage_format:
            return function(self, *args, **kwargs)
        self.console.print(
            "未设置 storage_format 参数",
            style=WARNING)
    return inner

class TikTok:
    SEARCH = {
        "type": {
            "综合": 0,
            "视频": 1,
            "用户": 2,
            "0": 0,
            "1": 1,
            "2": 2,
        },
        "type_text": {
            0: "综合搜索",
            1: "视频搜索",
            2: "用户搜索",
        },
        "sort": {
            "综合排序": 0,
            "最新发布": 1,
            "最多点赞": 2,
            "0": 0,
            "1": 1,
            "2": 2,
        },
        "sort_text": {
            0: "综合排序",
            1: "最新发布",
            2: "最多点赞",
        },
        "publish_text": {
            0: "不限",
            1: "一天内",
            7: "一周内",
            182: "半年内",
        },
    }
    DATA_TYPE = {
        0: "works",
        1: "works",
        2: "search_user",
    }

    def __init__(self, parameter):
        self.parameter = parameter
        self.console = parameter.console 
        self.links = Link()
        self.extractor = Extractor(parameter)  # 数据存储模块
        self.storage = bool(parameter.storage_format)
        self.record = RecordManager()
        self.settings = parameter.settings
        self.running = True  # 状态控制

    def run(self):
        while self.running:
            select = prompt(
                "请选择抖音爬虫的功能",
                ("采集用户数据",
                 "采集视频数据",
                 "手动采集评论数据",
                 "自动采集评论数据",
                 "备用搜索接口"),
                self.console)
            if select in {"Q", "q"}:
                self.running = False
            elif not select:
                break
            elif select == "1":
                self.search_interactive(mode="1")  # 搜索用户模式
            elif select == "2":
                self.search_interactive(mode="2")  # 搜索视频模式
            elif select == "3":
                self.comment_interactive()
            elif select == "4":
                self.comment_auto()
            elif select == "5":
                self.search_interactive()  # 默认搜索模式

    @check_storage_format
    def search_interactive(self, mode: str = "0"):
        while all(c := self._enter_search_criteria(mode=mode)):
            self._deal_search_data(*c)

    @check_storage_format
    def comment_interactive(self, ids: list = None):
        root, params, logger = self.record.run(self.parameter, type_="comment")
        if not ids:
            while url := self._inquire_input("作品"):
                ids = self.links.works(url)
                if bool(ids):
                    break
        if ids:
            for i in ids:
                name = f"作品{i}_评论数据"
                with logger(root, name=name, **params) as record:
                    Comment(self.parameter, i).run(self.extractor, record)

    @check_storage_format
    def comment_auto(self):
        while all(c := self._enter_search_comment_criteria()):
            self._deal_search_data(source=True, *c)

    def _enter_search_comment_criteria(self) -> None | tuple[list, str]:
        text = self._inquire_input(tip="请输入搜索视频类型关键词\n$ ")
        return self._verify_search_criteria(keyword=text, type_="1", pages="3", sort="2", publish="0")

    def _enter_search_criteria(self, text: str = None, mode: str = "0") -> None | tuple[list, str]:
        if not text:
            if mode == "1":  # 搜索用户数据
                text = self._inquire_input(tip="请输入用户搜索关键词\n$ ")
                return self._verify_search_criteria(keyword=text, type_="2", pages="50")
            elif mode == "2":  # 搜索视频数据
                text = self._inquire_input(tip="请输入视频搜索关键词\n$ ")
                return self._verify_search_criteria(keyword=text, type_="1", pages="50")
            else:  # 默认通道
                text = self._inquire_input(tip="- 关键词：搜索的关键词\n- 搜索类型：0->综合 1->视频 2->用户\n- 页数：搜索结果页数\n- 排序方式：0->综合排序 1->最新发布 2->最多点赞\n$ ")
                # 空格分割字符串
                text = text.split()
                # 空白参数使用空字符串补齐
                while 0 < len(text) < 5:
                    text.append("0")
                return self._verify_search_criteria(*text)

    def _inquire_input(self, url: str = None, tip: str = None) -> str:
        text = self.console.input(tip or f"请输入{url}链接\n$ ")
        if not text:
            return ""
        elif text in ("Q", "q", ""):
            self.running = False
            return ""
        return text

    def _verify_search_criteria(
            self,
            keyword: str = None,
            type_: str = None,
            pages: str = None,
            sort: str = None,
            publish: str = None) -> tuple:
        if not keyword:
            return (None,)
        type_ = self.SEARCH["type"].get(type_, 0)  # 搜索方式，默认综合搜索
        type_text = self.SEARCH["type_text"][type_] 
        pages = self._extract_integer(pages)  # 页面数量
        sort = self.SEARCH["sort"].get(sort, 0)  # 排序方式，默认综合排序
        sort_text = self.SEARCH["sort_text"][sort]
        publish = int(publish) if publish in {"0", "1", "7", "182"} else 0  # 默认不限
        publish_text = self.SEARCH["publish_text"][publish]
        return keyword, (type_, type_text), pages, (sort, sort_text), (publish, publish_text)

    @staticmethod
    def _extract_integer(page: str) -> int:
        """尝试将字符串转换为整数，如果转换成功，则返回比较大的数"""
        try:
            return max(int(page), 1)
        except ValueError:
            return 1

    @staticmethod
    def _generate_search_name(
            keyword: str,
            type_: str,
            sort: str = None,
            publish: str = None) -> str:
        """根据搜索参数生成本地保存文件名"""
        format_ = (
            datetime.now().strftime("%Y-%m-%d %H.%M.%S"),
            type_,
            keyword,
            sort,
            publish)
        if all(format_):
            return "_".join(format_)
        elif all(format_[:3]):
            return "_".join(format_[:3])
        raise ValueError

    def _deal_search_data(
            self,
            keyword: str,  # 关键词
            type_: tuple,  # 搜索类型
            pages: int,  # 搜索页数
            sort: tuple,  # 排序规则
            publish: tuple,  # 时间筛选
            source=False):
        search_data = Search(self.parameter, keyword, type_[0], pages, sort[0], publish[0]).run()
        if not any(search_data):
            self.console.print("采集搜索数据失败")  # debug
            return None
        if source:  # 根据视频id号提取评论
            ids = [data['aweme_info']['aweme_id'] for data in search_data]
            self.comment_interactive(ids=ids)
        # 保存到本地
        name = self._generate_search_name(keyword, type_[1], sort[1], publish[1])
        root, params, logger = self.record.run(self.parameter, type_=self.DATA_TYPE[type_[0]])
        with logger(root, name=name, **params) as logger:
            search_data = self.extractor.run(search_data, logger, type_="search", tab=type_[0])
        self.console.print(f"数据采集成功，已成功保存到本地，文件名为：\n{name}", style=INFO)
        return search_data





