# coding=utf-8
from inspect import trace
import os
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
import pickle

logger.add("nszy_auto_sign.log", rotation="60 MB")

# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


import random
import json5

signtime = 500 # 在每天的第几秒签到

class AutoSign:
    # @logger.catch

    async def agetold(self, ses: aiohttp.ClientSession, usr: str, pwd: str):
        """从服务器端读上一次的请求保存的信息"""
        try:
            await self.aauth_session(ses, usr, pwd)
            lnk = 'https://wxxy.csu.edu.cn/ncov/wap/default/index?from=history'
            async with ses.get(lnk) as resp:
                sr = await resp.text()
            # with open('dbg.htm', 'w', encoding='utf-8') as R:
                # R.write(sr)
            rer = re.findall('''var def = ({.*?});''',sr,re.DOTALL)
            # logger.warning(rer)
            # print(rer)
            je = json5.loads(rer[0].replace('\r\n',''))
            return je
        except:
            logger.error('爬历史信息出现问题：{}', traceback.format_exc())
            return {}


    @logger.catch
    async def asleep_until_sign(self, signtime):
        """等待直到下一次"""
        slpt = (datetime.datetime.now().timestamp() + 3600 * 8 ) % 86400
        slpt = 86400 - slpt + signtime
        logger.debug(f'等待{slpt}秒')
        await asyncio.sleep(max(1,slpt))


    def __init__(self, usr: str, pwd: str):
        self.ses = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
            }
        )
        self.usr = usr
        self.pwd = pwd
        self.alive = True
    
    async def asign_one(self):
        """为一个人打上"""
        ses = self.ses
        usr = self.usr
        pwd = self.pwd
        # async with aiohttp.ClientSession() as ses:
        while self.alive:
            try:
                # sign_res = sign_in(get_old_info())
                sign_res = await self.asign_in(ses, await self.agetold(ses, usr, pwd), usr, pwd)
                if sign_res and sign_res[0] == "{":
                    logger.debug(sign_res)
                    sign_res = json.loads(sign_res)
                    if sign_res["e"] == 0:
                        logger.info(f"[{usr}]今日签到提交成功，msg: {sign_res}")
                        logger.info(f'{datetime.datetime.now()}')
                        # sleep_until_sign(signtime)
                        await self.asleep_until_sign(signtime)
                    elif sign_res["e"] == 1 and sign_res["m"] == "今天已经填报了":
                        logger.info(f"[{usr}]今天已完成签到，msg: {sign_res}")
                        logger.info(f'{datetime.datetime.now()}')
                        # sleep_until_sign(signtime)
                        await self.asleep_until_sign(signtime)
                    else:
                        logger.error(f"[{usr}]未知的错误，msg: {sign_res}")
                else:
                    # auth_session()
                    await self.aauth_session(ses, usr, pwd)
                # time.sleep(5)
                await asyncio.sleep(random.randint(20,40))
            except:
                # traceback.print_exc(random.randint(20,40))
                # time.sleep(5)
                logger.error(traceback.format_exc())
                await asyncio.sleep(random.randint(20,40))
            
            logger.critical(f"[{usr}]程序退出")


    @logger.catch
    async def asign_in(self, ses: aiohttp.ClientSession, je, usr: str, pwd: str):
        await self.aauth_session(ses, usr, pwd)
        url = "https://wxxy.csu.edu.cn/ncov/wap/default/save"
        try:
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
            with open(f'{usr}_bak.json', 'w') as f:
                json.dump(je, f)
            if not os.path.exists('history'):
                os.mkdir('history')
            with open(f'history/{usr}_{datetime.datetime.now().strftime("%Y-%m-%d")}.json', 'w') as f:
                json.dump(je, f)
        except:
            logger.error(traceback.format_exc())
            with open(f'{usr}_bak.json', 'r') as f:
                je = json.load(f)
        async with ses.post(
            url, data=je, timeout=60
        ) as resp:
            return await resp.text()
    @logger.catch
    async def aauth_session(self, ses: aiohttp.ClientSession, usr: str, pwd: str):
        result = await ar2(ses, usr, pwd)
        if result is not None:
            logger.critical(result)
            self.alive = False


def unix_time():
    return int(datetime.datetime.now().timestamp())

    # @logger.catch
    # def auth_session():
    #     r2(ses, auth['userName'], auth['passWord'])



def str_time(pattern='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(pattern)

@logger.catch
async def main():
    await asyncio.gather(
        *(AutoSign(i['userName'], i['passWord']).asign_one() for i in auth)
    )
import asyncio
if __name__ == "__main__":
    asyncio.run(main())


# https://ca.csu.edu.cn/authserver/getCaptcha.htl?1630081044006