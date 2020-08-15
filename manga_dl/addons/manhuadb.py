import os
import re
import execjs
import urllib.parse
from tqdm import tqdm
from bs4 import BeautifulSoup

from .. import config
from ..api import MangaApi
from ..utils import retry_get, validate_title



class Manhuadb:
    source_url = config.get('source2url')['manhuadb']
    headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            }

    proxies = config.get('proxies')


    @classmethod
    def fetch_chapter(cls, chapter_url, chapter_dir=None):
        content = retry_get(chapter_url, proxies=cls.proxies).content
        bs = BeautifulSoup(content, features="lxml")

        page_total = bs.find('ol', {'class': 'breadcrumb'}).find_all('li')[-1].text
        page_total = int(re.findall(r'共 (\d*) 页', page_total)[0])

        images = []
        desc = '\rFetching {}: ({}/{})'
        for i in range(page_total):
            print(desc.format(chapter_url, i+1, page_total), end='\r')
            # skip exists image
            if chapter_dir is not None and os.path.isdir(chapter_dir):
                if os.path.exists(os.path.join(chapter_dir, str(i+1)+'.jpg')) or\
                   os.path.exists(os.path.join(chapter_dir, str(i+1)+'.png')):
                   continue

            page_url = '.'.join(chapter_url.split('.')[:-1]) + '_p' + str(i + 1) + '.' + chapter_url.split('.')[-1]
            content = retry_get(page_url, proxies=cls.proxies).content
            page_bs = BeautifulSoup(content, features='lxml')
            img_url = page_bs.find_all('img', {'class': ['img-fluid', 'show-pic']})[0].get('src')
            img_name = str(i+1) + os.path.splitext(cls.url2fn(img_url))[-1]

            images.append({
                'fname': img_name,
                'url': img_url,
            })
        print(' ' * os.get_terminal_size().columns, end='\r')
        return images

    @classmethod
    def fetch_manga(cls, manga_url):
        content = retry_get(manga_url, proxies=cls.proxies).content
        bs = BeautifulSoup(content, features="lxml")

        # details
        manga_title = bs.find('h1', {'class': 'comic-title'}).text.strip()
        manga_title = validate_title(manga_title)
        table = bs.find('table', {'class': 'comic-meta-data-table'})
        status = table.find('a', {'class': 'comic-pub-state'}).text
        latest = '-'

        # chapters
        comic_versions_span = bs.find('ul', {'id': 'myTab'}).find_all('span', {'class': 'comic_version'})
        comic_versions = [span.text.strip() for span in comic_versions_span]
        chapters_div = bs.find('div', {'id': 'comic-book-list'}).find_all('div', {'class': 'tab-pane'})
        
        chapters = []
        for i in range(len(comic_versions)):
            items = chapters_div[i].find('ol', {'class': 'links-of-books'}).find_all('li')
            for c in items:
                title = c.find('a').text
                url = cls.source_url + c.find('a').get('href')

                chapters.append({
                    'title': os.path.join(comic_versions[i], validate_title(title)),
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
            search_url = cls.source_url + '/search?q={}&p={}'.format(keyword, page_num)
            content = retry_get(search_url, proxies=cls.proxies).content
            bs = BeautifulSoup(content, features="lxml")

            container = bs.find('div', {'class': 'comic-main-section'})
            if container.find('div', {'class': 'alert-warning'}):
                break

            items = container.find('div', {'class': 'row'}).find_all('div', {'class': 'comicbook-index'})
            manga_urls = [cls.source_url + i.find('a', {'class': 'd-block'}).get('href') for i in items]
            
            if len(manga_urls) >= max_num:
                return manga_urls[:max_num]

        return manga_urls

    @classmethod
    def url2fn(cls, url):
        fn = url.split('/')[-1]
        return fn



