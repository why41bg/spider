"""配置文件处理程序"""

from json import dump
from json import load
from json.decoder import JSONDecodeError
from pathlib import Path
from time import localtime, strftime
from types import SimpleNamespace

from src.customizer import INFO, ERROR
from src.parameter import TtWid
from src.parseck import Register
from src.stringcleaner import Cleaner


class Settings:
    def __init__(self, root, console):
        self.file = root.joinpath("./settings.json")  # 配置文件路径
        self.console = console
        self.__default = {
            "root": "",
            "date_format": "%Y-%m-%d",
            "storage_format": "xlsx",
            "cookie": "",
            "chunk": 512 * 1024,  # 每次从服务器接收的数据块大小
            "max_retry": 5,  # 重试最大次数
            "max_pages": 10,  # 采集评论时控制最大页数，0为不限制
            "default_mode": 0,
            "api_key": "",
            "secret_key": ""
        }  # 默认配置

    def __create(self) -> dict:
        """创建默认配置文件"""
        with self.file.open("w", encoding="UTF-8") as f:
            dump(self.__default, f, indent=4, ensure_ascii=False)
        self.console.print(
            "创建默认配置文件 settings.json 成功！")
        return self.__default

    def read(self) -> dict:
        """读取配置文件，如果没有配置文件，则生成配置文件"""
        try:
            if self.file.exists():
                with self.file.open("r", encoding="UTF-8") as f:
                    return self.__check(load(f))
            return self.__create()
        except JSONDecodeError:
            self.console.print(
                "配置文件 settings.json 格式错误", style=ERROR)
            return self.__default  # 读取配置文件发生错误时返回空配置

    def __check(self, data: dict) -> dict:
        if set(self.__default.keys()).issubset(set(data.keys())):
            return data
        if self.console.input(f"[{ERROR}]配置文件 settings.json 缺少必要的参数，是否需要生成默认配置文件(YES/NO): [/{ERROR}]").upper() == "YES":
            self.__create()
        self.console.print("本次运行将会使用各项参数默认值")
        return self.__default

    def update(self, settings: dict | SimpleNamespace):
        """更新配置文件"""
        with self.file.open("w", encoding="UTF-8") as f:
            dump(
                settings if isinstance(
                    settings,
                    dict) else vars(settings),
                f,
                indent=4,
                ensure_ascii=False)
        self.console.print("保存配置成功！", style=INFO)


class Parameter:
    name_keys = (
        "id",
        "desc",
        "create_time",
        "nickname",
        "uid",
        "mark",
        "type",
    )
    cleaner = Cleaner()

    def __init__(
            self,
            settings,
            cookie_object,
            main_path: Path,
            user_agent: str,
            ua_code: tuple,
            xb,
            console,
            cookie: dict | str,
            root: str,
            date_format: str,
            storage_format: str,
            # chunk: int,
            max_retry: int,
            max_pages: int,
            default_mode: int,
            timeout=10,
            **kwargs,
    ):
        self.settings = settings
        self.cookie_object = cookie_object
        self.main_path = main_path  # 项目根路径
        self.temp = main_path.joinpath("./cache/temp")  # 缓存路径
        self.headers = {
            "User-Agent": user_agent,
        }
        self.ua_code = ua_code
        self.xb = xb
        self.console = console
        self.cookie_cache = None
        self.cookie = self.check_cookie(cookie)
        self.root = self.check_root(root)
        self.date_format = self.check_date_format(date_format)
        self.storage_format = self.check_storage_format(storage_format)  # 采集数据持久化存储格式
        # self.chunk = self.check_chunk(chunk)
        self.max_retry = self.check_max_retry(max_retry)
        self.max_pages = self.check_max_pages(max_pages)
        self.timeout = self.check_timeout(timeout)
        self.default_mode = self.check_default_mode(default_mode)
        self.preview = "static/images/blank.png"
        self.check_rules = {
            "accounts_urls": None,
            "root": self.check_root,
            "storage_format": self.check_storage_format,
            "chunk": self.check_chunk,
            "max_retry": self.check_max_retry,
            "max_pages": self.check_max_pages,
            "default_mode": self.check_default_mode,
        }

    def check_cookie(self, cookie: dict | str) -> dict:
        if isinstance(cookie, dict):
            return cookie
        elif isinstance(cookie, str):
            self.cookie_cache = cookie
        return {}

    @staticmethod
    def add_cookie(cookie: dict) -> None | str:
        """合成cookie"""
        if isinstance(cookie, dict):
            for i in (TtWid.get_tt_wid(),):
                if isinstance(i, dict):
                    cookie |= i
            return cookie

    def check_root(self, root: str) -> Path:
        if (r := Path(root)).is_dir():
            return r
        if r := self.check_root_again(r):
            pass
        else:
            return self.main_path

    @staticmethod
    def check_root_again(root: Path) -> bool | Path:
        if root.resolve().parent.is_dir():
            root.mkdir()
            return root
        return False

    def check_chunk(self, chunk: int) -> int:
        if isinstance(chunk, int) and chunk > 0:
            return chunk
        return 512 * 1024

    def check_max_retry(self, max_retry: int) -> int:
        if isinstance(max_retry, int) and max_retry >= 0:
            return max_retry
        return 0

    def check_max_pages(self, max_pages: int) -> int:
        if isinstance(max_pages, int) and max_pages > 0:
            return max_pages
        return 99999

    def check_timeout(self, timeout: int | float) -> int | float:
        if isinstance(timeout, (int, float)) and timeout > 0:
            return timeout
        return 10

    def check_date_format(self, date_format: str) -> str:
        try:
            _ = strftime(date_format, localtime())
            return date_format
        except ValueError:
            return "%Y-%m-%d %H.%M.%S"

    def check_storage_format(self, storage_format: str) -> str:
        if storage_format in {"xlsx", "csv", "sql"}:
            return storage_format
        return ""

    def check_default_mode(self, default_mode: int) -> str:
        if default_mode in range(3, 7):
            return str(default_mode)
        return "0"

    def update_cookie(self):
        if self.cookie:
            self.add_cookie(self.cookie)
            self.headers["Cookie"] = Register.generate_cookie(self.cookie)
        elif self.cookie_cache:
            self.headers["Cookie"] = self.add_cookie(self.cookie_cache)
