#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: muketong
@file: basic.py
@time: 2020-08-15
"""

"""
    Basic manga object
"""

import os
import re
import time
import copy
import datetime
import logging
import click
import requests
import importlib

from . import config
from .pick import pick
from .utils import colorize, validate_title, retry_get, DownloadThread
from .addons import * 


from tqdm import tqdm
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
class DownloadProgressBar(FileSystemEventHandler):
    def __init__(self, watch_dir, total_num, desc):
        self.watch_dir = watch_dir
        self.pbar = tqdm(total=total_num, desc=desc, ncols=os.get_terminal_size().columns-10)
        self.last_num = 0
        self.total_num = total_num

    def on_any_event(self, event):
        self.update()

    def update(self, end=False):
        fl = [f for f in os.listdir(self.watch_dir) if not f.endswith('.part')]
        cur_num = len(fl)
        update_num = cur_num - self.last_num
        self.last_num = cur_num
        self.pbar.update(update_num) 
        if end and self.last_num != self.total_num:
            print()


class BasicManga:
    """
        Define the basic properties and methods of a manga.
        Such as title, status, lastest chapter etc.
    """

    def __init__(self, source=None, n_workers=20):
        self.idx = 0
        self.n_workers = n_workers 

        self.source = source.lower()
        self.addons = importlib.import_module(".addons.{}".format(source), __package__)
        self.api = getattr(self.addons, self.source.title())

        self.title = ""
        self.status = ""
        self.latest = ""
        self.manga_url = ""

        self.manga_info = dict()
        self.all_chapters = list()
        self.picked_chapters = list()
        self.save_dir = config.get('outdir')

        self.logger = logging.getLogger(__name__)

    def __str__(self):
        """ Song details """
        source = colorize("%s" % self.source.title(), self.source)
        return _(
            " -> source: {source}\n"
            " -> Title: {title}\n"
            " -> Status: {status}\n"
            " -> Latest: {latest}\n"
            " -> Chapters: {chapters}\n"
            " -> Manga URL: {manga_url}"
        ).format(
            source=source,
            title=self.title,
            status=self.status,
            latest=self.latest,
            chapters='共 {} 章'.format(len(self.all_chapters)),
            manga_url=self.manga_url,
        )

    @property
    def row(self) -> list:
        """ Manga details in list form """

        def highlight(s, k):
            return s.replace(k, colorize(k, "yellow")).replace(
                k.title(), colorize(k.title(), "yellow")
            )

        ht_title = self.title if len(self.title) < 30 else self.title[:30] + "..."

        if config.get("keyword"):
            keywords = re.split(";|,|\s|\*", config.get("keyword"))
            for k in keywords:
                if not k:
                    continue
                ht_title = highlight(ht_title, k)

        return [
            colorize(self.idx, "cyan"),
            ht_title,
            self.status,
            self.latest,
            '共 {} 章'.format(len(self.all_chapters)),
            self.source.title(),
        ]

    def _download_images(self, images, save_dir, desc=''):
        """
            Helper function for download
        :param url:
        :param outfile:
        :return:
        """
        if len(images) == 0:
            return

        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)

        # watch folder
        event_handler = DownloadProgressBar(save_dir, len(images), desc=desc)
        observer = Observer()
        observer.schedule(event_handler, path=save_dir) 
        observer.start()

        try_num = 0
        max_retry_num = 10
        while len(images) > 0:
            try_num += 1
            if try_num > max_retry_num:
                click.echo("")
                self.logger.error(_("Download failed: "))
                self.logger.error(_("Failed images: {images}").format(images=images))
                self.logger.error(_("File location: {save_dir}").format(save_dir=save_dir))
                if config.get("verbose"):
                    self.logger.error(e)
                break

            e_pnt = 0
            while e_pnt < len(images):
                s_pnt = e_pnt
                e_pnt = min(s_pnt+self.n_workers, len(images))
                # download
                thread_pool = []
                for image in images[s_pnt:e_pnt]:                    
                    save_path = os.path.join(save_dir, image['fname'])
                    t = DownloadThread(image['url'], save_path, \
                                       headers=self.api.session.headers,\
                                       proxies=self.api.session.proxies)
                    t.start()
                    thread_pool.append(t)

                for t in thread_pool:
                    t.join()

                time.sleep(0.5)

            # check done
            tmp_images = []
            for image in images:
                if not os.path.exists(os.path.join(save_dir, image['fname'])):
                    tmp_images.append(image)
            images = tmp_images

        event_handler.update(end=True)
        observer.stop()
        observer.join()
            
    def download_chapters(self, chapters):
        for i, c in enumerate(chapters):
            click.echo("Fetching {}".format(c['url']), nl=False)

            images = self.api.fetch_chapter(c['url'])
            save_dir = os.path.join(config.get('outdir'), self.title, c['title'])
            desc = '[{}/{}] {}'.format(i+1, len(chapters), c['title'])

            self._download_images(images, save_dir, desc)

    def select_chapters(self, chapters_list) -> list:
        options = [c['title'] for c in chapters_list]        
        ret = pick(options, title='Please choose chapters to download (select: <space>/→; select all: a; toggle all: t; resort all: r):',\
                   default_index=list(range(len(chapters_list))), multiselect=True)

        selected_titles = [i[0] for i in ret]
        select_chapters = [c for c in chapters_list if c['title'] in selected_titles]
        return select_chapters

    def download(self):
        """ Main download function """
        click.echo("===============================================================")
        if config.get("verbose"):
            click.echo(str(self))
        else:
            click.echo(" | ".join(self.row))
        click.echo("---------------------------------------------------------------")
        if input('Continue? [Y|n]') not in ['y', 'Y', '']:
            return

        if config.get('download_all'):
            self.picked_chapters = self.all_chapters
        else:
            self.picked_chapters = self.select_chapters(self.all_chapters)
            
        self.download_chapters(self.picked_chapters)

        click.echo("===============================================================\n")

    def single(self, url):
        manga_info = self.api.fetch_manga(url)

        self.manga_url = url
        self.title = validate_title(manga_info['title'])
        self.status = manga_info['status']
        self.latest = manga_info['latest']
        self.all_chapters = manga_info['chapters']


