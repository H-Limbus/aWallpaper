#  -*- coding: utf-8 -*-
# @Author  :  Limbus
#  @file   :  bingDownload
#  @Date   :  28/3/2023 AM 12:04
# @Github  :  https://github.com/H-Limbus

import httpx
import asyncio
import aiofiles
import random
from lxml import etree
from configure.Config import ConfigFunc


def bingDownload(searchSyntax):
    try:
        loop = asyncio.get_event_loop()
        url = 'https://bing.ioliu.cn/?p={}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0'}
        tasks = []
        for i in range(8):
            task = loop.create_task(GetPicturesLink(url.format(str(random.randint(1, 120))), headers))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        downloadTasks = []
        for t in tasks:
            for x in t.result():
                tt = loop.create_task(DownloadPic(x))
                downloadTasks.append(tt)
        asyncio.get_event_loop().run_until_complete(asyncio.wait(downloadTasks))
    except httpx.ConnectTimeout:
        pass


async def GetPicturesLink(link, headers):
    async with httpx.AsyncClient(timeout=10) as client:
        req = await client.get(link, headers=headers)
        q = etree.HTML(req.text).xpath('/html/body/div[3]/div/div/img/@src')
        return q


async def DownloadPic(url):
    tempFile = ConfigFunc()['global'].get('imagemainfile')
    async with httpx.AsyncClient(timeout=10) as client:
        name = url.split('.')[2].split('_')[0]
        type = url.split('.')[-1]
        reqContent = await client.get(url.replace('800x480', '1920x1080'))
        async with aiofiles.open(f'{tempFile}{name}.{type}', 'wb') as f:
            await f.write(reqContent.content)


