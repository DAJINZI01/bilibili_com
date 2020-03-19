# coding=utf-8
from gevent import monkey; monkey.patch_all()
from gevent import pool
from ffmpy3 import FFmpeg

from myutils.mybasespider import MyBaseSpider
from myutils.mydownloader import Downloader
from bilibili_com_api import BilibiliComAPI
from settings import BASE_DIR

import os
import re


class BilibiliCom(MyBaseSpider):
    """
    哔哩哔哩网站爬虫
    """
    def __init__(self):
        MyBaseSpider.__init__(self)
        self.headers.update({
            "Referer": "https://www.bilibili.com", # 没有refer会出现453的错误
            "Range": "bytes=0-",
        })
        # 创建下载器对象
        self.downloader = Downloader(headers=self.headers)
        # 获取操作的api
        self.api = BilibiliComAPI()
        # 过滤的无效字符 文件名
        self.invalid_char = r":"
        # 进程池
        self.pool = pool.Pool()

    def __del__(self):
        self.pool.join()

    @staticmethod
    def combine_video_and_audio(video_name, audio_name, combine_name):
        """
        合并视频和音频文件，并且删除原来的文件
        :param video_name: 视频文件名字
        :param audio_name: 音频文件名字
        :param combine_name: 合成后的名字
        :return: 返回ffmpeg实例
        """
        # 创建ffmpeg实例
        ff = FFmpeg(inputs={video_name: None, audio_name: None}, outputs={combine_name: None})
        # ff.run_async()
        ff.run()
        # 删除视频和音频文件
        os.remove(video_name)
        os.remove(audio_name)
        return ff

    def download_video(self, params):
        """
        合并视频和音频的下载
        :param params: {"title": title, "video": {"title": title, "url": url}, "audio": {"title": title, "url": url}}
        :return: 下载成功的状态 下载成功, True, 下载失败, False
        """
        video, audio = params["video"], params["audio"]
        if not video["url"] or not audio["url"]:
            print("index: {} require a membership, which has not been fixed. you can choose another.".format(index))
            return False
        # 下载视频
        if not os.path.exists(video["title"]):
            self.downloader.download(video["title"], video["url"])
        # 下载音频
        if not os.path.exists(audio["title"]):
            self.downloader.download(audio["title"], audio["url"])
        # 合并视频和音频
        return self.combine_video_and_audio(video["title"], audio["title"], params["title"])

    def download_video_by_ssid(self, ssid):
        """
        根据番剧ssId，下载所有的集数
        :param ssid: 番剧ssId
        :return:
        """
        ep_list = self.api.get_ss_video_and_audio_urls(ssid)
        # 1. 创建番剧文件夹
        bangumi_dir = "{}/{}".format(BASE_DIR, re.sub(self.invalid_char, "-", ep_list["title"]))
        if not os.path.exists(bangumi_dir):
            os.mkdir(bangumi_dir)
        # 2. 根据下载列表下载视频和音频
        ff_list = []
        for item in ep_list["ep_list"]:
            file_name = "{}/{}".format(bangumi_dir, item["title"])
            # 构造下载参数
            video_name = "{}_video.mp4".format(file_name)
            audio_name = "{}_audio.mp4".format(file_name)
            combine_name = "{}.mp4".format(file_name)
            params = {
                "title": combine_name,
                "video": {"title": video_name, "url": item["video"]},
                "audio": {"title": audio_name, "url": item["audio"]},
            }
            self.pool.apply_async(func=self.download_video, args=(params))
        # 阻塞等待结束
        self.pool.join()

    def download_video_by_index(self, ssid, index):
        """
        根据指定ssid, index下标，下载单p
        :param ssid: 番剧ssid
        :param index: 默认从0开始，如果是最新会员句集，这里暂时不处理，直接返回
        :return: 下载的状态 True: 表示成功, False: 表示失败
        """
        ep_list = self.api.get_ss_video_and_audio_urls(ssid)
        # 1. 创建番剧文件夹
        bangumi_dir = "{}/{}".format(BASE_DIR, re.sub(self.invalid_char, "-", ep_list["title"]))
        if not os.path.exists(bangumi_dir):
            os.mkdir(bangumi_dir)
        # 2. 判断index是否越界
        ep_list_len = len(ep_list["ep_list"])
        if index >= ep_list_len:
            print("index: {} must be in [0 - {}]".format(index, ep_list_len))
            return False
        # 4. 开始下载
        ep = ep_list["ep_list"][index]
        file_name = "{}/{}".format(bangumi_dir, ep["title"])
        video_name = "{}_video.mp4".format(file_name)
        audio_name = "{}_audio.mp4".format(file_name)
        combine_name = "{}.mp4".format(file_name)
        params = {
            "title": combine_name,
            "video": {"title": video_name, "url": ep["video"]},
            "audio": {"title": audio_name, "url": ep["audio"]},
        }
        # 5. 下载成功
        self.download_video(params)
        return True

    def download_video_by_keyword(self, keyword, index=0, all_download=False):
        """
        通过关键字keyword，下载番剧
        :param keyword: 关键词
        :param index: 指定下载的集数，如果指定all_download，则index无效
        :param all_download: 是否全部下载
        :return: 下载成功的标志 成功: True, 失败: False
        """
        # 1. 获取ssid
        ssid = self.api.get_ssid(keyword)
        if not ssid:
            print("{} does not exists, please check your input.".format(keyword))
            return False
        if all_download:
            self.download_video_by_ssid(ssid)
            return True
        return self.download_video_by_index(ssid, index)

if __name__ == "__main__":
    b = BilibiliCom()
    # b.combine_video_and_audio("video.mp4", "audio.mp4", "xxx.mp4")
    # b.download_video_by_ssid(29310)
    # b.download_video_by_index(29310, 10)
    b.download_video_by_keyword("某科学的超电磁炮T", 2)
