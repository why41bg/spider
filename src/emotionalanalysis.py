"""评论情感分析模块"""

import requests
import json
import re
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib

from src.configuration import Settings
from src.maincomplete import prompt
from src.customizer import (
    ERROR,
    INFO,
)

# pd.pandas.set_option('display.max_rows', 200)  # debug


class EmotionalAnalysis:
    def __init__(self, root, console, filepath, workid) -> None:
        self.root = root
        self.console = console
        self.workid = workid
        self.vis = False  # 可视化标志位
        self.running = True
        settings = Settings(self.root, self.console)
        self.api_key = settings.read()['api_key']
        self.secret_key = settings.read()['secret_key']
        self.filepath = filepath
        self.savedf = pd.DataFrame(columns=[
                    "评论内容", "confidence", "negative_prob", "positive_prob", "sentiment"])
        self.url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token=" + self.get_access_token()
        self.payload = None
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_access_token(self) -> str:
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.api_key, "client_secret": self.secret_key}
        return str(requests.post(url, params=params).json().get("access_token"))

    def send_requests(self) -> json:
        response = requests.request("POST", self.url, headers=self.headers, data=self.payload)
        return json.loads(response.text)

    def update_payload(self, comment) -> None:
        payload = {
            "text": f"{comment}"
        }
        self.payload = json.dumps(payload)

    def read_comments(self) -> pd.DataFrame:
        comment_df = pd.read_excel(self.filepath)
        # 判断评论中是否包含 '@' 符号
        comment_df['drop'] = comment_df["评论内容"].str.contains('@')
        # 删除包含 '@' 符号的评论
        comment_df = comment_df[~comment_df['drop'].astype(bool)]
        # 删除评论中的中括号及其中括号里面的内容
        comment_df['评论内容'] = comment_df['评论内容'].apply(lambda x: re.sub(r'\[.*?\]', '', x))
        # 重新设置索引
        comment_df = comment_df.reset_index(drop=True)
        return comment_df["评论内容"]

    def is_emoji(self, content) -> bool:
        if not content:
            return False
        if u"\U0001F600" <= content and content <= u"\U0001F64F":
            return True
        elif u"\U0001F300" <= content and content <= u"\U0001F5FF":
            return True
        elif u"\U0001F680" <= content and content <= u"\U0001F6FF":
            return True
        elif u"\U0001F1E0" <= content and content <= u"\U0001F1FF":
            return True
        else:
            return False

    def emo_res_vis(self) -> None:
        try:
            df = pd.read_excel(self.root.joinpath(
                f'./data/作品{self.workid}_评论感情色彩分析结果.xlsx'))
        except:
            if self.console.input(
                f"作品{self.workid}对应的分析结果不存在，是否对其评论进行分析？(YES/NO)："
                ).upper() == "YES":
                self.callapi()
                return
        count_v = df["sentiment"].value_counts()
        labels = count_v.index.tolist()
        v = count_v.values.tolist()
        # 设置颜色映射
        cmap = matplotlib.colormaps.get_cmap('tab20c')
        colors = cmap.colors[:len(labels)]
        explode = (0.07, ) * len(count_v)
        plt.pie(v, explode=explode, colors=colors)
        plt.title('评论情感正负性饼图')
        legend_labels = [
            f"{self.change_label(label)}: {value}" 
            for label, value in zip(labels, v)]
        plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

    def change_label(self, label: str) -> str:
        if str(label) == "0":
            return "消极评论"
        elif str(label) == "1":
            return "中立评论"
        elif str(label) == "2":
            return "积极评论"

    def add_df(self, text: dict) -> None:
        row = [text["text"]]
        for k, v in text["items"][0].items():
            row.append(v)
        self.savedf.loc[len(self.savedf.index)] = row
        self.console.print(f'评论"{text["text"]}"分析成功', style=INFO)

    def callapi(self) -> None:
        comments = self.read_comments()
        # self.console.print(comments)  # debug
        for v in comments:
            if not v:  # 空行
                continue
            if self.is_emoji(v):  # 含Emoji表情
                continue
            self.update_payload(v)
            if resp := self.send_requests():
                self.add_df(resp)
                continue
            self.console.print(f'评论"{v}"分析失败', style=ERROR)
        self.savedf.to_excel(
            self.root.joinpath(f"./data/作品{self.workid}_评论感情色彩分析结果.xlsx"),
            index=False)
        self.console.print(f"作品{self.workid}评论分析结果已保存", style=INFO)

    def run(self) -> None:
        while self.running:
            select = prompt(
                "评论分析模块功能",
                ("评论感情色彩分析",
                "分析结果可视化",),
                self.console,)
            if select in {"Q", "q"}:
                self.running = False
            elif not select:
                break
            elif select == "1":
                self.callapi()
            elif select == "2":
                self.emo_res_vis()





