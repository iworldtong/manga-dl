#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author: muketong
@file: source.py
@time: 2020-08-15
"""

"""
    Manga source proxy object
"""

import re
import threading
import importlib
import traceback
import logging
import click

from . import config
from .utils import colorize
from .exceptions import *
from .manga import BasicManga
from .addons import * 


class MangaSource:
    """
        Manga source proxy object
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def search(self, keyword, sources_list) -> list:
        source2url = config.get('source2url')
        thread_pool = []
        ret_mangas_list = []
        ret_errors = []

        click.echo("")
        click.echo(
            _("Searching {keyword} from ...").format(
                keyword=colorize(config.get("keyword"), "highlight")
            ),
            nl=False,
        )

        for source in sources_list:
            if not source in source2url.keys():
                raise ParameterError("Invalid manga source.")

            t = threading.Thread(
                target=self.search_thread,
                args=(source, keyword, ret_mangas_list, ret_errors),
            )
            t.start()
            thread_pool.append(t)

        for t in thread_pool:
            t.join()
        
        click.echo("")
        # 输出错误信息
        for err in ret_errors:
            self.logger.debug(_("漫画列表 {error} 获取失败.").format(error=err[0].upper()))
            self.logger.debug(err[1])

        # 对搜索结果排序和去重
        if not config.get("nomerge"):
            ret_mangas_list.sort(
                key=lambda song: (song.title, song.all_chapters), reverse=True
            )
            tmp_list = []
            for i in range(len(ret_mangas_list)):
                # 根据漫画标题去重，保留章节数较多的漫画
                if (
                    i > 0
                    and len(ret_mangas_list[i].all_chapters) <= len(ret_mangas_list[i - 1].all_chapters)
                    and ret_mangas_list[i].title == ret_mangas_list[i - 1].title
                ):
                    continue
                tmp_list.append(ret_mangas_list[i])
            ret_mangas_list = tmp_list

        return ret_mangas_list

    def search_thread(self, source, keyword, ret_mangas_list, ret_errors):
        try:
            api = getattr(importlib.import_module(".addons.{}".format(source), __package__), source.title())
            manga_urls = api.fetch_keyword(keyword, config.get('number'))
            for url in manga_urls:
                manga = BasicManga(source)
                manga.single(url)
                ret_mangas_list.append(manga)

        except (RequestError, ResponseError, DataError) as e:
            ret_errors.append((source, e))
        except Exception as e:
            # 最后一起输出错误信息免得影响搜索结果列表排版
            # print(e)
            err = traceback.format_exc() if config.get("verbose") else str(e)
            ret_errors.append((source, err))
        finally:
            # 放在搜索后输出是为了营造出搜索很快的假象
            click.echo(" %s ..." % colorize(source.title(), source), nl=False)

    def single(self, url):
        source2url = config.get('source2url')

        sources = [s for s, u in source2url.items() if u.replace('https://www.', '') in url]
        if not sources:
            raise ParameterError("Invalid url.")
        source = sources[0]
        click.echo(_("Downloading manga from %s ..." % source.title()))
        try:
            manga = BasicManga(source)
            manga.single(url)
            return manga
        except (RequestError, ResponseError, DataError) as e:
            self.logger.error(e)
        except Exception as e:
            # 最后一起输出错误信息免得影响搜索结果列表排版
            err = traceback.format_exc() if config.get("verbose") else str(e)
            self.logger.error(err)


