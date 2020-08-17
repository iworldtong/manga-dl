import os
import re
import copy
import execjs
import urllib.parse
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests

from .. import config
from ..api import MangaApi
from ..utils import validate_title



class Mangabz(MangaApi):

    source_url = config.get('source2url')['mangabz']

    session = copy.deepcopy(MangaApi.session)
    session.headers.update({"referer": source_url})
                        
    @classmethod
    def fetch_chapter_argv(cls, chapter_url):
        cls.session.headers.update({"referer": chapter_url})
        res = cls.request(url, method="GET")
        cls.session.headers.update({"referer": cls.source_url})

        mangabz_cid = re.findall("MANGABZ_CID=(.*?);", res.text)[0]
        mangabz_mid = re.findall("MANGABZ_MID=(.*?);", res.text)[0]
        page_total = re.findall("MANGABZ_IMAGE_COUNT=(.*?);", res.text)[0]
        mangabz_viewsign_dt = re.findall("MANGABZ_VIEWSIGN_DT=(.*?);", res.text)[0]
        mangabz_viewsign = re.findall("MANGABZ_VIEWSIGN=(.*?);", res.text)[0]
        return (mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign, page_total)

    @classmethod
    def fetch_images_js(cls, chapter_url, page, mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign):
        url = chapter_url + "chapterimage.ashx?" + "cid=%s&page=%s&key=&_cid=%s&_mid=%s&_dt=%s&_sign=%s" % (mangabz_cid, page, mangabz_cid, mangabz_mid, urllib.parse.quote(mangabz_viewsign_dt), mangabz_viewsign)
        res = cls.request(url, method="GET")
        cls.session.headers.update({"referer": res.url})
        return res.text

    @classmethod
    def fetch_chapter(cls, chapter_url, chapter_dir=None):
        mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign, page_total = cls.fetch_chapter_argv(chapter_url)
        page_total = int(page_total)
        
        images_info = []
        desc = '\rFetching {}: ({}/{})'
        for i in range(page_total):
            print(desc.format(chapter_url, i+1, page_total), end='\r')
            i += 1
            # skip exists image
            if chapter_dir is not None and os.path.isdir(chapter_dir):
                if os.path.exists(os.path.join(chapter_dir, str(i+1)+'.jpg')) or\
                   os.path.exists(os.path.join(chapter_dir, str(i+1)+'.png')):
                   continue
                
            js_str = cls.fetch_images_js(chapter_url, i, mangabz_cid, mangabz_mid, mangabz_viewsign_dt, mangabz_viewsign)
            imagesList = execjs.eval(js_str)
            img_url = imagesList[0]
            img_name = str(i+1) + os.path.splitext(cls.url2fn(img_url))[-1]

            images_info.append({
                'fname': img_name,
                'url': img_url,
            })
        print(' ' * os.get_terminal_size().columns, end='\r')   
        return images_info

    @classmethod
    def fetch_manga(cls, manga_url):
        content = cls.request(manga_url, method="GET").content
        bs = BeautifulSoup(content, features="lxml")

        # details
        manga_title = bs.find('div', {'class': 'detail-info'})
        manga_title = manga_title.find('p', {'class': 'detail-info-title'}).text.strip()
        manga_title = validate_title(manga_title)

        manga_info = bs.find('div', {'class': 'detail-list-form-title'})
        tmp = [i for i in manga_info.text.split(' ') if i!='']
        status = tmp[1]
        latest = '-'
        if status == '連載中':
            manga_info['lastest'] = tmp[-2] + tmp[-1]
            manga_info['date'] = tmp[-3] 

        # chapters
        chapters_div = bs.find('div', {'id': 'chapterlistload'}).find_all('a')
        chapters = []
        for c in chapters_div:
            page_num = c.span.text.strip()
            title = c.text.replace(page_num, '').strip()
            url = cls.source_url + c.get('href')
            page_num = re.findall(r"\d+\.?\d*", c.find('span').text)[0]
            
            chapters.append({
                'title': validate_title(title),
                'url': url,
                'page_num': int(page_num),
                })

        manga_info = {
            'title': manga_title,
            'status': status,
            'latest': latest,
            'chapters': chapters,
        }
        return manga_info 

    @classmethod
    def fetch_keyword(cls, keyword, max_num=5):
        page_num = 0
        manga_urls = []
        while True:
            page_num += 1
            search_url = cls.source_url + '/search?title={}&page={}'.format(keyword, page_num)
            content = cls.request(search_url, method="GET").content
            bs = BeautifulSoup(content, features="lxml")

            container = bs.find('ul', {'class': 'mh-list'})
            if bs.find('img', {'class': 'img-404'}):
                break

            items = container.find_all('div', {'class': 'mh-item'})
            manga_urls.extend([cls.source_url + i.find('a').get('href') for i in items])
            
            if len(manga_urls) >= max_num:
                return manga_urls[:max_num]

        return manga_urls

    @classmethod
    def url2fn(cls, url):
        fn = url.split('/')[-1].split('?')[0]
        return fn



