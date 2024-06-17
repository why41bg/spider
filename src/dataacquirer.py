from itertools import cycle
from re import compile
from types import SimpleNamespace
from urllib.parse import quote
from requests import exceptions
from requests import request

from src.configuration import Parameter
from src.customizer import (
    WARNING,
)
from src.customizer import wait
from src.dataextractor import Extractor


__all__ = [
    "retry",
    "Search",
]


def retry(function):
    def inner(self, *args, **kwargs):
        finished = kwargs.pop("finished", False)
        output = kwargs.pop("output", True)
        for i in range(self.max_retry):
            if result := function(self, *args, **kwargs):
                return result
            if output:
                self.console.print(f"正在尝试第 {i + 1} 次重试！", style=WARNING)
        if not (result := function(self, *args, **kwargs)) and finished:
            self.finished = True
        return result
    return inner


class Acquirer:
    Phone_headers = {
        'User-Agent': 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)'
                      '+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'}

    def __init__(self, params: Parameter):
        self.PC_headers, self.black_headers = self.init_headers(params.headers)
        self.ua_code = params.ua_code
        self.xb = params.xb
        self.console = params.console
        self.max_retry = params.max_retry  # 最大重试次数
        self.timeout = params.timeout
        self.cursor = 0  # 记录请求游标位置
        self.response = []  # 存储请求结果
        self.finished = False  # 标记请求状态

    @staticmethod
    def init_headers(headers: dict) -> tuple:
        return (headers | {
            "Referer": "https://www.douyin.com/", },
            {"User-Agent": headers["User-Agent"]})

    @retry
    def send_request(
            self,
            url: str,
            params=None,
            method='get',
            headers=None,
            **kwargs) -> dict | bool:
        try:
            response = request(
                method,
                url,
                params=params,
                timeout=self.timeout,
                headers=headers or self.PC_headers, **kwargs)
            wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            return False
        except exceptions.ReadTimeout:
            return False
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            return False

    def deal_url_params(self, params: dict, version=23):
        xb = self.xb.get_x_bogus(params, self.ua_code, version)
        params["X-Bogus"] = xb

    def deal_item_data(
            self,
            data: list[dict],
            start: int = None,
            end: int = None):
        for i in data[start:end]:
            self.response.append(i)


class Search(Acquirer):
    search_params = (
        SimpleNamespace(  # 综合搜索
            api="https://www.douyin.com/aweme/v1/web/general/search/single/",
            count=15,
            channel="aweme_general",
            type="general",
        ),
        SimpleNamespace(  # 视频搜索
            api="https://www.douyin.com/aweme/v1/web/search/item/",
            count=20,
            channel="aweme_video_web",
            type="video",
        ),
        SimpleNamespace(  # 用户搜索
            api="https://www.douyin.com/aweme/v1/web/discover/search/",
            count=20,
            channel="aweme_user_web",
            type="user",
        ),
    )

    def __init__(
            self,
            params: Parameter,
            keyword: str,
            tab=0,  # 搜索类型
            page=1,
            sort_type=0,
            publish_time=0):
        super().__init__(params)
        self.keyword = keyword
        self.tab = tab
        self.page = page
        self.sort_type = sort_type
        self.publish_time = publish_time

    def run(self):
        data = self.search_params[self.tab]
        self.PC_headers["Referer"] = (
            f"https://www.douyin.com/search/{
                quote(self.keyword)}?" f"source=switch_tab&type={data.type}"
            )
        if self.tab in {2, 3}:
            deal = self._run_user_live
        elif self.tab in {0, 1}:
            deal = self._run_general
        else:
            raise ValueError
        while not self.finished and self.page > 0:
            deal(data, self.tab)
            self.page -= 1
        return self.response

    def _run_user_live(self, data: SimpleNamespace, type_: int):
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "search_channel": data.channel,
            "keyword": self.keyword,
            "search_source": "switch_tab",
            "query_correct_type": "1",
            "is_filter_search": "0",
            "offset": self.cursor,
            "count": data.count,
            "pc_client_type": "1",
            "version_code": "170400",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "7.7",
        }
        self.deal_url_params(params, 174 if self.cursor else 23)
        self._get_search_data(
            data.api,
            params,
            "user_list" if type_ == 2 else "data")  # 返回json中关键信息键值

    def _run_general(self, data: SimpleNamespace, *args):
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "search_channel": data.channel,
            "sort_type": self.sort_type,
            "publish_time": self.publish_time,
            "keyword": self.keyword,
            "search_source": "switch_tab",
            "query_correct_type": "1",
            "is_filter_search": {True: 1, False: 0}[any((self.sort_type, self.publish_time))],
            "offset": self.cursor,
            "count": data.count,
            "pc_client_type": "1",
            "version_code": "170400",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "7.7",
        }
        self.deal_url_params(params, 174 if self.cursor else 23)
        self._get_search_data(data.api, params, "data")

    def _get_search_data(self, api: str, params: dict, key: str):
        if not (
                data := self.send_request(
                    api,
                    params=params,
                    finished=True,
                )):
            return
        try:
            self.deal_item_data(data[key])
            self.cursor = data['cursor']
        except KeyError:
            self.finished = True


class Link:
    # 抖音链接
    works_link = compile(r".*?https://www\.douyin\.com/(?:video|note)/([0-9]{19}).*?")  # 作品链接

    def __init__(self):
        pass

    def works(self, text: str) -> tuple:
        if u := self.works_link.findall(text):
            return u
        return []


class Comment(Acquirer):
    comment_api = "https://www.douyin.com/aweme/v1/web/comment/list/"  # 评论API
    comment_api_reply = "https://www.douyin.com/aweme/v1/web/comment/list/reply/"  # 评论回复API
    cycle = cycle(("-", "\\", "|", "/"))

    def __init__(self, params: Parameter, item_id: str, pages: int = None):
        super().__init__(params)
        self.item_id = item_id
        self.pages = pages or params.max_pages
        self.all_data = None
        self.reply_ids = None

    def run(self, extractor: Extractor, recorder, source=False) -> list[dict]:
        num = 1
        while not self.finished and self.pages > 0:
            self.console.print(f"正在获取第 {num} 页数据...")
            self.get_comments_data(self.comment_api)
            self.pages -= 1
            num += 1
        self.all_data, self.reply_ids = extractor.run(
            self.response, recorder, "comment", source=source)
        self.response = []
        for i in self.reply_ids:
            self.finished = False
            self.cursor = 0
            while not self.finished and self.pages > 0:
                self.console.print(f"{next(self.cycle)} 正在获取评论回复数据...")
                self.get_comments_data(self.comment_api_reply, i)
                self.pages -= 1
        self.all_data.extend(
            self._check_reply_ids(
                *
                extractor.run(
                    self.response,
                    recorder,
                    "comment",
                    source=source)))
        return self.all_data

    def get_comments_data(self, api: str, reply=""):
        if reply:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "item_id": self.item_id,
                "comment_id": reply,
                "cursor": self.cursor,
                "count": "10" if self.cursor else "3",  # 每次返回数据的数量
                "version_code": "170400",
                "cookie_enabled": "true",
                "platform": "PC",
                "downlink": "10",
            }
            self.deal_url_params(params, 174)
        else:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "aweme_id": self.item_id,
                "cursor": self.cursor,
                "count": "20",
                "version_code": "170400",
                "cookie_enabled": "true",
                "platform": "PC",
                "downlink": "10",
            }
            self.deal_url_params(params)
        if not (
                data := self.send_request(
                    api,
                    params=params,
                    finished=True)):
            return
        try:
            if not (c := data["comments"]):
                raise KeyError
            self.deal_item_data(c)
            self.cursor = data["cursor"]
            self.finished = not data["has_more"]
        except KeyError:
            self.finished = True

    @staticmethod
    def _check_reply_ids(data: list[dict], ids: list) -> list[dict]:
        if ids:
            raise ValueError
        return data