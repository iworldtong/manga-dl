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


class Dogemanga(MangaApi):

    source = 'dogemanga'
    source_url = config.get('source2url')[source]

    session = copy.deepcopy(MangaApi.session)
    session.headers.update({"referer": source_url})
    if config.get("auto_proxy"):
        MangaApi.auto_set_proxy(source)

    @classmethod
    def fetch_image_js(cls, url):
        cls.session.headers.update({"referer": url})
        html = cls.request(url, method="GET")
        cls.session.headers.update({"referer": cls.source_url})

        bs = BeautifulSoup(html.content, features="lxml")
        js_slic = re.search(r">window.*(\(function\(p.*?)</script>", str(bs)).group(1)
        core_str = re.search(r"[0-9],'([A-Za-z0-9+/=]+?)'", js_slic).group(1)
        dec_str = lzstring.LZString.decompressFromBase64(core_str)
        js_new = re.sub(r"'[A-Za-z0-9+/=]*'\[.*\]\('\\x7c'\)", "'" + dec_str + "'.split('|')", js_slic)
        sol = execjs.eval(js_new)
        return json.loads(re.search(r"(\{.*\})", sol).group(1))

    @classmethod 
    def fetch_chapter(cls, chapter_url, chapter_dir=None):
        content = cls.request(chapter_url, method="GET").content
        bs = BeautifulSoup(content, features="lxml")
        img_box_bs = bs.find('div', {'id': 'site-page-slides-box'})

        images_info = []
        for img_bs in img_box_bs.find_all('img', {'class': 'site-page-slide'}):
            img_url = img_bs.get('data-src')
            if img_url is None:
                continue
            
            img_name = img_bs.get('site-page-index')+'.'+img_url.split('.')[-1]

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
        manga_title = bs.find('h2', {'class': 'site-red-dot-box'}).text.strip()
        manga_info = bs.find('ul', {'class': 'list-unstyled'})
        status = manga_info.find_all('li')[0].text.split('：')[-1]
        latest = manga_info.find_all('li')[1].text.split('：')[-1]        

        # chapters
        chapters_div = bs.find('div', {'id': 'site-manga-all'})        
        chapters = []
        if chapters_div != None:
            for c in chapters_div.find_all('div', {'class': 'site-page-thumbnail-icons-box'}):

                title = c.find('a', {'class': 'site-link'}).text.strip()
                url = c.find('a', {'class': 'site-link'}).get('href')                
                chapters.append({
                    'title': validate_title(title),
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
            search_url = cls.source_url + '/s/{}_p{}.html'.format(keyword, page_num)
            content = cls.request(search_url, method="GET").content
            bs = BeautifulSoup(content, features="lxml")
            
            # check next page exists
            if bs.find('div', {'id': 'PanelNoResult'}):
                break

            lis = bs.find('div', {'class': 'book-result'}).find_all('li', {'class': 'cf'})
            manga_urls.extend([cls.source_url+li.find('a').get('href') for li in lis])

            if len(manga_urls) >= max_num:
                return manga_urls[:max_num]

        return manga_urls

    @classmethod
    def url2fn(cls, url):
        fn = url.split('/')[-1].split('?')[0]
        return fn
    





