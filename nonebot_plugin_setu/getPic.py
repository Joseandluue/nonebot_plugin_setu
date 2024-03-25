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


headers = {
        'referer': 'https://www.pixiv.net/',
        'cookie': Config.get_file_args('COOKIE'),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }

http = proxy_http if Config().proxies_switch else None
socks = proxy_socks if Config().proxies_switch else None


async def is_vip():
    vip_url = 'https://www.pixiv.net/setting_user.php'
    try:
        async with AsyncClient(proxies=http, transport=socks) as client:
            res = await client.get(url=vip_url, headers=headers, timeout=10)
            if res.status_code == 200:
                if 'ads_hide_pc' in res.text:
                    logger.info(f'用户是 VIP 账号')
                    return True
                else:
                    logger.info(f'用户是普通账号')
                    return False
            else:
                logger.error(f"请求失败，状态码: {res.status_code}")
                return False
    except TimeoutException as e:
        logger.error(f"请求超时: {e}")
        return False
    except HTTPError as e:
        logger.error(f"HTTP 错误: {e}")
        return False
    except Exception as e:
        logger.error(f"发生异常: {e}")
        return False


async def get_ArtPic(data):     #通过作品id获取图片url(regular)/width/height
    id = data["id"]
    artword_url = 'https://www.pixiv.net/ajax/illust/{id}/pages?lang=zh'
    async with AsyncClient(proxies=http, transport=socks) as client:
        res = await client.get(url=artword_url.format(id=id), headers=headers, timeout=10)
    response = json.loads(unquote(res.text))
    try:
        data_list = response["body"]
        url = [urls["urls"]["regular"] for urls in data_list]
    except KeyError as e:
        logger.error(f"多图索引错误：{e}")
        raise Exception("多图索引错误")
    update_data = {
        "url": url
    }
    data.update(update_data)
    return data


async def get_rankpic_url(r18: int ,nums):
    rankpic_url = 'https://www.pixiv.net/ajax/top/illust?mode={mode}&lang=zh'
    async with AsyncClient(proxies=http, transport=socks) as client:
        flag = 0
        while True:
            try:
                flag += 1
                if flag > 10:
                    raise Exception(f"获取api内容失败次数过多，请检查网络链接")
                res = await client.get(url=rankpic_url.format(mode = 'all' if r18==0 else 'r18'), headers=headers, timeout=10)
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
        rankpic_list = response['body']['page']['ranking']['items']
        one_rankpicId = await Config.dict_choice(rankpic_list) if nums == 0 else rankpic_list[int(nums) - 1] 
        illusts_list = {d['id']: d for d in response['body']['thumbnails']['illust']}
        one_picData = illusts_list.get(one_rankpicId['id'])
        one_picData['url'] = one_picData['urls']["1200x1200"]
        one_picData['Rank_No'] = one_rankpicId['rank']
        return one_picData

async def get_notagPic_url(r18: int ):
    notag_url = 'https://www.pixiv.net/ajax/discovery/artworks?mode={mode}&limit=60&lang=zh'    #发现页面
    notag_vip_url = 'https://www.pixiv.net/ajax/top/illust?mode={mode}&lang=zh'                    #首页
    
    vip = Config.get_file_args('ISVIP')

    async with AsyncClient(proxies=http, transport=socks) as client:
        flag = 0
        while True:
            try:
                flag += 1
                if flag > 10:
                    raise Exception(f"获取api内容失败次数过多，请检查网络链接")
                if vip == 0:
                    res = await client.get(url=notag_url.format(mode = 'safe' if r18==0 else 'r18'), headers=headers, timeout=10)
                    logger.info(f"返图url:{notag_url.format(mode = 'safe' if r18==0 else 'r18')}")
                elif vip == 1:
                    if r18 == 0:
                        res = await client.get(url=notag_vip_url.format(mode = 'all'), headers=headers, timeout=10)
                        logger.info(f"返图url:{notag_vip_url.format(mode = 'all')}")
                    elif r18 == 1:
                        res = await client.get(url=notag_vip_url.format(mode = 'r18'), headers=headers, timeout=10)
                        logger.info(f"返图url:{notag_vip_url.format(mode = 'r18')}")
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
        
        if vip == 0:
            id_list = response['body']['recommendedIllusts']
            one_picid = await Config.dict_choice(id_list) if id_list else logger.debug('普通账号返图清单失败')
            illusts_list = {d['id']: d for d in response['body']['thumbnails']['illust']}
            one_picData = illusts_list.get(one_picid['illustId'])   
        elif vip == 1:
            if r18 == 0:
                ## id_list = response['body']['thumbnails']['illust']     ## 暂时废弃，这个太看p站给你的推荐作品了，号没养好不建议用response['body']['page']['recommend']['ids']
                ## one_picid = await Config.dict_choice(id_list) if id_list else logger.debug('会员账号返图非R18清单失败')
                ## illusts_list = {d['id']: d for d in response['body']['thumbnails']['illust']}
                ## one_picData = illusts_list.get(one_picid)
                illusts_list = response['body']['thumbnails']['illust']
                one_picData = await Config.dict_choice(illusts_list) if illusts_list else logger.debug('会员账号返图非R18清单失败')
            elif r18 == 1:
                illusts_list = response['body']['thumbnails']['illust']
                one_picData = await Config.dict_choice(illusts_list) if illusts_list else logger.debug('会员账号返图R18清单失败')
        one_picData['url'] = one_picData['urls']["1200x1200"]
        return one_picData


async def get_tagPic_url(tags,sort,r18):
    url = 'https://www.pixiv.net/ajax/search/illustrations/{tag}?word={tag}&order={sort}&mode={mode}&p={p}&csw=0&s_mode=s_tag&type=illust&lang=zh'
    async with AsyncClient(proxies=http, transport=socks) as client:
        flag = 0
        while True:
            try:
                flag += 1
                if flag > 10:
                    raise Exception("获取api内容失败次数过多，请检查网络链接")
                xq_url = url.format(tag=tags, sort=sort, mode='safe' if r18==0 else 'r18', p=random.choice([1,2]))
                res = await client.get(url=xq_url, headers=headers, timeout=10)
                logger.debug(f"第一次tag搜索链接：{xq_url}")
                if not json.loads(unquote(res.text))['body']['illust']['data']:
                    logger.debug('第一次tag搜索失败，插画data为空')
                    res = await client.get(url=url.format(tag=tags, sort=sort, mode='safe' if r18==0 else 'r18', p=1), headers=headers, timeout=10)
                    logger.debug(f"第二次tag搜索链接：{url.format(tag=tags, sort=sort, mode='safe' if r18==0 else 'r18', p=1)}")
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
        data_list = response['body']['illust']['data']
        c = 0
        while c < 10:
            one_picData = await Config.dict_choice(data_list)
            one_picData = await Config().isban_tag(one_picData)
            if one_picData:
                break
            c += 1
        if c >= 10:
            one_picData = None
        del data_list
        return one_picData


async def get_url(online_switch: int, sort: str = 'date_d', tags: str = "", r18: int = 0, rank: int = 0, nums: int = 0):
    try:
        if rank == 1:
            one_picData = await get_rankpic_url(r18,nums)
        elif not tags:
            one_picData = await get_notagPic_url(r18)
        elif tags:
            one_picData = await get_tagPic_url(tags,sort,r18)
        if one_picData["pageCount"] > 1 :
            one_picData = await get_ArtPic(one_picData)
        if one_picData:
            one_picData['r18'] = False if r18==0 else True
            filename, ext = os.path.splitext(one_picData['url'] if isinstance(one_picData['url'],str) else one_picData['url'][0])
            ext = ext[1:]
            one_picData['ext'] = ext
            one_picData = [one_picData]
    except Exception as e:
        logger.error(f"{e}")
        raise e
    if not one_picData:
        return ""
    # ImageDao().add_images(one_picData)
    logger.debug(one_picData)
    img = await down_pic(one_picData, online_switch, r18)
    return img


async def down_pic(one_picData, online_switch: int, r18: int = 0):
    logger.debug('0')
    head = {
        'referer': 'https://www.pixiv.net/',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }
    http = proxy_http if Config().proxies_switch else None
    socks = proxy_socks if Config().proxies_switch else None
    async with AsyncClient(proxies=http, transport=socks) as client:
        pbar = tqdm(one_picData, desc='Downloading', colour='green')
        tag_img = ""
        if isinstance(one_picData[0]['url'], str):
            one_picData[0]['url'] = [one_picData[0]['url']]
        pid = one_picData[0]['id']
        tag_img = str(pid) + "." + one_picData[0]['ext']
        tags = one_picData[0]['tags']
        flag = 0
        down_pic_list = []
        pic_saveData = []
        for one_url in one_picData[0]['url']:
            splicing_url = "https://i.pixiv.re/img-master" + one_url[one_url.find("/img/"):]
            proxy_url = splicing_url
            if "square" in splicing_url:
                splicing_url = splicing_url.replace("square", "master")
            url = proxy_url if Config().proxies_switch else one_url
            while True:
                try:
                    flag += 1
                    if flag > 10:
                        raise Exception("获取图片内容失败次数过多，请检查网络链接")
                    response = await client.get(url=url, headers=head, timeout=10)
                    if response.status_code == 200:
                        if online_switch == 1:
                            down_pic_list.append(f"base64://{base64.b64encode(BytesIO(response.content).getvalue()).decode()}")
                        else:
                            pic_saveData.append(response.content)
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
                        'base64': down_pic_list}
            return img_info
        count = 0
        for response in pic_saveData:
            count += 1
            img_path = f"loliconImages/{'r18/' if r18 else ''}{pid}_{count}.{one_picData[0]['ext']}"
            with open(img_path, 'wb') as f:
                f.write(response)
    pbar.close()
    return tag_img
