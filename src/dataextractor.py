from datetime import datetime
from json import dumps
from time import localtime, strftime
from types import SimpleNamespace


__all__ = ["Extractor"]


class Extractor:
    def __init__(self, params):
        self.date_format = params.date_format
        self.cleaner = params.cleaner
        self.type = {
            "works": self.works,
            "comment": self.comment,
            "search": self.search,
        }

    @staticmethod
    def generate_data_object(data: dict) -> SimpleNamespace:
        """数据格式转化"""
        def depth_conversion(element):
            if isinstance(element, dict):
                return SimpleNamespace(
                    **{k: depth_conversion(v) for k, v in element.items()})
            elif isinstance(element, list):
                return [depth_conversion(item) for item in element]
            else:
                return element

        return depth_conversion(data)

    @staticmethod
    def safe_extract(
            data: SimpleNamespace,
            attribute_chain: str,  # 需要提取的属性链
            default: str | int | list | dict | SimpleNamespace = ""):
        """从 SimpleNamespace 中提取指定属性的值"""
        attributes = attribute_chain.split(".")
        for attribute in attributes:
            if "[" in attribute:
                parts = attribute.split("[", 1)
                attribute = parts[0]
                index = parts[1].split("]", 1)[0]
                try:
                    index = int(index)
                    data = getattr(data, attribute, None)[index]
                except (IndexError, TypeError, ValueError):
                    return default
            else:
                data = getattr(data, attribute, None)
                if not data:
                    return default
        return data or default

    def run(self, data: list[dict], recorder, type_: str, **kwargs) -> list[dict]:
        if type_ not in self.type.keys():
            raise ValueError
        return self.type[type_](data, recorder, **kwargs)

    def clean_description(self, desc: str) -> str:
        return self.cleaner.clear_spaces(self.cleaner.filter(desc))

    def format_date(self, data: SimpleNamespace, key: str = None) -> str:
        return strftime(
            self.date_format,
            localtime(
                self.safe_extract(data, key or "create_time") or None))

    def extract_description(self, data: SimpleNamespace) -> str:
        return self.safe_extract(data, "desc")

    def extract_batch(
            self,
            container: SimpleNamespace,
            data: SimpleNamespace) -> None:
        container.cache = container.template.copy()
        self.extract_works_info(container.cache, data)
        self.extract_account_info(container, data)
        self.extract_music(container.cache, data)
        self.extract_statistics(container.cache, data)
        self.extract_tags(container.cache, data)
        self._extract_extra_info(container.cache, data)
        self.extract_additional_info(container.cache, data)
        container.all_data.append(container.cache)

    def extract_works_info(self, item: dict, data: SimpleNamespace) -> None:
        item["id"] = self.safe_extract(data, "aweme_id")
        item["desc"] = self.clean_description(
            self.extract_description(data)) or item["id"]
        item["create_time"] = self.format_date(data)
        item["create_timestamp"] = self.safe_extract(data, "create_time")
        self._extract_text_extra(item, data)
        self.classifying_works(item, data)

    def extract_account_info(
            self,
            container: SimpleNamespace,
            data: SimpleNamespace,
            key="author",
    ) -> None:
        data = self.safe_extract(data, key)
        container.cache["uid"] = self.safe_extract(data, "uid")
        container.cache["sec_uid"] = self.safe_extract(data, "sec_uid")
        container.cache["short_id"] = self.safe_extract(data, "short_id")
        container.cache["unique_id"] = self.safe_extract(data, "unique_id")
        container.cache["signature"] = self.safe_extract(data, "signature")
        container.cache["user_age"] = self.safe_extract(data, "user_age")
        self.extract_nickname_info(container, data)

    def extract_nickname_info(self,
                              container: SimpleNamespace,
                              data: SimpleNamespace) -> None:
        if container.same:
            container.cache["nickname"] = container.name
            container.cache["mark"] = container.mark or container.name
        else:
            name = self.cleaner.filter_name(
                self.safe_extract(
                    data,
                    "nickname",
                    "已注销账号"),
                inquire=False,
                default="无效账号昵称", )
            container.cache["nickname"] = name
            container.cache["mark"] = name 

    def extract_music(self, item: dict, data: SimpleNamespace) -> None:
        if music_data := self.safe_extract(data, "music"):
            author = self.safe_extract(music_data, "author")
            title = self.safe_extract(music_data, "title")
            url = self.safe_extract(
                music_data, "play_url.url_list[-1]")  # 部分作品的音乐无法下载
        else:
            author, title, url = "", "", ""
        item["music_author"] = author
        item["music_title"] = title
        item["music_url"] = url

    def extract_statistics(self, item: dict, data: SimpleNamespace) -> None:
        data = self.safe_extract(data, "statistics")
        for i in (
                "digg_count",
                "comment_count",
                "collect_count",
                "share_count",
        ):
            item[i] = str(self.safe_extract(data, i))

    def extract_tags(self, item: dict, data: SimpleNamespace) -> None:
        if not (t := self.safe_extract(data, "video_tag")):
            tags = ["", "", ""]
        else:
            tags = [self.safe_extract(i, "tag_name") for i in t]
        for tag, value in zip(("tag_1", "tag_2", "tag_3"), tags):
            item[tag] = value

    def _extract_extra_info(self, item: dict, data: SimpleNamespace):
        if e := self.safe_extract(data, "anchor_info"):
            extra = dumps(
                e,
                ensure_ascii=False,
                indent=2,
                default=lambda x: vars(x))
        else:
            extra = ""
        item["extra"] = extra

    def extract_additional_info(self, item: dict, data: SimpleNamespace):
        item["height"] = self.safe_extract(data, "video.height")
        item["width"] = self.safe_extract(data, "video.width")
        item["ratio"] = self.safe_extract(data, "video.ratio")

    def works(self, data: list[dict], recorder) -> list[dict]:
        container = SimpleNamespace(
            all_data=[],
            template={
                "collection_time": datetime.now().strftime(self.date_format),
            },
            cache=None,
            same=False,
        )
        [self.extract_batch(container, self.generate_data_object(item))
         for item in data]
        self.record_data(recorder, container.all_data)
        return container.all_data

    def comment(self, data: list[dict], recorder,
                source=False) -> tuple[list[dict], list]:
        if not any(data):
            return [{}], []
        container = SimpleNamespace(
            all_data=[],
            reply_ids=[],
            template={
                "collection_time": datetime.now().strftime(self.date_format),
            },
            cache=None,
            same=False,
        )
        if source:
            [self._extract_reply_ids(container, i) for i in data]
        else:
            [self._extract_comments_data(
                container, self.generate_data_object(i)) for i in data]
            self.record_data(recorder, container.all_data)
        return container.all_data, container.reply_ids

    def _extract_comments_data(
            self,
            container: SimpleNamespace,
            data: SimpleNamespace):
        container.cache = container.template.copy()
        container.cache["create_time"] = self.format_date(data)
        container.cache["ip_label"] = self.safe_extract(data, "ip_label", "未知")
        container.cache["text"] = self.safe_extract(data, "text")
        container.cache["image"] = self.safe_extract(
            data, "image_list[0].origin_url.url_list[-1]")
        container.cache["sticker"] = self.safe_extract(
            data, "sticker.static_url.url_list[-1]")
        container.cache["digg_count"] = str(
            self.safe_extract(data, "digg_count"))
        container.cache["reply_to_reply_id"] = self.safe_extract(
            data, "reply_to_reply_id")
        container.cache["reply_comment_total"] = str(
            self.safe_extract(data, "reply_comment_total", 0))
        container.cache["reply_id"] = self.safe_extract(data, "reply_id")
        container.cache["cid"] = self.safe_extract(data, "cid")
        self.extract_account_info(container, data, "user")
        self._filter_reply_ids(container)
        container.all_data.append(container.cache)

    @staticmethod
    def _filter_reply_ids(container: SimpleNamespace):
        if container.cache["reply_comment_total"] != "0":
            container.reply_ids.append(container.cache["cid"])

    def _extract_reply_ids(self, container: SimpleNamespace, data: dict):
        cache = self.generate_data_object(data)
        container.cache = {
            "reply_comment_total": str(
                self.safe_extract(
                    cache, "reply_comment_total", 0)), "cid": self.safe_extract(
                cache, "cid")}
        self._filter_reply_ids(container)
        container.all_data.append(data)

    def search(self, data: list[dict], recorder, tab: int) -> list[dict]:
        if tab in {0, 1}:
            return self.search_general(data, recorder)
        elif tab == 2:
            return self.search_user(data, recorder)

    def search_general(self, data: list[dict], recorder) -> list[dict]:
        container = SimpleNamespace(
            all_data=[],
            cache=None,
            template={
                "collection_time": datetime.now().strftime(self.date_format),
            },
            same=False,
        )
        [self._search_result_classify(container, self.generate_data_object(i)) for i in data]
        self.record_data(recorder, container.all_data)
        return container.all_data

    def _search_result_classify(
            self,
            container: SimpleNamespace,
            data: SimpleNamespace):
        if d := self.safe_extract(data, "aweme_info"):
            self.extract_batch(container, d)
        elif d := self.safe_extract(data, "aweme_mix_info.mix_items"):
            [self.extract_batch(container, i) for i in d]
        elif d := self.safe_extract(data, "card_info.attached_info.aweme_list"):
            [self.extract_batch(container, i) for i in d]
        elif d := self.safe_extract(data, "user_list[0].items"):
            [self.extract_batch(container, i) for i in d]

    def search_user(self, data: list[dict], recorder) -> list[dict]:
        container = SimpleNamespace(
            all_data=[],
            cache=None,
            template={
                "collection_time": datetime.now().strftime(self.date_format),
            },
        )
        [self._deal_search_user_live(container, self.generate_data_object(i["user_info"])) for i in data]
        self.record_data(recorder, container.all_data)
        return container.all_data

    def record_data(self, record, data: list[dict]):
        for i in data:
            record.save(self.extract_values(record, i))

    def _deal_search_user_live(self,
                               container: SimpleNamespace,
                               data: SimpleNamespace,
                               user=True):
        if user:
            container.cache = container.template.copy()
        container.cache["avatar"] = self.safe_extract(data, f"{'avatar_thumb' if user else 'avatar_larger'}.url_list[0]")
        container.cache["nickname"] = self.safe_extract(data, "nickname")
        container.cache["sec_uid"] = self.safe_extract(data, "sec_uid")
        container.cache["signature"] = self.safe_extract(data, "signature")
        container.cache["uid"] = self.safe_extract(data, "uid")
        container.cache["short_id"] = self.safe_extract(data, "short_id")
        container.cache["verify"] = self.safe_extract(data, "custom_verify", "无")
        container.cache["enterprise"] = self.safe_extract(data, "enterprise_verify_reason", "无")
        if user:
            container.cache["follower_count"] = str(self.safe_extract(data, "follower_count"))
            container.cache["total_favorited"] = str(self.safe_extract(data, "total_favorited"))
            container.cache["unique_id"] = self.safe_extract(data, "unique_id")
            container.all_data.append(container.cache)

    @staticmethod
    def extract_values(record, data: dict) -> list:
        return [data[key] for key in record.field_keys]

    def _extract_text_extra(self, item: dict, data: SimpleNamespace):
        text = [
            self.safe_extract(i, "hashtag_name")
            for i in self.safe_extract(
                data, "text_extra", []
            )
        ]
        item["text_extra"] = ", ".join(i for i in text if i)

    def classifying_works(self, item: dict, data: SimpleNamespace) -> None:
        if images := self.safe_extract(data, "images"):
            self.extract_image_info(item, data, images)
        elif images := self.safe_extract(data, "image_post_info"):
            self.extract_image_info_tiktok(item, data, images)
        else:
            self.extract_video_info(item, data)

    def extract_image_info(
            self,
            item: dict,
            data: SimpleNamespace,
            images: list) -> None:
        item["type"] = "图集"
        item["downloads"] = " ".join(
            self.safe_extract(
                i, 'url_list[-1]') for i in images)
        item["duration"] = "00:00:00"
        self.extract_cover(item, data)

    def extract_image_info_tiktok(
            self,
            item: dict,
            data: SimpleNamespace,
            images: dict) -> None:
        item["type"] = "图集"
        item["downloads"] = " ".join(self.safe_extract(
            i, "display_image.url_list[-1]") for i in images["images"])
        item["duration"] = "00:00:00"
        self.extract_cover(item, data)

    @staticmethod
    def _time_conversion(time_: int) -> str:
        return f"{
        time_ //
        1000 //
        3600:0>2d}:{
        time_ //
        1000 %
        3600 //
        60:0>2d}:{
        time_ //
        1000 %
        3600 %
        60:0>2d}"

    def extract_video_info(self, item: dict, data: SimpleNamespace) -> None:
        item["type"] = "视频"
        item["downloads"] = self.safe_extract(
            data, "video.play_addr.url_list[-1]")
        item["duration"] = self._time_conversion(
            self.safe_extract(data, "video.duration", 0))
        self.extract_cover(item, data, True)

    def extract_cover(
            self,
            item: dict,
            data: SimpleNamespace,
            has=False) -> None:
        if has:
            # 动态封面图链接
            item["dynamic_cover"] = self.safe_extract(
                data, "video.dynamic_cover.url_list[-1]")
            # 静态封面图链接
            item["origin_cover"] = self.safe_extract(
                data, "video.origin_cover.url_list[-1]")
        else:
            item["dynamic_cover"], item["origin_cover"] = "", ""
       