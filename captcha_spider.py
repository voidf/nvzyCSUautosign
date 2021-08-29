import aiohttp
import datetime
import aiofiles
import PIL
from PIL import Image
from io import BytesIO
from PIL.JpegImagePlugin import JpegImageFile
from loguru import logger
from typing import Union, List
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

def sqrt_sum(differ_array: np.array):
    return differ_array[0]**2 + differ_array[1]**2 + differ_array[2]**2

async def fliter_and_cut(pic: JpegImageFile) -> List[JpegImageFile]:
    matrix = np.array(pic, dtype=int)
    ctr = statistics(matrix)
    sorted_result = sorted(ctr.items(), key=lambda x: x[1], reverse=True)
    blank_color = sorted_result[0][0]
    blank_color_tp = tuple(blank_color)
    radius = 1
    same_th = 5000
    width = matrix.shape[1]
    width_per_pic = width // 4


    for p, i in enumerate(matrix):
        for q, j in enumerate(i):
            tot = 0
            same_color = 0
            tj = tuple(j)
            
            # cur_sq = sqrt_sum(j)
            if sqrt_sum(j - blank_color) < same_th:
                matrix[p][q] = blank_color
                continue
            for k in range(max(0, p-radius), min(len(matrix), p+radius+1)):
                for l in range(max(0, q-radius), min(len(i), q+radius+1)):
                    tot += 1
                    dvd = j - matrix[k][l]
                    sq = sqrt_sum(dvd)
                    # print(sq)

                    if sq < same_th:
                        same_color += 1
            # print(same_color, tot, same_color*2 < tot, p, q)
            if same_color*2 < tot:
                matrix[p][q] = blank_color
    m2 = matrix.copy()
    m2.resize((pic.height, pic.width), refcheck=False)
    for p, i in enumerate(matrix):
        for q, j in enumerate(i):
            tot = 0
            same_color = 0
            tj = tuple(j)
            
            # cur_sq = sqrt_sum(j)
            if sqrt_sum(j - blank_color) < same_th:
                m2[p, q] = 255
                # matrix[p][q] = matrix[p][q][:1]
            else:
                m2[p, q] = 0
            # matrix[p][q] = matrix[p][q][:1]
            # matrix[p, q].resize(1, refcheck=False)
    # new_img = Image.fromarray(matrix.astype('uint8'))
    # new_img.show()
    pics = [
        m2[:, i*width_per_pic:(i+1)*width_per_pic].astype('uint8') for i in range(4)
    ]
    for ind, cut in enumerate(pics):
        border = [114514, 1919810, 0, 0] # 左上右下
        for p, i in enumerate(cut):
            for q, j in enumerate(i):
                if j == 0:
                    border[0] = min(q, border[0])
                    border[1] = min(p, border[1])
                    border[2] = max(q, border[2])
                    border[3] = max(p, border[3])
        # cut.crop(border)
        pics[ind] = Image.fromarray(
            cut[border[1]:border[3]+1, border[0]:border[2]+1]
        )


    return pics
    # for i in pics:
        # i.show()
    #     f: aiofiles.threadpool.binary.AsyncBufferedIOBase
    #     async with aiofiles.open(f'data/R_{i}.png', 'wb') as f:
        


    # print()
    # print(matrix)

    # pic.
import string, os

def train(pic: JpegImageFile):
    pic.show()
    cmd = input('像哪个？>>>')
    if len(cmd)>1:
        return
    if cmd in string.ascii_uppercase:
        with open('data/{}_/{:0>2d}.png'.format(cmd, 1+len(os.listdir(f'data/{cmd}_/'))), 'wb') as f:
            pic.save(f)
    else:
        with open('data/{}/{:0>2d}.png'.format(cmd, 1+len(os.listdir(f'data/{cmd}/'))), 'wb') as f:
            pic.save(f)

ml_data = {}

def reload():
    for directory in os.listdir('data/'):
        if os.path.isdir('data/' + directory):
            data_class = directory[0]
            for fn in os.listdir('data/' + directory):
                # with open('data/' + directory + '/' + fn) as f:
                ml_data.setdefault(data_class, []).append(np.array(Image.open('data/' + directory + '/' + fn)))

def predict(pic: Union[np.array, JpegImageFile, Image.Image]):
    if isinstance(pic, (JpegImageFile, Image.Image)):
        pic = np.array(pic)
    if not ml_data:
        reload()
    rate = []
    for k, v in ml_data.items():
        for mat in v:
            hamming = max(pic.shape[0], mat.shape[0]) * max(pic.shape[1], mat.shape[1])
            for p in range(min(pic.shape[0], mat.shape[0])):
                for q in range(min(pic.shape[1], mat.shape[1])):
                    if pic[p][q] == mat[p][q]:
                        hamming -= 1
            rate.append((hamming, k))
    rate.sort()
    d = {}
    for p, i in enumerate(rate[:4]):
        rated, key = i
        d[key] = d.get(key, 0) + 100 - p
    logger.debug(d.items())
    return sorted(d.items(), key=lambda x: x[1], reverse=True)[0][0]




async def get_captcha(ses: aiohttp.ClientSession):
    # for i in string.ascii_lowercase + string.ascii_uppercase + string.digits:
    for i in string.ascii_uppercase:
        if not os.path.exists('data/'+i+'_/'):
            os.mkdir('data/'+i+'_/')
    
    # async with aiohttp.ClientSession() as ses:
        # resp: 
        # for i in range(10):
    resp: aiohttp.ClientResponse
    async with ses.get(f'https://ca.csu.edu.cn/authserver/getCaptcha.htl?{int(datetime.datetime.now().timestamp()*1e3)}') as resp:
        b = await resp.content.read()

        # f:aiofiles.tempfile.
        f: aiofiles.threadpool.binary.AsyncBufferedIOBase
        with open('data/ori.png', 'wb') as f:
            f.write(b)
        pic: JpegImageFile = Image.open(BytesIO(b))
        pics = await fliter_and_cut(pic)
        j: JpegImageFile
        res = []
        for p, j in enumerate(pics):
            # train(j)
            # res = predict(j)
            # print(res)
            res.append(predict(j))
        res = ''.join(res)
        logger.debug('predict result: {}', res)
        return res

                    
import asyncio

# if __name__ == '__main__':
#     asyncio.run(get_captcha())
