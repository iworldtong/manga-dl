import os
import re
import copy
import pyaes
import execjs
import base64
import requests
from bs4 import BeautifulSoup

from .. import config
from ..api import MangaApi
from ..utils import validate_title


class Manhuabei(MangaApi):

    source_url = config.get('source2url')['manhuabei']

    session = copy.deepcopy(MangaApi.session)
    session.headers.update({"referer": source_url})


    @classmethod
    def fetch_image_js(cls, url):
        cls.session.headers.update({"referer": url})
        html = cls.request(url, method="GET")
        cls.session.headers.update({"referer": cls.source_url})

        # find Key and IV
        js_fix = re.search('/js/decrypt[0-9]+.js', html.text).group(0)
        js_str = cls.request(cls.source_url + js_fix, method="GET").text
        IV_encrypted = re.findall("iv':(_.*?),", js_str)[0] #_0x1c8ae7
        IV_searchkey = re.findall('var ' + IV_encrypted + ".*?\['parse'\].*?\[(.*?\'\))\]\);", js_str)[0]  #_0x4936('2d','OO8Z')
        IV_searchvalue = execjs.compile(js_str).eval(IV_searchkey) #TOtFq
        IV_searchkey2 = re.findall(IV_searchvalue + "':(_.*?)};", js_str)[0] #_0x4936('22', 'CA]!')
        IV = execjs.compile(js_str).eval(IV_searchkey2)
        IV = IV.encode(encoding="utf-8")

        KEY_encrypted = re.findall("chapterImages,(.*?),", js_str)[0] #_0xd4450f
        KEY_searchkey =re.findall('var ' + KEY_encrypted + ".*?\['enc'\].*?\((_.*?\))\);", js_str)[0]  #_0x4936('30','eo!$')
        KEY = execjs.compile(js_str).eval(KEY_searchkey) 
        KEY = KEY.encode(encoding="utf-8")

        chapterPath = re.search(r"var chapterPath = \"(.*?)\";var chapterPrice", html.text).group(1)
        chapterImages_base64 = re.search(r"var chapterImages = (.*?);var chapterPath = ", html.text).group(1)

        encrypted_str = base64.b64decode(chapterImages_base64)
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(KEY, IV))
        decrypted_str = decrypter.feed(encrypted_str) 
        decrypted_str += decrypter.feed()

        output = re.sub(r'[\[\]\"\\]', '', decrypted_str.decode("utf-8"))
        output = output.split(',')

        return chapterPath, output

    @classmethod 
    def fetch_chapter(cls, chapter_url, chapter_dir=None):
        chapterPath, output = cls.fetch_image_js(chapter_url)
        page_total = len(output)

        images_info = []
        desc = '\rFetching {}: ({}/{})'
        for i in range(page_total):
            print(desc.format(chapter_url, i+1, page_total), end='\r')
            # skip exists image
            if chapter_dir is not None and os.path.isdir(chapter_dir):
                if os.path.exists(os.path.join(chapter_dir, str(i+1)+'.jpg')) or\
                   os.path.exists(os.path.join(chapter_dir, str(i+1)+'.png')):
                   continue

            item = output[i]
            if 'http' in item:
                img_url = 'https://img01.eshanyao.com/showImage.php?url=' + item.replace("%", "%25")
            else:
                img_url = 'https://img01.eshanyao.com/' + chapterPath + item

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
        manga_title = bs.find('div', {'class': 'comic_deCon'}).find('h1').text.strip()
        manga_title = validate_title(manga_title)
        status = bs.find('ul', {'class': 'comic_deCon_liO'}).find_all('li')[1].find('a').text.strip()
        latest = '-'
        if status == '连载中':
            date = bs.find('span', {'class': 'zj_list_head_dat'}).text
            date = re.sub(r'[\更新时间：\[\]]', '', date).strip()
            latest = date

        # chapters
        chapters = []
        if bs.find('ul', {'id': 'chapter-list-1'}) is not None:
            chapters_list = bs.find('ul', {'id': 'chapter-list-1'})
            for c in chapters_list.find_all('a'):
                title = c.get('title').strip()
                url = cls.source_url + c.get('href')

                chapters.append({
                    'title': validate_title(title),
                    'url': url,
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
            search_url = cls.source_url + '/search/?keywords={}&page={}'.format(keyword, page_num)
            content = cls.request(search_url, method="GET").content
            bs = BeautifulSoup(content, features="lxml")
            lis = bs.find('div', {'id': 'w0'}).find_all('li', {'class': 'list-comic'})
            manga_urls.extend([li.find('a').get('href') for li in lis])

            if len(manga_urls) >= max_num:
                return manga_urls[:max_num]

            # check next page exists
            page_nav = bs.find('url', {'class': 'pagination'})
            if page_nav is None or page_nav.find('li', {'class': 'next'}).find('a') is None:
                break

        return manga_urls

    @classmethod
    def url2fn(cls, url):
        fn = url.split('/')[-1].split('?')[0]
        return fn
    





