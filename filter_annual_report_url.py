#!/usr/bin/python
#-*- coding:utf-8 -*-


"""
@author: Li Bin
@date: 2017-12-13
"""


import configparser as ConfigParser
import csv
import logging
import re
import time
import urllib.request
from bs4 import BeautifulSoup


config = ConfigParser.ConfigParser()
config.read('config.ini')
local_reports_collect_url = config['url']['collect_url']
file_path = config['file_path']['url_data_file']


def get_standard_html(url):
    """获取网页的标准 HTML 文本
    :return: 
    """
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/63.0.3239.84 Safari/537.36'}
    req = urllib.request.Request(url=url, headers=headers)
    try:
        html = urllib.request.urlopen(req, timeout=60).read()
        standard_html = BeautifulSoup(html, 'html5lib')
    except Exception as e:  # 如果抓取失败则退出，并令 standard_html 为 None
        logging.info(url + "抓取超时......")
        standard_html = None
        pass
    return standard_html


def filter_report_collect_url(standard_html):
    """从 standard_html 中过滤得到历年地方政府报告合集页面的 URL
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
    """地方政府报告合集页面的省市报告的 URL
    :param url: 
    :return: 
    [{'report_title': '北京市政府工作报告 (2017年1月14日 蔡奇)', 
    'report_url': 'http://district.ce.cn/newarea/roll/201702/07/t20170207_20015641.shtml'}]
    """
    local_gov_report_url_dict = []
    standard_html = get_standard_html(url)
    raw_html_text = standard_html.find_all('div', class_='TRS_Editor')
    """个别网页的链接在 div 标签的 content 类中"""
    if len(raw_html_text) > 0:
        html_text = raw_html_text[0].find_all('a')
        for text in html_text:
            temp_dict = {
                'report_title': (text.get_text()).replace('\xa0', '').replace('资料:', ''),  # 1. 替换 \xa0，防止写入 csv 错误
                'report_url': text.get('href')                                              # 2. 替换“资料:”，文件名中有冒号无法写入
            }
            local_gov_report_url_dict.append(temp_dict)
    else:
        raw_html_text = standard_html.find_all('div', class_='content')
        html_text = raw_html_text[0].find_all('a')
        for text in html_text:
            temp_dict = {
                'report_title': (text.get_text()).replace('\xa0', '').replace('资料:', ''),
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
        report_url = item.get('url')  # report_url 是某年报告汇编合集的地址
        local_gov_report_url = filter_local_gov_report_url(report_url)
        annual_report_url_list.append(local_gov_report_url)
        print(report_url)
        time.sleep(2)                 # 为了防止 ip 被封，每抓完一年延迟两秒
    return annual_report_url_list


def write_data_to_file(url_list):
    with open(file_path, 'w', newline='') as f:
        fieldnames = ['report_title', 'report_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in url_list:
            for sub_item in item:
                report_title = sub_item.get('report_title')
                province_report_url = sub_item.get('report_url')
                """
                1. 判断 URL 地址是否合法
                2. 判断标题是否数字或者以中文括号‘（’开头，如果是，则不是报告地址
                3. 标题长度至少大于 6：“政府工作报告”
                """
                if re.match(r'^https?:/{2}\w.+$', province_report_url) and \
                    re.match(r'[^?!(\d) | ^?!(（)]', report_title) and \
                    len(report_title) > 6:
                    writer.writerow(sub_item)
    f.close()


if __name__ == '__main__':
    standard_html = get_standard_html(local_reports_collect_url)
    url_dict = filter_report_collect_url(standard_html)
    annual_report_url_list = get_annual_report_url_list(url_dict)
    write_data_to_file(annual_report_url_list)

