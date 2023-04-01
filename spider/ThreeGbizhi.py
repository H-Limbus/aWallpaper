#  -*- coding: utf-8 -*-
# @Author  :  Limbus
#  @file   :  3gbizhiDownload
#  @Date   :  29/3/2023 PM 4:33
# @Github  :  https://github.com/H-Limbus


import httpx
import asyncio
import aiofiles
from lxml import etree
import urllib.parse
from configure.Config import ConfigFunc

tempFile = ConfigFunc()['global'].get('imagemainfile')


def ThreeGbizhiDownload(searchSyntax):
    try:
        loop = asyncio.get_event_loop()
        url = 'https://www.3gbizhi.com/search/2-{}/{}.html'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
                   'Referer': 'https://desk.3gbizhi.com/'}
        tasks = []
        for i in range(1, 7):
            task = loop.create_task(GetPicturesLink(url.format(urllib.parse.quote(searchSyntax), str(i)), headers))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        downloadTasks = []
        for t in tasks:
            for x in t.result():
                tt = loop.create_task(DownloadPic(x, headers))
                downloadTasks.append(tt)
        if len(downloadTasks) == 0:
            return
        asyncio.get_event_loop().run_until_complete(asyncio.wait(downloadTasks))
    except httpx.ConnectTimeout:
        pass


async def GetPicturesLink(link, headers):
    async with httpx.AsyncClient(timeout=15) as client:
        req = await client.get(link, headers=headers)
        q = etree.HTML(req.text).xpath('/html/body/div[3]/ul/li/a/div[1]/img/@src')
        return q


async def DownloadPic(url, headers):
    async with httpx.AsyncClient(timeout=10) as client:
        name = url.replace('.556.308.jpg', '').split('/')[-1]
        reqContent = await client.get(url.replace('.556.308.jpg', ''), headers=headers)
        async with aiofiles.open(f'{tempFile}{name}', 'wb') as f:
            await f.write(reqContent.content)