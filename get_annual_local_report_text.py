#!/usr/bin/python
#-*- coding:utf-8 -*-


"""
@author: Li Bin
@date: 2017-12-17
"""


import configparser as ConfigParser
import logging
import pandas as pd
import random
import re
import time
import urllib.request
from bs4 import BeautifulSoup


config = ConfigParser.ConfigParser()
config.read('config.ini')
local_reports_collect_url = config['url']['collect_url']
file_path = config['file_path']['url_data_file']
root_file_path = config['file_path']['root_directory']


def read_url(annual_report_url_list_file_path):
    """
    读取 CSV 文件
    :return: 
    """
    df = pd.read_csv(annual_report_url_list_file_path, encoding='gbk')
    return df


def get_standard_html(url):
    """获取汇总合集页面的标准 HTML 文本
    :return: 
    """
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/63.0.3239.84 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    try:
        html = urllib.request.urlopen(req, timeout=60).read()
        standard_html = BeautifulSoup(html, 'html5lib')
    except Exception as e:
        logging.info(url + "抓取超时......")
        standard_html = None
        pass
    return standard_html


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
    else:
        return None


def get_page_sum(url):
    """
    获取报告总页数：共（n）页
    :param url: 
    :return: 
    """
    standard_html = get_standard_html(url)
    if standard_html:
        try:
            tmp_html = standard_html.find_all('script', language='JavaScript')
            tmp_str = re.search(r'createPageHTML\((\d+)', str(tmp_html))
            page_sum = tmp_str.group(1)
        except:
            page_sum = 1
        return int(page_sum)  # 如果 standard_html 为 None，则返回 1，至少抓一页


def generate_page_urls(url, page_sum):
    """
    当报告有多个页面时，生成多页面的 URL
    :param page_num_sum: 
    :return: 
    """
    i = 1
    url_list = [url]
    try:
        while i < page_sum:
            page_url = ''.join([url[:-6], '_', str(i), '.shtml'])
            url_list.append(page_url)
            i += 1
    except Exception:
        url_list = [url]
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
        print('正在抓取' + str(report_title) + '......')
        time.sleep(random.randint(0, 9))
    try:
        flatten_text = [item for sublist in text for item in sublist]
        report_text_handler = open(file_path, "ab+")
        for item in flatten_text:
            report_text_handler.write((item + '\r\n').encode('UTF-8'))
            print('正在写入文件......')
    except Exception:
        pass


def get_all_report():
    """
    从省市报告地址中提取出网页正文，并写入 TXT 文件
    :param annual_report_url_list: 
    :return: 
    """
    url_list_df = read_url(file_path)
    for item in url_list_df.iterrows():
        report_title = item[1]['report_title']
        province_report_url = item[1]['report_url']
        crawl_province_report(report_title, province_report_url)
    time.sleep(3)


if __name__ == '__main__':
    get_all_report()
