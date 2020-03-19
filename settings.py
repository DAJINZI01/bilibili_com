import os


# 项目的根目录
BASE_DIR = "./data"
if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)

# url接口地址
API_URLS= {
    # 获取播放连接的url
    "play": "https://api.bilibili.com/pgc/player/web/playurl",
    # 获取初始化信息的url 需要拼接路径 ssId
    "bangumi_play": "https://www.bilibili.com/bangumi/play/ss{ssId}",
    # 搜索接口
    "search_all": "https://api.bilibili.com/x/web-interface/search/all/v2",
}
