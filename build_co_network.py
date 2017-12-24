#!/usr/bin/python
#-*- coding:utf-8 -*-


"""
@author: Li Bin
@date: 2017-12-21
"""


"""
生成词同现矩阵步骤：

1. 分词，将文章中所有的词置于列表中
2. 统计词同现词组频率，统计
3. 统计同现词组频率，并按频率的降序排列
4. 获取所有同现词组列表，保证列表中的元素是唯一的
5. 生成一个空矩阵，并使得矩阵的长宽为同现词组列表长度加一
6. 构建一个关键词集合，用于作为共现矩阵的首行和首列
7. 从同现词组中获得词组共现次数并填入共现矩阵
"""


import jieba
import numpy as np
import operator
from collections import defaultdict


file_path = ''


def word_segment(file_path):
    """分词"""
    word_list = []
    f = open(file_path, encoding='utf-8')
    for line in f.readlines():
        seg_list = jieba.lcut(line, cut_all=False)
        filter_seg_list = [fil for fil in seg_list if len(fil) >= 2]
        for item in filter_seg_list:
            word_list.append(item)
    return word_list


def build_co_network(seg_list):
    """统计词同现词组频率"""
    co_net = defaultdict(lambda: defaultdict(int))
    for i in range(len(seg_list)-1):
        for j in range(i+1, i+2):
            w1 = seg_list[i]
            w2 = seg_list[j]
            if w1 != w2:
                co_net[w1][w2] += 1
    return co_net


def get_co_terms(co_net):
    """统计同现词组频率，并按频率的降序排列"""
    com_max = []
    for t1 in co_net:
        t1_max_terms = sorted(co_net[t1].items(), key=operator.itemgetter(1), reverse=True)
        for t2, t2_count in t1_max_terms:
            com_max.append(((t1, t2), t2_count))
    terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)
    return terms_max


def get_all_words(terms_max):
    """获取所有词汇列表，列表每个元素都是唯一的"""
    word_list = []
    for item in terms_max:
        for word in item[0]:
            word_list.append(word)
    return word_list


def build_matrix(word_list):
    """生成空矩阵，矩阵的高度和宽度为词汇集合的长度 +1"""
    edge = len(set(word_list)) + 1
    matrix = [['' for j in range(edge)] for i in range(edge)]
    return matrix


def get_set_key(data):
    """将词汇列表集合作为共现矩阵的首行和首列"""
    all_key = '/'.join(data)
    key_list = all_key.split('/')
    set_key_list = list(filter(lambda x: x != '', key_list))
    return list(set(set_key_list))


def init_matrix(set_key_list, matrix):
    """初始化矩阵，将关键词集合赋值给第一列和第二列"""
    matrix[0][1:] = np.array(set_key_list)
    matrix = list(map(list, zip(*matrix)))
    matrix[0][1:] = np.array(set_key_list)
    return matrix


def count_matrix(matrix, test):
    """从 term_max 中获得词组共现次数并填入共现矩阵"""
    for row in range(1, len(matrix)):
        for col in range(1, len(matrix)):
            if matrix[0][row] == matrix[col][0]:
                matrix[col][row] = str(0)
            else:
                count = 0
                for item in test:
                    if matrix[0][row] in item[0] and matrix[col][0] in item[0]:
                         count += int(item[1])
                    else:
                        continue
                matrix[col][row] = str(count)
    return matrix


if __name__ == '__main__':
    segment_word_list = word_segment(file_path)
    co_net = build_co_network(segment_word_list)
    terms_max = get_co_terms(co_net)
    word_list = get_all_words(terms_max)
    key_word_set = get_set_key(word_list)
    matrix = build_matrix(key_word_set)
    init_matrix = init_matrix(key_word_set, matrix)
    co_occurrence_matrix = count_matrix(init_matrix, terms_max)
