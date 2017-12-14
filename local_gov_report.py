#!/usr/bin/python
#coding=utf-8


"""
@author: Li Bin
@date: 2017-12-13
"""


import requests
import urllib.request
from bs4 import BeautifulSoup


local_reports_collect_url = "http://district.ce.cn/zg/201702/26/t20170226_20529710.shtml"


def get_standard_html(url):
    """获取汇总合集页面的标准 HTML 文本
    
    :return: 
    """
    html_doc = urllib.request.urlopen(url)
    standard_html = BeautifulSoup(html_doc, 'html.parser')
    return standard_html


def filter_report_collect_url(standard_html):
    """过滤汇总页面中历年地方政府报告 URL 
    
    :return: url_dict
    """
    url_dict = []
    raw_html_text = standard_html.find_all('div', class_='TRS_Editor')
    html_text = raw_html_text[0].find_all('a')
    for text in html_text:
        temp_dict = {
            'year': text.get_text(),
            'url': text.get('href')
        }
        url_dict.append(temp_dict)
    return url_dict


def filter_local_gov_report_url(url):
    """
    
    :param url: 
    :return: 
    """
    local_gov_report_url = []
    standard_html = get_standard_html(url)
    raw_html_text = standard_html.find_all('div', class_='TRS_Editor')
    html_text = raw_html_text[0].find_all('a')
    for text in html_text:
        temp_dict = {
            'report_title': text.get_text(),
            'report_url': text.get('href')
        }
        local_gov_report_url.append(temp_dict)
    return local_gov_report_url


def get_report_text(local_report_url):
    """从报告发布页 URL 地址获取报告正文
    
    :param local_report_url: 
    :return: 
    """
    standard_html = get_standard_html(local_report_url)
    raw_html_text = standard_html.find_all('div', class_='TRS_Editor')
    text = raw_html_text[0].get_text()
    return text


def get_pagination_url(url):
    standard_html = get_standard_html(url)
    laiyuan = standard_html.find_all('span')
    print(laiyuan)


if __name__ == '__main__':
    # html = get_standard_html(local_reports_collect_url)
    # a = filter_report_collect_url(html)
    # html_text = get_report_text('http://district.ce.cn/newarea/roll/201702/07/t20170207_20015641.shtml')
    # get_pagination_url('http://district.ce.cn/newarea/roll/201702/07/t20170207_20015641.shtml')
    filter_local_gov_report_url('http://district.ce.cn/zg/201702/26/t20170226_20528713.shtml')