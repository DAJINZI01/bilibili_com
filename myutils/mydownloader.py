# coding=utf-8

import requests
import time


class Downloader(object):
    """
    自定义的下载器
    """
    def __init__(self, symbol="=", total_num=30, headers={}):
        """
        初始化方法
        :param symbol: 进度条显示的符号 例如: = , * , ...
        :param total_num: 显示符号的数量（长度）
        :param headers: 下载需要的请求头
        """
        # 下载显示的一些符号
        # self.download_symbol = r"\|/"
        # 符号控制变量
        # self.s_l = len(self.download_symbol)
        # 显示的符号
        self.symbol = symbol
        #
        self.total_num = total_num
        # 请求头
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        }
        self.headers.update(headers)

    def download_line(self, already_download_size, file_size, start_time):
        """
        下载行的显示的符号
        :param already_download_size: 已经下载的文件的大小 单位M
        :param file_size: 总的文件的长度 单位M
        :param start_time: 开始下载的时间
        :return: 字符串
        """
        already_num = int(self.total_num * already_download_size / file_size)
        remind_num = self.total_num - already_num
        # 进度条
        progress_bar = "[" + self.symbol*already_num + " "*remind_num + "]"
        # 比例显示
        percent_bar = "%.2fM/%.2fM" % (already_download_size, file_size)
        # 时间显示
        time_bar = time.strftime("%M:%S", time.localtime(time.time() - start_time))
        print("\r{} {} {}".format(progress_bar, percent_bar, time_bar), end="")

    def download(self, file_name, url):
        """
        下载网络文件
        :param file_name: 下载存放的路径
        :param url: url地址
        :return:
        """
        # 1. 获取文件大小
        response = requests.get(url, headers=self.headers, stream=True)
        file_size = int(response.headers["Content-Length"]) / 1024 / 1024
        already_write_size = 0  # 已经写入的数据长度
        # 2. 打开文件写入
        start_time = time.time() # 统计开始时间
        f = open(file_name, "wb")
        print("download {}".format(file_name))
        for chunk in response.iter_content(chunk_size=1024):
            data_len = f.write(chunk)
            already_write_size += data_len / 1024 / 1024
            self.download_line(already_write_size, file_size, start_time)
        # 3. 关闭文件
        f.close()
        print("\tok.")


if __name__ == '__main__':
    d = Downloader()
    d.download_line(7, 10, time.time())
