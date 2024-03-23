import base64
import json
from io import BytesIO
import os
import random

from httpx import AsyncClient, TimeoutException, HTTPError
from nonebot.log import logger
from tqdm import tqdm
from urllib.parse import unquote


from .file_tools import Config
from .dao.image_dao import ImageDao
from .proxies import proxy_http, proxy_socks

config = Config()

async def is_vip():
    cookie = Config.get_file_args('COOKIE')
    vip = 'https://www.pixiv.net/setting_user.php'
    headers = {
        'referer': 'https://www.pixiv.net/',
        'cookie': Config().cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }
    http = proxy_http if Config().proxies_switch else None
    socks = proxy_socks if Config().proxies_switch else None
    async with AsyncClient(proxies=http, transport=socks) as client:
        res = await client.get(url=vip, headers=headers, timeout=10)
    if res.status_code == 200:
        if 'ads_hide_pc' in res.text:
            return True
        else:
            False
    else:
        logger.error(f"请求失败，状态码: {res.status_code}")

async def get_ArtPic(data):     #通过作品id获取图片url(regular)/width/height

    id = data["id"]
    artword_url = 'https://www.pixiv.net/ajax/illust/{id}/pages?lang=zh'
    
    headers = {
        'referer': 'https://www.pixiv.net/artworks/'+id,
        'cookie': Config().cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }

    http = proxy_http if Config().proxies_switch else None
    socks = proxy_socks if Config().proxies_switch else None
    async with AsyncClient(proxies=http, transport=socks) as client:
        res = await client.get(url=artword_url.format(id=id), headers=headers, timeout=10)
    response = json.loads(unquote(res.text))
    try:
        data_url = await config.dict_choice(response["body"])
    except KeyError as e:
        logger.error(f"多图索引错误：{e}")
        raise Exception("多图索引错误")
    update_data = {
        "url": data_url["urls"]["regular"],
        "width": data_url["width"],
        "height": data_url["height"]
    }
    data.update(update_data)
    return data


async def get_url(online_switch: int, sort: str = 'date_d', tags: str = "", r18: int = 0, rank: int = 0, nums: int = 0):
    safe_url = 'https://www.pixiv.net/ajax/search/illustrations/{tag}?word={tag}&order={sort}&mode=safe&p={p}&csw=0&s_mode=s_tag&type=illust&lang=zh'
    r18_url = 'https://www.pixiv.net/ajax/search/illustrations/{tag}?word={tag}&order={sort}&mode=r18&p={p}&csw=0&s_mode=s_tag&type=illust&lang=zh'
    notag_url = 'https://www.pixiv.net/ajax/discovery/artworks?mode={mode}&limit=60&lang=zh'

    headers = {
        'referer': 'https://www.pixiv.net/premium',
        'cookie': Config().cookie,
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
                    res = await client.get(url=notag_url.format(mode = 'safe' if r18==0 else 'r18'), headers=headers, timeout=10)
                else :
                    url = safe_url if r18==0 else r18_url
                    res = await client.get(url=url.format(tag=tags, sort=sort, p=random.choice([1,2])), headers=headers, timeout=10)
                    if not json.loads(unquote(res.text))['body']['illust']['data']:
                        res = await client.get(url=url.format(tag=tags, sort=sort, p=1), headers=headers, timeout=10)
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
                data_list = response['body']['page']['ranking']['items'] if rank == 1 \
                    else response['body']['recommendedIllusts']
            else:
                data_list = response['body']['illust']['data']
            if not data_list:
                raise Exception("没有获取到与tag相关图片")
            if rank ==1:            #每日排行榜
                logger.debug(f'nums = {nums}')
                one_rankpic = await Config.dict_choice(data_list) if nums == 0 else data_list[int(nums) - 1] 
                dict_map = {d['id']: d for d in response['body']['thumbnails']['illust']}
                one_picData = dict_map.get(one_rankpic['id'])
                one_picData['url'] = one_picData['urls']["1200x1200"]
                one_picData['Rank_No'] = one_rankpic['rank']
                del dict_map,data_list
            elif not tags and rank == 0 :       #涩图不带tag的
                c = 0
                while c < 3:
                    one_picData = await Config.dict_choice(data_list)
                    dict_map = {d['id']: d for d in response['body']['thumbnails']['illust']}
                    one_picData = dict_map.get(one_picData['illustId'])
                    one_picData = await Config().isban_tag(one_picData)
                    if one_picData:
                        break
                    c += 1
                if c >= 3:
                    one_picData = None
                one_picData['url'] = one_picData['urls']["1200x1200"]
                del dict_map,data_list
            else:                       #涩图带tag
                c = 0
                while c < 3:
                    logger.debug('1')
                    one_picData = await Config.dict_choice(data_list)
                    logger.debug('2')
                    one_picData = await Config().isban_tag(one_picData)
                    logger.debug('3')
                    if one_picData:
                        break
                    c += 1
                if c >= 3:
                    one_picData = None
                del data_list
                    
                if one_picData["pageCount"] > 1 :
                    one_picData = await get_ArtPic(one_picData)
            if one_picData:
                one_picData['r18'] = False if r18==0 else True
                filename, ext = os.path.splitext(one_picData['url'])
                ext = ext[1:]
                one_picData['ext'] = ext
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
        tag_img = str(pid) + "." + one_picData[0]['ext']
        tags = one_picData[0]['tags']
        flag = 0
        while True:
            try:
                flag += 1
                if flag > 10:
                    raise Exception("获取图片内容失败次数过多，请检查网络链接")
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
                        'tags': tags,
                        'Rank_No': one_picData[0].get('Rank_No', None),
                        'base64': f"base64://{base64.b64encode(BytesIO(response.content).getvalue()).decode()}"}
            return img_info
        img_path = f"loliconImages/{'r18/' if r18 else ''}{pid}.{one_picData[0]['ext']}"
        with open(img_path, 'wb') as f:
            f.write(response.content)
    pbar.close()
    return tag_img
