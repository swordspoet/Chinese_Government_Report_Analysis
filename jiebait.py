#结巴分词
def jiebait(text):
    seglist = jieba.lcut(text, cut_all = False)
    filter_seglist = [fil for fil in seglist if len(fil) >= 2]
    return filter_seglist 
Report_Links = filterReportLinks(url)