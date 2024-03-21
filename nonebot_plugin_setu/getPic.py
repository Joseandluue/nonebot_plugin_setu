import base64
import json
from io import BytesIO

from httpx import AsyncClient, TimeoutException, HTTPError
from nonebot.log import logger
from tqdm import tqdm
from urllib.parse import unquote
import random

from .file_tools import Config
from .dao.image_dao import ImageDao
from .proxies import proxy_http, proxy_socks

cookie = ''


async def choice_picData(data):

    id = data["id"]
    artword_url = 'https://www.pixiv.net/ajax/illust/{id}/pages?lang=zh'
    
    headers = {
        'referer': 'https://www.pixiv.net/artworks/'+id,
        'cookie': cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }

    http = proxy_http if Config().proxies_switch else None
    socks = proxy_socks if Config().proxies_switch else None
    async with AsyncClient(proxies=http, transport=socks) as client:
        res = await client.get(url=artword_url.format(id=id), headers=headers, timeout=10)
    response = json.loads(unquote(res.text))
    try:
        data_urls = response["body"]
        data_url = data_url = data_urls[random.randint(0,len(data_urls)) - 1]
    except KeyError as e:
        logger.error(f"多图索引错误：{e}")
        raise Exception(f"多图索引错误")
    update_data = {
        "url": data_url["urls"]["regular"],
        "width": data_url["width"],
        "height": data_url["height"]
    }
    data.update(update_data)
    return data


async def isban(data, ban_tags:list = []):
    count = 0
    while count < 3:
        one_picData = data[random.randint(0, len(data) - 1)]
        tags = one_picData.get("tag", [])
        if not any(tag in tags for tag in ban_tags):
            return one_picData
        count += 1
    return None

async def get_url(online_switch: int, tags: str = "", r18: int = 0, ban_tags:list = []):
    safe_url = 'https://www.pixiv.net/ajax/search/illustrations/{tag}?word={tag}&order=date_d&mode=safe&p={p}&csw=0&s_mode=s_tag&type=illust&lang=zh'
    r18_url = 'https://www.pixiv.net/ajax/search/illustrations/{tag}?word={tag}&order=date_d&mode=r18&p={p}&csw=0&s_mode=s_tag&type=illust&lang=zh'
    notag_url = 'https://www.pixiv.net/ajax/top/illust?mode={mode}&lang=zh'

    headers = {
        'referer': 'https://www.pixiv.net/',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-GB;q=0.6',
        'Cache-Control':'max-age=0',
        'cookie': cookie,
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform':'"Windows"',
        'Sec-Fetch-Des': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }

    http = proxy_http if Config().proxies_switch else None
    socks = proxy_socks if Config().proxies_switch else None
    async with AsyncClient(proxies=http, transport=socks) as client:
        flag = 0
        while True:
            try:
                flag += 1
                if flag > 10:
                    raise Exception(f"获取api内容失败次数过多，请检查网络链接")
                if not tags:
                    res = await client.get(url=notag_url.format(mode = 'all' if r18==0 else 'r18'), headers=headers, timeout=10)
                else :
                    url = safe_url if r18==0 else r18_url
                    res = await client.get(url=url.format(tag=tags, p=random.choice([1,2])), headers=headers, timeout=10)
                    if not json.loads(unquote(res.text))['body']['illust']['data']:
                        res = await client.get(url=url.format(tag=tags, p=1), headers=headers, timeout=10)
                logger.debug(res)
                if res.status_code == 200:
                    break
            except TimeoutException as e:
                logger.error(f"获取pixiv内容超时{type(e)}")
            except HTTPError as e:
                logger.error(f"{type(e)}")
                raise e
            except Exception as e:
                logger.error(f"{e}")
                raise e
        response = json.loads(unquote(res.text))
        try:
            if not tags:
                data_list = response['body']['thumbnails']['illust']
            else:
                data_list = response['body']['illust']['data']
            if not data_list:
                raise Exception("没有获取到与tag相关图片")
            one_picData = await isban(data_list, ban_tags)
            if one_picData["pageCount"] > 1 :
                one_picData = await choice_picData(one_picData)
            if one_picData:
                one_picData['r18'] = False if r18==0 else True
                one_picData['ext'] = "jpg"
            one_picData = [one_picData]
        except Exception as e:
            logger.error(f"{e}")
            raise e
        if not one_picData:
            return ""
        logger.debug(one_picData)
        # ImageDao().add_images(one_picData)
        img = await down_pic(one_picData, online_switch, r18)
        return img


async def down_pic(one_picData, online_switch: int, r18: int = 0):
    head = {
        'referer': 'https://www.pixiv.net/',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }
    http = proxy_http if Config().proxies_switch else None
    socks = proxy_socks if Config().proxies_switch else None
    async with AsyncClient(proxies=http, transport=socks) as client:
        pbar = tqdm(one_picData, desc='Downloading', colour='green')
        tag_img = ""
        splicing_url = "https://i.pixiv.re/img-master/" + one_picData[0]["url"][one_picData[0]["url"].find("/img/"):]
        if "square" in splicing_url:
            splicing_url = splicing_url.replace("square", "master")
        proxy_url = splicing_url
        url = one_picData[0]['url']
        url = proxy_url if Config().proxies_switch else url
        pid = one_picData[0]['id']
        ext = one_picData[0]['ext']
        tag_img = str(pid) + "." + ext
        flag = 0
        while True:
            try:
                flag += 1
                if flag > 10:
                    raise Exception(f"获取图片内容失败次数过多，请检查网络链接")
                response = await client.get(url=url, headers=head, timeout=10)
                if response.status_code == 200:
                    break
            except TimeoutException as e:
                logger.error(f"获取图片内容超时: {type(e)}")
            except HTTPError as e:
                logger.error(f"{type(e)}")
                raise e
            except Exception as e:
                logger.error(f"{e}")
                raise e
        pbar.update(1)
        if online_switch == 1:
            img_info = {'pid': pid,
                        'base64': f"base64://{base64.b64encode(BytesIO(response.content).getvalue()).decode()}"}
            return img_info
        img_path = f"loliconImages/{'r18/' if r18 else ''}{pid}.{ext}"
        with open(img_path, 'wb') as f:
            f.write(response.content)
    pbar.close()
    return tag_img
