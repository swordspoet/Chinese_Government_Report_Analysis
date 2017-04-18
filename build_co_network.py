#针对每年报告文本结巴分词之后得到的seg_list进行“同现词”统计
def build_co_network(seg_list):   
    co_net = defaultdict(lambda: defaultdict(int))
    for i in range(len(seg_list)-1):            
        for j in range(i+1, i+2):
            w1 = seg_list[i]
            w2 = seg_list[j]
            if w1 != w2:
                co_net[w1][w2] += 1
    return co_net
#“同现词”统计之后，我们将统计的结果（Top 100）返回到“terms_max”中
def get_co_terms(co_net): 
    com_max = []
    for t1 in co_net:
        t1_max_terms = sorted(co_net[t1].items(), key=operator.itemgetter(1), reverse=True)
        for t2, t2_count in t1_max_terms:
            com_max.append(((t1, t2), t2_count))
    terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)
    return terms_max

#针对terms_max，将s2,s3,s4写入CSV文件中        
def get_co_network():
    for (year, link) in Report_Links.items():
        #year = str(year)
        text = extract_text(link)
        seg_list = jiebait(text)
        co_net = build_co_network(seg_list)
        terms_max = get_co_terms(co_net)
        for s1 in terms_max:
            s2 = s1[0][0]
            s3 = s1[0][1]
            s4 = s1[1]
            s2 = s2.encode('utf-8') #s2和s3以Unicode编码存在，故转码为‘utf8’
            s3 = s3.encode('utf-8')
            s4 = str(s4)
            print year,  s4
            terms = open('terms5.csv', 'ab')
            terms.write(year + '\t')
            terms.write(s2 + '\t')
            terms.write(s3 + '\t')
            terms.write(s4 + '\n')
            terms.close()

get_co_network()