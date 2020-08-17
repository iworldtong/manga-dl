#!/usr/bin/env python
# -*- coding:utf-8 -*-


from manga_dl.source import MangaSource


def test_search():
    ms = MangaSource()
    mangas_list = ms.search("进击的巨人", ["manhuabei"])
    assert mangas_list is not None


# def test_single():
#     ms = MangaSource()
#     manga = ms.single("https://www.manhuabei.com/manhua/jinjidejuren/")
#     assert manga is not None

