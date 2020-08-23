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


class Manhuagui(MangaApi):

    source_url = config.get('source2url')['manhuagui']

    session = copy.deepcopy(MangaApi.session)
    session.headers.update({"referer": source_url})

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
        data = cls.fetch_image_js(chapter_url)
        page_total = len(data['files'])

        images_info = []
        desc = '\rFetching {}: ({}/{})'
        for i in range(page_total):
            print(desc.format(chapter_url, i+1, page_total), end='\r')
            # skip exists image
            if chapter_dir is not None and os.path.isdir(chapter_dir):
                if os.path.exists(os.path.join(chapter_dir, str(i+1)+'.jpg')) or\
                   os.path.exists(os.path.join(chapter_dir, str(i+1)+'.png')):
                   continue
                
            pic = data['files'][i]
            mangaurl = 'https://i.hamreus.com' + data['path'] + re.match(r".*?\.[a-z]*", pic).group(0)
            
            img_url = mangaurl + "?cid=" + str(data['cid']) + "&md5=" + data['sl']['m']
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
        manga_title = bs.find('div', {'class': 'book-title'}).find('h1').text.strip()
        manga_info = bs.find('li', {'class': 'status'}).find('span')
        status = manga_info.find_all('span')[0].text
        date = manga_info.find_all('span')[1].text
        latest_chapter = manga_info.find('a', {'class': 'blue'}).text
        latest = date + ' ' + latest_chapter

        # chapters
        if bs.find('div', {'id': 'chapter-list-0'}) is not None:
            chapters_div = bs.find('div', {'id': 'chapter-list-0'})
        elif bs.find('div', {'id': 'chapter-list-1'}) is not None:
            chapters_div = bs.find('div', {'id': 'chapter-list-1'})
        else:
            chapters_div = []

        chapters = []
        if chapters_div != []:
            for c in chapters_div.find_all('a'):
                title = c.get('title').strip()
                url = cls.source_url + c.get('href')
                page_num = re.findall(r"\d+\.?\d*", c.find('i').text)[0]
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
    





