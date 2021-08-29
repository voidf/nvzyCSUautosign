from loguru import logger
try:
    from Cryptodome.Cipher import AES
except:
    from Crypto.Cipher import AES

from binascii import b2a_hex, a2b_hex
import base64
import random
from bs4 import BeautifulSoup
import aiohttp
import requests
from requests import session

# ses = session()

saltStorage = None
exeStorage = None


def randomaesstring(x: int):
    return ''.join(random.choices("ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678", k=x))


class prpcrypt():

    @staticmethod
    def pad(s):
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
    # 定义 padding 即 填充 为PKCS7

    @staticmethod
    def unpad(s):
        return s[0:-ord(s[-1])]

    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
        # AES的加密模式为CBC

    def encrypt(self, text, iv):
        text = prpcrypt.pad(text)
        cryptor = AES.new(self.key.encode('utf-8'),
                          self.mode, iv.encode('utf-8'))
        # 第二个self.key 为 IV 即偏移量
        x = len(text) % 8
        if x != 0:
            text = text + '\0' * (8 - x)  # 不满16，32，64位补0
        # print(text)
        self.ciphertext = cryptor.encrypt(text.encode('utf-8'))
        return base64.standard_b64encode(self.ciphertext).decode("utf-8")

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        de_text = base64.standard_b64decode(text)
        plain_text = cryptor.decrypt(de_text)
        st = str(plain_text.decode("utf-8")).rstrip('\0')
        out = prpcrypt.unpad(st)
        return out

@logger.catch
def generate_auth(pw: str, key: str):
    iv = randomaesstring(16)
    word = randomaesstring(64) + pw
    pr = prpcrypt(key)
    return pr.encrypt(word, iv)

# @logger.catch
# def get_aes_salt(ses: session):
#     # headers = {
#     #     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#     #     "Accept-Encoding":"gzip, deflate, br",
#     #     "Accept-Language":"zh-CN,zh;q=0.9",
#     #     "Cache-Control":"no-cache",
#     #     "Connection":"keep-alive",
#     #     "DNT":"1",
#     #     "Host":"ca.csu.edu.cn",
#     #     "Pragma":"no-cache",
#     #     "Sec-Fetch-Dest":"document",
#     #     "Sec-Fetch-Mode":"navigate",
#     #     "Sec-Fetch-Site":"none",
#     #     "Sec-Fetch-User":"?1",
#     #     "Upgrade-Insecure-Requests":"1",
#     #     "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
#     # }
#     req = ses.get('https://ca.csu.edu.cn/authserver/login?service=https%3A%2F%2Fwxxy.csu.edu.cn%2Fa_csu%2Fapi%2Fcas%2Findex%3Fredirect%3Dhttps%253A%252F%252Fwxxy.csu.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%253Ffrom%253Dhistory%26from%3Dwap')

#     B = BeautifulSoup(req.text, "html.parser")
#     saltobj = B.find('input', attrs={'id': 'pwdEncryptSalt'})
#     exeobj = B.find('input', attrs={'id': 'execution'})

#     global saltStorage, exeStorage
#     if saltobj:
#         saltStorage = saltobj
#     else:
#         saltobj = saltStorage
#     if exeobj:
#         exeStorage = exeobj
#     else:
#         exeobj = exeStorage
#     # print(saltobj['value'])
#     # print(exeobj['value'])
#     return saltobj['value'], exeobj['value']

@logger.catch
async def aget_aes_salt(ses: aiohttp.ClientSession):
    async with ses.get(
        'https://ca.csu.edu.cn/authserver/login?service=https%3A%2F%2Fwxxy.csu.edu.cn%2Fa_csu%2Fapi%2Fcas%2Findex%3Fredirect%3Dhttps%253A%252F%252Fwxxy.csu.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%253Ffrom%253Dhistory%26from%3Dwap'
    ) as resp:
        req = await resp.text()
    # req = ses.get()
    B = BeautifulSoup(req, "html.parser")
    saltobj = B.find('input', attrs={'id': 'pwdEncryptSalt'})
    exeobj = B.find('input', attrs={'id': 'execution'})

    global saltStorage, exeStorage
    if saltobj:
        saltStorage = saltobj
    else:
        saltobj = saltStorage
    if exeobj:
        exeStorage = exeobj
    else:
        exeobj = exeStorage
    return saltobj['value'], exeobj['value']

# @logger.catch
# def r2(ses: session, user: str, pw: str):
#     salt, exe = get_aes_salt(ses)
#     form = {
#         "username": user,
#         "password": generate_auth(pw, salt),
#         "captcha": None,
#         # "rememberMe":True,
#         "_eventId": "submit",
#         "cllt": "userNameLogin",
#         "dllt": "generalLogin",
#         "lt": None,
#         "execution": exe
#     }
#     lnk = 'https://ca.csu.edu.cn/authserver/login?service=https%3A%2F%2Fwxxy.csu.edu.cn%2Fa_csu%2Fapi%2Fcas%2Findex%3Fredirect%3Dhttps%253A%252F%252Fwxxy.csu.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%253Ffrom%253Dhistory%26from%3Dwap'
#     # https://ca.csu.edu.cn/authserver/login?service=https%3A%2F%2Fwxxy.csu.edu.cn%2Fa_csu%2Fapi%2Fcas%2Findex%3Fredirect%3Dhttps%253A%252F%252Fwxxy.csu.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%253Ffrom%253Dhistory%26from%3Dwap
#     req = ses.post(lnk, data=form)
#     print(req.history)
#     print(req)
    # logger.warning(req.text)

# https://ca.csu.edu.cn/authserver/checkNeedCaptcha.htl?username={usr}&_={ts}

import datetime
from captcha_spider import get_captcha

@logger.catch
async def ar2(ses: aiohttp.ClientSession, usr: str, pwd: str):
    salt, exe = await aget_aes_salt(ses)
    ts = int(datetime.datetime.now().timestamp() * 1000)
    resp: aiohttp.ClientResponse
    async with ses.get(f'https://ca.csu.edu.cn/authserver/checkNeedCaptcha.htl?username={usr}&_={ts}') as resp:
        res = await resp.text()
    captcha = None
    if 'false' not in res:
        captcha = get_captcha(ses)
    form = { # TODO: 写验证码
        "username": usr,
        "password": generate_auth(pwd, salt),
        "captcha": captcha,
        "rememberMe": True,
        "_eventId": "submit",
        "cllt": "userNameLogin",
        "dllt": "generalLogin",
        "lt": None,
        "execution": exe
    }
    lnk = 'https://ca.csu.edu.cn/authserver/login?service=https%3A%2F%2Fwxxy.csu.edu.cn%2Fa_csu%2Fapi%2Fcas%2Findex%3Fredirect%3Dhttps%253A%252F%252Fwxxy.csu.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%253Ffrom%253Dhistory%26from%3Dwap'
    async with ses.post(
        lnk,
        data=form
    ) as resp:
        req = await resp.text()
        # logger.debug(req)

    # req = ses.post(lnk, data=form)
    # print(req.history)
    # print(req)
    # print(req.text)
# if __name__ == "__main__":
#     r2()
