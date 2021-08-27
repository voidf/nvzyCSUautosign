import aiohttp
import datetime
import aiofiles
import PIL
from PIL import Image
from io import BytesIO
from PIL.JpegImagePlugin import JpegImageFile
from loguru import logger
from typing import Union
import numpy as np


def statistics(pic: Union[np.array, JpegImageFile]):
    ctr = {}
    if isinstance(pic, JpegImageFile):
        pic = np.array(pic)
    for i in pic:
        for j in i:
            jrgb = tuple(j)
            ctr[jrgb] = ctr.get(jrgb, 0) + 1
    return ctr

def fliter_lines(pic: JpegImageFile):
    matrix = np.array(pic)
    ctr = statistics(matrix)
    sorted_result = sorted(ctr.items(), key=lambda x: x[1], reverse=True)
    blank_color = sorted_result[0][0]
    blank_color_tp = tuple(blank_color)
    radius = 4

    for p, i in enumerate(matrix):
        for q, j in enumerate(i):
            tot = 0
            same_color = 0
            tj = tuple(j)
            if tj == blank_color:
                continue
            for k in range(max(0, p-radius), min(len(matrix), p+radius)):
                for l in range(max(0, q-radius), min(len(i), q+radius)):
                    tot += 1
                    dvd = j - matrix[k][l]
                    sqrt_sum = dvd[0]**2 + dvd[1]**2 + dvd[2]**2 < 20
                    print(sqrt_sum)

                    if sqrt_sum < 20:
                        same_color += 1
            # print(same_color, tot, same_color*30 < tot, p, q)
            if same_color < 1:
                matrix[p][q] = blank_color
    new_img = Image.fromarray(matrix)
    new_img.show()


    print()
    # print(matrix)

    # pic.

async def main():
    async with aiohttp.ClientSession() as ses:
        # resp: 
        for i in range(1):
            resp: aiohttp.ClientResponse
            async with ses.get(f'https://ca.csu.edu.cn/authserver/getCaptcha.htl?{int(datetime.datetime.now().timestamp()*1e3)}') as resp:
                b = await resp.content.read()
                # f:aiofiles.tempfile.
                f: aiofiles.threadpool.binary.AsyncBufferedIOBase
                pic: JpegImageFile = Image.open(BytesIO(b))
                fliter_lines(pic)

                # async with aiofiles.open(f'data/R_{i}.png', 'wb') as f:
                    # print(type(f))
                    # await f.write(b)
                # print(b)

import asyncio

if __name__ == '__main__':
    asyncio.run(main())