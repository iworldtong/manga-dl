import os
import re
import copy
import json
import execjs
import lzstring
import base64
import requests
from bs4 import BeautifulSoup

from .. import config
from ..api import MangaApi
from ..utils import validate_title


class Ykmh(MangaApi):

    source_url = config.get('source2url')['ykmh']

    session = copy.deepcopy(MangaApi.session)
    session.headers.update({"referer": source_url})

    @classmethod 
    def fetch_chapter(cls, chapter_url, chapter_dir=None):
        content = cls.request(chapter_url, method="GET").content
        bs = BeautifulSoup(content, features="lxml")
        
        chapterImages = re.search(r"var chapterImages = (.*?);var chapterPath = ", str(bs)).group(1)
        chapterImages = [i.replace('\\', '') for i in chapterImages[1:-1].replace(',', '').split('\"') if i != '']
        page_total = len(chapterImages)

        images_info = []
        desc = '\rFetching {}: ({}/{})'
        for i in range(page_total):
            print(desc.format(chapter_url, i+1, page_total), end='\r')
            # skip exists image
            if chapter_dir is not None and os.path.isdir(chapter_dir):
                if os.path.exists(os.path.join(chapter_dir, str(i+1)+'.jpg')) or\
                   os.path.exists(os.path.join(chapter_dir, str(i+1)+'.png')):
                   continue
                            
            img_url = 'https://ykimg.zzszs.com.cn' + chapterImages[i]
            img_name = str(i+1) + os.path.splitext(cls.url2fn(img_url))[-1]

            images_info.append({
                'fname': img_name,
                'url': img_url,
            })

        return images_info

    @classmethod
    def fetch_manga(cls, manga_url):
        content = cls.request(manga_url, method="GET").content
        bs = BeautifulSoup(content, features="lxml")

        # details
        manga_info = bs.find('div', {'class': 'comic_deCon'})
        manga_title = manga_info.find('h1').text.strip()
        status = manga_info.find('ul', {'class': 'comic_deCon_liO'}).find_all('li')[1].find('a').text
        latest = '-'

        # chapters
        chapters_div = bs.find_all('div', {'class': 'zj_list'})

        chapters = []
        if chapters_div != []:
            for v in chapters_div:
                c_title = v.find('div', {'class': 'zj_list_head'}).find('h2').text.strip()
                cs = v.find('div', {'class': 'zj_list_con'}).find_all('li')
                for c in cs:
                    c = c.find('a')
                    title = c.find('span', {'class': 'list_con_zj'}).text.strip()
                    url = cls.source_url + c.get('href')
                    chapters.append({
                        'title': validate_title(c_title) + '/' + validate_title(title),
                        'url': url,
                        })
        
        manga_info = {
            'title': validate_title(manga_title),
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
            search_url = cls.source_url + '/search/?keywords={}&page={}'.format(keyword, page_num)
            content = cls.request(search_url, method="GET").content
            bs = BeautifulSoup(content, features="lxml")

            # check next page exists
            if bs.find('div', {'class': 'empty'}):
                break

            lis = bs.find('div', {'id': 'w0'}).find_all('li', {'class': 'list-comic'})
            manga_urls.extend([li.find('a').get('href') for li in lis])

            if len(manga_urls) >= max_num:
                return manga_urls[:max_num]

            # check next page exists
            page_nav = bs.find('ul', {'class': 'pagination'})
            if page_nav is None or ('disabled' in page_nav.find('li', {'class': 'last'}).get('class')):
                break

        return manga_urls

    @classmethod
    def url2fn(cls, url):
        fn = url.split('/')[-1].split('?')[0]
        return fn
    





