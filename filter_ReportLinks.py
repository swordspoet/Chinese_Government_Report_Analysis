# -*- coding: utf-8 -*-
"""
Created on Wed Dec 07 14:29:37 2016

@author: libin
"""
import urllib2
import requests
import re
import jieba
import csv
from bs4 import BeautifulSoup
import operator 
from collections import defaultdict
import jieba.analyse

def filterReportLinks(url):
    print '过滤1954-2016年政府工作报告网址······'
    html_doc = urllib2.urlopen(url).read()
    standard_html = BeautifulSoup(html_doc, "html.parser")
    for link in standard_html.find_all('a', href = re.compile(r'/content_')):
        url = link.get('href')
        year = link.get_text()
        Report_Links[year] = url
    return Report_Links