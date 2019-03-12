#!/usr/bin/python
# -*- coding:UTF-8 -*-

"""
豆瓣top N 电影数据抓取
"""

import requests
from bs4 import BeautifulSoup


def text_clean(text):
    temp = text.strip().replace(' ', '').replace('\n', '')
    return temp


def spider_douban_top_movie(num):
    if num >= 250:
        page = 10
    elif num <= 25:
        page = 1
    else:
        page = num / 25 + 1
    url = "https://movie.douban.com/top250?start="
    content = []

    index = 1
    for i in range(page):
        current_url = url + str(i * 25)
        html = requests.get(current_url)
        soup = BeautifulSoup(html.text, 'html.parser')

        for item in soup.find_all('div', 'info'):
            movie_title = item.div.a.span.string
            movie_year = text_clean(item.find('div', 'bd').p.contents[1].string)[0:4]
            movie_rating = item.find('span', 'rating_num').string
            line = str(index) + '\t' + movie_title + '\t' + movie_year + '\t' + movie_rating
            content.append(line)
            if index >= num:
                break
            else:
                index = index + 1

    return content


if __name__ == "__main__":
    for item in spider_douban_top_movie(30):
        print item
