"""Cookie 解析程序"""

from re import finditer

from src.parameter import TtWid


class Cookie:
    pattern = r'(?P<key>[^=;,]+)=(?P<value>[^;,]+)'

    def __init__(self, settings, console):
        self.settings = settings
        self.console = console

    def run(self):
        """提取 Cookie 并写入配置文件"""
        if not (cookie := self.console.input("请粘贴输入cookie\n$ ")):
            return
        self.extract(cookie)

    def extract(self, cookie: str, clean=True, return_=False):
        if clean:
            keys = {
                "passport_csrf_token": None,
                "passport_csrf_token_default": None,
                "passport_auth_status": None,
                "passport_auth_status_ss": None,
                "sid_guard": None,
                "uid_tt": None,
                "uid_tt_ss": None,
                "sid_tt": None,
                "sessionid": None,
                "sessionid_ss": None,
                "sid_ucp_v1": None,
                "ssid_ucp_v1": None,
                "csrf_session_id": None,
                "odin_tt": None,
            }
            matches = finditer(self.pattern, cookie)
            for match in matches:
                key = match.group('key').strip()
                value = match.group('value').strip()
                if key in keys:
                    keys[key] = value
            self.check_key(keys)
        else:
            keys = cookie
        if return_:
            return keys
        self.write(keys)
        self.console.print("写入 Cookie 成功！")

    def check_key(self, items):
        """主要查看sessionid_ss参数状态"""
        if not items["sessionid_ss"]:
            self.console.print("当前 Cookie 未登录")
        else:
            self.console.print("当前 Cookie 已登录")
        # 将Cookie当中所有为空的值删去
        keys_to_remove = [key for key, value in items.items() if value is None]
        for key in keys_to_remove:
            del items[key]

    def write(self, text: dict | str):
        """将cookie写入本地settings文件中"""
        data = self.settings.read()
        data["cookie"] = text
        self.settings.update(data)


class Register:
    get_url = "https://sso.douyin.com/get_qrcode/"
    check_url = "https://sso.douyin.com/check_qrconnect/"
    get_params = {
        "service": "https://www.douyin.com",
        "need_logo": "false",
        "need_short_url": "true",
        "device_platform": "web_app",
        "aid": "6383",
        "account_sdk_source": "sso",
        "sdk_version": "2.2.5",
        "language": "zh",
    }
    check_params = {
        "service": "https://www.douyin.com",
        "need_logo": "false",
        "need_short_url": "false",
        "device_platform": "web_app",
        "aid": "6383",
        "account_sdk_source": "sso",
        "sdk_version": "2.2.5",
        "language": "zh",
    }

    def __init__(self, settings, console, xb, user_agent, ua_code):
        self.xb = xb
        self.settings = settings
        self.console = console
        self.headers = {
            "User-Agent": user_agent,
            "Referer": "https://www.douyin.com/",
            "Cookie": self.generate_cookie(TtWid.get_tt_wid()),
        }
        self.verify_fp = None
        self.ua_code = ua_code
        self.temp = None

    @staticmethod
    def generate_cookie(data: dict) -> str:
        if not isinstance(data, dict):
            return ""
        result = [f"{k}={v}" for k, v in data.items()]
        return "; ".join(result)
