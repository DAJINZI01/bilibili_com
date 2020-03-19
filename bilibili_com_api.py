# coding=utf-8
from settings import API_URLS

import requests
import re
import json

"""
bilibili.com api 文件
"""


class BilibiliComAPI(object):
    """
    bilibili api
    """
    def __init__(self):
        """
        初始化方法
        """
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            # "Referer": "https://www.bilibili.com",
        }

    def get_initial_state(self, ssid):
        """
        通过ssId获取番剧的所有的信息
        {
            "loaded":true,
            "ver":Object{...},
            "ssr":Object{...},
            "loginInfo":Object{...},
            "h1Title":"异度侵入 ID:INVADED",
            "mediaInfo":Object{...},
            "epList":Array[12],
            "epInfo":Object{...},
            "sections":Array[1],
            "orderSections":Array[0],
            "ssList":Array[1],
            "userState":Object{...},
            "ssPayMent":null,
            "epPayMent":null,
            "player":Object{...},
            "sponsor":Object{...},
            "ssRecom":Array[0],
            "showBv":false,
            "interact":Object{...},
            "nextEp":null,
            "playerEpList":Object{...},
            "insertScripts":Array[2]
        }
        :param ssId: 番剧id
        :return: 所有信息的字典
        """
        response = requests.get(API_URLS["bangumi_play"].format(ssId=ssid), headers=self.headers)
        html = response.content.decode("utf-8")
        res = re.search(r"window.__INITIAL_STATE__=({.+?});", html).group(1)
        return json.loads(res)

    def get_ep_list(self, ssid):
        """
        通过番剧ssId，获取番剧集数
        {
            "loaded":false,
            "id":307446,
            "badge":"",
            "badgeType":0,
            "epStatus":2,
            "aid":82232111,
            "bvid":"BV1zJ411L7Vv",
            "cid":160231833,
            "from":"bangumi",
            "cover":"//i0.hdslb.com/bfs/archive/4a1895e5b675209b6948dc321c3cc4991a6262bc.jpg",
            "title":"1",
            "titleFormat":"第1话",
            "vid":"",
            "longTitle":"JIGSAWED 碎片世界",
            "hasNext":true,
            "i":0,
            "sectionType":0,
            "releaseDate":"",
            "skip":{

            },
            "hasSkip":false
        }
        :param ssId: 番剧ssId
        :return: 字典 {"title": title, "ep_list": []}
        """
        init_state = self.get_initial_state(ssid)
        return {"title": init_state["mediaInfo"]["title"], "ep_list": init_state["epList"]}

    def get_play_url(self, params):
        """
        根据参数params，获取播放信息的接口
        params格式同 get_video_and_audio_url
        {
            "code":0,
            "message":"success",
            "result":{
                "accept_format":"hdflv2,flv,flv720,flv480,mp4",
                "code":0,
                "seek_param":"start",
                "is_preview":0,
                "no_rexcode":0,
                "format":"flv480",
                "fnval":16,
                "video_project":true,
                "fnver":0,
                "message":"",
                "type":"DASH",
                "accept_quality":Array[5],
                "bp":0,
                "quality":32,
                "timelength":1479977,
                "result":"suee",
                "seek_type":"offset",
                "has_paid":false,
                "from":"local",
                "dash":Object{...},
                "video_codecid":7,
                "accept_description":Array[5],
                "status":2
            }
        }
        :param params: 请求的一些参数
        :return: 字典
        """
        return requests.get(API_URLS["play"], headers=self.headers, params=params).json()

    def get_video_and_audio_url(self, params):
        """
        获取视频和音频的下载链接
        params: 格式如下
            params = {
                # 没有也可以
                # "avid": "82232426",
                # 没有也可以
                # "cid": "140699463",
                # 没有也可以
                # "bvid": "",
                "qn": "80", # 这个应该表示的是视频的质量 16， 32， 64， 80， 112 不过试了一下112好像没啥用
                # 没有也可以
                # "type": "",
                # 没有也可以
                # "otype": "json",
                "ep_id": "307447", # 对应每一p集数 episode
                # 没有也可以
                # "fourk": "1",
                # 没有也可以
                # "fnver": "0",
                "fnval": "16",
                # 没有也可以
                # "session": "c1f003185cac135189816b9625e0880e",
            }
        请求最新的一集出现 {'code': -10403, 'message': '大会员专享限制'}
        :param params: 请求的一些参数
        :return: 视频和音频连接
        """
        data = self.get_play_url(params)
        # 这里先不处理会员视频 {'code': -10403, 'message': '大会员专享限制'}
        if data.get("code") == -10403:
            return None, None
        # 这里默认取video视频8个中的第一个
        video_url = data["result"]["dash"]["video"][0]["base_url"]
        # 这里默认取audio音频3个中的第一个
        audio_url = data["result"]["dash"]["audio"][0]["base_url"]
        return video_url, audio_url

    def get_ss_video_and_audio_urls(self, ssid):
        """
        通过番剧ssId，获取一个番剧的所有番的下载连接
        :param ssid: 番剧ssId
        :return: 字典 {"title": title, ep_list: [{"title" title, "video": url, "audio": url}, {}, {}])
        """
        ep_list = self.get_ep_list(ssid)
        items = []
        for ep in ep_list["ep_list"]:
            # 构造请求的params
            params = {
                "avid": ep["aid"],
                "cid": ep["cid"],
                "bvid": ep["bvid"],
                "qn": "80",  # 这个应该表示的是视频的质量 16， 32， 64， 80， 112 不过试了一下112好像没啥用
                "type": "",
                "otype": "json",
                "ep_id": ep["id"],  # 对应每一p集数 episode
                "fourk": "1",
                "fnver": "0",
                "fnval": "16",
            }
            video, audio = self.get_video_and_audio_url(params)
            # 数据过滤
            item = {
                "title": "{}-{}".format(ep["titleFormat"], ep["longTitle"]),
                "video": video,
                "audio": audio,
            }
            items.append(item)
        ep_list["ep_list"] = items
        return ep_list

    def search_all(self, keyword, page=1):
        """
        根据keyword关键字，搜索
        {
            "code":0,
            "message":"0",
            "ttl":1,
            "data":{
                "seid":"",
                "page":1,
                "pagesize":20,
                "numResults":1000,
                "numPages":50,
                "suggest_keyword":"",
                "rqt_type":"search",
                "cost_time":Object{...},
                "exp_list":Object{...},
                "egg_hit":0,
                "pageinfo":Object{...},
                "top_tlist":Object{...},
                "show_column":0,
                "show_module_list":Array[9],
                "result":Array[9]
            }
        }
        :param keyword: 关键字
        :param page: 页数 一页默认20条
        :return: 字典
        """
        params = {
            "page": page,
            "keyword": keyword,
        }
        return requests.get(API_URLS["search_all"], params=params, headers=self.headers).json()

    def get_ssid(self, keyword):
        """
        根据关键字keyword，获取ssid
        :param keyword: 关键字
        :return: ssid
        """
        result_list = self.search_all(keyword)["data"]["result"]
        for result in result_list:
            if result["result_type"] == "media_bangumi" and result["data"]:
                return result["data"][0]["season_id"]
        return None


if __name__ == '__main__':
    api = BilibiliComAPI()
    # print(api.get_initial_state(29310))
    # print(api.get_ep_list(29310))
    # 测试获取一个番剧的所有番的下载连接
    # print(api.get_ss_video_and_audio_urls(29310))
    # print(api.search_all("异度侵入"))
    print(api.get_ssid("异度入侵"))

