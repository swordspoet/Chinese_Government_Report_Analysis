#!/usr/bin/python
#-*- coding:utf-8 -*-


"""
@author: Li Bin
@date: 2017-12-13
"""


import configparser as ConfigParser
import random
import re
import requests
import time
import urllib.request
from bs4 import BeautifulSoup


config = ConfigParser.ConfigParser()
config.read('config.ini')
local_reports_collect_url = config['url']['collect_url']
root_file_path = config['file_path']['root_directory']


def get_standard_html(url):
    """获取汇总合集页面的标准 HTML 文本
    :return: 
    """
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    try:
        html_doc = urllib.request.urlopen(req, timeout=60)
        html_doc.encoding = "utf-8"
        standard_html = BeautifulSoup(html_doc, 'html5lib')
        return standard_html
    except Exception as e:
        print("有错误！")
        pass


def filter_report_collect_url(standard_html):
    """过滤得到汇总页面中历年地方政府报告合集页面的 URL
    :return: url_dict，
    [{'year': "2017年汇编", 'url': 'http://district.ce.cn/zg/201702/26/t20170226_20528713.shtml'}]
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
    """地方政府报告合集页面的省市发布的 URL
    :param url: 
    :return: 
    [{'report_title': '北京市政府工作报告 (2017年1月14日 蔡奇)', 
    'report_url': 'http://district.ce.cn/newarea/roll/201702/07/t20170207_20015641.shtml'}]
    """
    local_gov_report_url_dict = []
    standard_html = get_standard_html(url)
    # standard_html.decode('gb2312').encode('utf8')
    raw_html_text = standard_html.find_all('div', class_='TRS_Editor')
    if len(raw_html_text) > 0:
        html_text = raw_html_text[0].find_all('a')
        for text in html_text:
            temp_dict = {
                'report_title': text.get_text(),
                'report_url': text.get('href')
            }
            local_gov_report_url_dict.append(temp_dict)
    else:
        raw_html_text = standard_html.find_all('div', class_='content')
        html_text = raw_html_text[0].find_all('a')
        for text in html_text:
            temp_dict = {
                'report_title': text.get_text(),
                'report_url': text.get('href')
            }
            local_gov_report_url_dict.append(temp_dict)
    return local_gov_report_url_dict


def get_annual_report_url_list(url_dict):
    """
    获取所有的省市报告地址
    :param url_dict: 
    :return: 
    """
    annual_report_url_list = []       # 年度省（直辖市）报告 URL 列表：2003-2017 年所有省市报告的地址
    for item in url_dict:
        report_url = item.get('url')  # report_url 是某年报告汇编的地址，如“2017年汇编”
        local_gov_report_url = filter_local_gov_report_url(report_url)
        annual_report_url_list.append(local_gov_report_url)
        print(report_url)
        time.sleep(2)
    return annual_report_url_list


def get_report_text(url):
    """从 URL 地址获取网页正文部分
    :param local_report_url: 
    :return: 
    """
    standard_html = get_standard_html(url)
    if standard_html:
        raw_html_text = standard_html.find_all('p')
        text = []
        for item in raw_html_text:
            text.append(item.get_text())
        return text


def get_page_sum(url):
    """
    获取报告总页数：共（n）页
    :param url: 
    :return: 
    """
    standard_html = get_standard_html(url)
    tmp_html = standard_html.find_all('script', language='JavaScript')
    tmp_str = re.findall(r'[^createPageHTML(].*[$,]', str(tmp_html))
    page_sum = tmp_str[1][16]
    return int(page_sum)


def generate_page_urls(url, page_sum):
    """
    当报告有多个页面时，生成多页面的 URL
    :param page_num_sum: 
    :return: 
    """
    i = 1
    url_list = [url]
    while i < page_sum:
        page_url = ''.join([url[:-6], '_', str(i), '.shtml'])
        url_list.append(page_url)
        i += 1
    return url_list


def crawl_province_report(report_title, province_report_url):
    """抓取报告全文并写入 txt 
    
    """
    global file_path
    page_sum = get_page_sum(province_report_url)
    url_list = generate_page_urls(province_report_url, page_sum)
    text = []
    for page_url in url_list:
        tmp_text = get_report_text(page_url)
        text.append(tmp_text)
        file_path = root_file_path + str(report_title) + '.txt'
        print(page_url)
        time.sleep(random.randint(0, 9))
    flatten_text =  [item for sublist in text for item in sublist]
    report_text_handler = open(file_path, "ab+")
    for item in flatten_text:
        report_text_handler.write((item + '\r\n').encode('UTF-8'))
        print('正在写入文件...')


def get_all_report(annual_report_url_list):
    """
    从省市报告地址中提取出网页正文，并写入 TXT 文件
    :param annual_report_url_list: 
    :return: 
    """
    for item in annual_report_url_list:
        for sub_item in item:
            report_title = sub_item.get('report_title')
            province_report_url = sub_item.get('report_url')
            if re.match(r'^https?:/{2}\w.+$', province_report_url) and \
                    re.match(r'[^?!(\d) | ^?!(（)]', report_title) and len(report_title) > 6:
                crawl_province_report(report_title, province_report_url)
            time.sleep(2)


if __name__ == '__main__':
    a = get_standard_html(local_reports_collect_url)
    b = filter_report_collect_url(a)
    d = get_annual_report_url_list(b)
    # get_all_report(d)
    # a = get_page_sum('http://district.ce.cn/newarea/roll/201702/07/t20170207_20020701.shtml')
    # b = get_report_text('http://district.ce.cn/newarea/roll/201702/07/t20170207_20020701.shtml')
