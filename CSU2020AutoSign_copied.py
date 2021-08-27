# coding=utf-8
import time
import datetime
import json
import requests
import re
import ssl
from http_config import auth
import aiohttp
import urllib.parse
from bs4 import BeautifulSoup as BS
import urllib.request
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import traceback
import requests.packages.urllib3.util.ssl_
from AES import ar2
from loguru import logger
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

# ses = requests.session()
# # ses.mount('https://', MyAdapter(max_retries=20))



# ses.headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
# }

# @logger.catch
# def get_old_info():
#     auth_session(ses)
#     lnk = 'https://wxxy.csu.edu.cn/ncov/wap/default/index?from=history'
#     hds = {
#         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#         "Accept-Encoding":"gzip, deflate, br",
#         "Accept-Language":"zh-CN,zh;q=0.9",
#         "Cache-Control":"no-cache",
#         "Connection":"keep-alive",
#         "DNT":"1",
#         "Host":"wxxy.csu.edu.cn",
#         "Pragma":"no-cache",
#         "Referer":"https://wxxy.csu.edu.cn/ncov/wap/default/recently",
#         "Upgrade-Insecure-Requests":"1",
#         "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
#     }
#     sr = ses.get(lnk)
#     # logger.critical(sr.text)
#     # print(sr.text)
#     rer = re.findall('''var def = ({.*})''',sr.text)
#     # logger.warning(rer)
#     # print(rer)
#     je = json.loads(rer[0])
#     return je

@logger.catch
async def agetold(ses: aiohttp.ClientSession, usr: str, pwd: str):
    await aauth_session(ses, usr, pwd)
    lnk = 'https://wxxy.csu.edu.cn/ncov/wap/default/index?from=history'
    async with ses.get(lnk) as resp:
        sr = await resp.text()
    rer = re.findall('''var def = ({.*})''',sr)
    # logger.warning(rer)
    # print(rer)
    je = json.loads(rer[0])
    return je

# @logger.catch
# def sleep_until_sign(signtime):
#     slpt = (datetime.datetime.now().timestamp() + 3600 * 8 ) % 86400
#     slpt = 86400 - slpt + signtime
#     print(f'阻塞{slpt}秒')
#     time.sleep(max(1,slpt))
import random

@logger.catch
async def asleep_until_sign(signtime):
    slpt = (datetime.datetime.now().timestamp() + 3600 * 8 ) % 86400
    slpt = 86400 - slpt + signtime
    # print(f'等待{slpt}秒')
    logger.debug(f'等待{slpt}秒')
    await asyncio.sleep(max(1,slpt))

signtime = 500 # 在每天的第几秒签到

async def asign_one(usr: str, pwd: str):
    async with aiohttp.ClientSession() as ses:
        while True:
            try:
                # sign_res = sign_in(get_old_info())
                sign_res = await asign_in(ses, await agetold(ses, usr, pwd), usr, pwd)
                if sign_res and sign_res[0] == "{":
                    logger.debug(sign_res)
                    sign_res = json.loads(sign_res)
                    if sign_res["e"] == 0:
                        logger.info(f"[{usr}]今日签到提交成功，msg: {sign_res}")
                        logger.info(f'{datetime.datetime.now()}')
                        # sleep_until_sign(signtime)
                        await asleep_until_sign(signtime)
                    elif sign_res["e"] == 1 and sign_res["m"] == "今天已经填报了":
                        logger.info(f"[{usr}]今天已完成签到，msg: {sign_res}")
                        logger.info(f'{datetime.datetime.now()}')
                        # sleep_until_sign(signtime)
                        await asleep_until_sign(signtime)
                    else:
                        logger.error(f"[{usr}]未知的错误，msg: {sign_res}")
                else:
                    # auth_session()
                    await aauth_session(ses, usr, pwd)
                # time.sleep(5)
                await asyncio.sleep(random.randint(20,40))
            except:
                # traceback.print_exc(random.randint(20,40))
                # time.sleep(5)
                logger.error(traceback.format_exc())
                await asyncio.sleep(random.randint(20,40))
            
            logger.critical(f"[{usr}]程序退出")

@logger.catch
async def main():
    await asyncio.gather(
        *(asign_one(i['userName'], i['passWord']) for i in auth)
    )
    # sleep_until_sign(signtime)
    
    

# @logger.catch
# def sign_in(je):
#     auth_session()
#     url = "https://wxxy.csu.edu.cn/ncov/wap/default/save"
#     try:
        
#         je["id"] = int(je["id"])
#         je["date"] = str_time("%Y%m%d")
#         je["created"] = unix_time()
#         jgeo = json.loads(je["geo_api_info"])
#         je["address"] = jgeo['formattedAddress']
#         je["city"] = jgeo['addressComponent']['city']
#         je["province"] = jgeo['addressComponent']['province']
#         je["area"] = ' '.join([
#             jgeo['addressComponent']['province'],
#             jgeo['addressComponent']['city'],
#             jgeo['addressComponent']['district'],
#         ])

#         http_result = ses.post(
#             url, data=je, timeout=(2, 30))
#         return http_result.text
#     except requests.exceptions.ReadTimeout:
#         print("requests.exceptions.ReadTimeout:[%s]" % url)
#         return ""
#     except requests.exceptions.ConnectionError:
#         print("requests.exceptions.ConnectionError:[%s]" % url)
#         return ""

@logger.catch
async def asign_in(ses: aiohttp.ClientSession, je, usr: str, pwd: str):
    await aauth_session(ses, usr, pwd)
    url = "https://wxxy.csu.edu.cn/ncov/wap/default/save"
    je["id"] = int(je["id"])
    je["date"] = str_time("%Y%m%d")
    je["created"] = unix_time()
    jgeo = json.loads(je["geo_api_info"])
    je["address"] = jgeo['formattedAddress']
    je["city"] = jgeo['addressComponent']['city']
    je["province"] = jgeo['addressComponent']['province']
    je["area"] = ' '.join([
        jgeo['addressComponent']['province'],
        jgeo['addressComponent']['city'],
        jgeo['addressComponent']['district'],
    ])
    async with ses.post(
        url, data=je, timeout=60
    ) as resp:
        return await resp.text()

def unix_time():
    return int(datetime.datetime.now().timestamp())

# @logger.catch
# def auth_session():
#     r2(ses, auth['userName'], auth['passWord'])

@logger.catch
async def aauth_session(ses: aiohttp.ClientSession, usr: str, pwd: str):
    await ar2(ses, usr, pwd)


def str_time(pattern='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(pattern)

import asyncio
if __name__ == "__main__":
    asyncio.run(main())


# https://ca.csu.edu.cn/authserver/getCaptcha.htl?1630081044006