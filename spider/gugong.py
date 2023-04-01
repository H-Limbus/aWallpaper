#  -*- coding: utf-8 -*-
# @Author  :  Limbus
#  @file   :  gugong.py
#  @Date   :  2/4/2023 AM 12:24
# @Github  :  https://github.com/H-Limbus

# import httpx
# from lxml import etree

#
# https://www.dpm.org.cn/download/lights_image/id/237608/img_size/4.html
# https://www.dpm.org.cn/light/259142.html
# https://www.dpm.org.cn/download/lights_image/id/259288/img_size/2.html
# /searchs/royal/category_id/173/p/6.html
# /searchs/royal/category_id/173/p/2.html
import httpx
import asyncio
import aiofiles
import random
from lxml import etree
from configure.Config import ConfigFunc


def gugongDownload(searchSyntax):
    link = 'https://www.dpm.org.cn/download/lights_image/id/'
    try:
        loop = asyncio.get_event_loop()
        url = 'https://www.dpm.org.cn/searchs/royal/category_id/173/p/{}.html'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'}
        tasks = []
        for i in range(1):
            task = loop.create_task(GetPicturesLink(url.format(str(random.randint(1, 60))), headers))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        downloadTasks = []
        for t in tasks:
            for x in t.result():
                tt = loop.create_task(DownloadPic(link + x.replace('/light/', '').split('.')[0] + '/img_size/4.html'))
                downloadTasks.append(tt)
        asyncio.get_event_loop().run_until_complete(asyncio.wait(downloadTasks))
    except httpx.ConnectTimeout:
        pass


async def GetPicturesLink(link, headers):
    async with httpx.AsyncClient(timeout=10) as client:
        req = await client.get(link, headers=headers)
        q = etree.HTML(req.text).xpath('/html/body/div[3]/div[2]/div/div[2]/div[2]/div/div[1]/a/@href')
        return q


async def DownloadPic(url):
    tempFile = ConfigFunc()['global'].get('imagemainfile')
    async with httpx.AsyncClient(timeout=10) as client:
        name = url.split('/')[-3]
        reqContent = await client.get(url)
        async with aiofiles.open(f'{tempFile}{name}.jpg', 'wb') as f:
            await f.write(reqContent.content)