import numpy as np
import matplotlib.pyplot as plt
import sys
import gatherData

def dataClean(timeList1,timeList2):
    count = 0
    while count != len(timeList1):
        if timeList1[count] > 40000 or timeList1[count] < 0 or timeList2[count] > 40000 or timeList2[count] < 0:
            del timeList1[count]
            del timeList2[count]
            count -= 1
        count += 1
    return [timeList1,timeList2]

def my_sum(l):
    res = 0
    for i in l:
        if not i == None:
            res += i
    return res

def my_len(l):
    res = 0
    for i in l:
        if not i == None:
            res += 1
    return res

def makeList(source,attr,special = None):
    res = []
    for Dict in source:
        if special == None:
            if not attr == ['critical_path:']:
                if isinstance(Dict[attr],list):
                    res.append(my_sum(Dict[attr]) / my_len(Dict[attr]))
                else:
                    res.append(Dict[attr])
            else:
                res.append(Dict[attr])
        else:
            if special == 'number':
                if attr == 'orig':
                    res.append(float(len(Dict['orig_dl'])) / len(Dict['orig_dl']) + len(Dict['orig_comp']))
                else:
                    res.append(float(len(Dict['imp_dl'])) / len(Dict['imp_dl']) + len(Dict['imp_comp']))
            if special == 'time':
                if attr == 'orig':
                    res.append(my_sum(Dict['orig_dl']) / my_sum(Dict['orig_comp']) + my_sum(Dict['orig_dl']))
                else:
                    res.append(my_sum(Dict['imp_dl']) / my_sum(Dict['imp_comp']) + my_sum(Dict['imp_dl']))

    return res

def scatterAttr(list1,label1,list2,label2,fn):
    plt.plot(list1,label = label1)
    plt.plot(list2,label = label2)
    plt.title(fn)
    plt.xlabel('websites')
    plt.ylabel('value')
    plt.legend(loc = 'upper right')
    plt.savefig('./figures/' + fn)
    plt.clf()

def cdfAttr(list1,label1,list2,label2,fn):
    list1.sort()
    list2.sort()
    l = len(list1)
    y = []
    for i in range(l):
        y.append(float(i + 1) / l)
    plt.plot(list1,y,label = label1)
    plt.plot(list2,y,label = label2)
    plt.title(fn)
    plt.xlabel('time')
    plt.ylabel('cdf')
    plt.legend(loc = 'upper right')
    plt.savefig('./figures/cdf/' + fn)
    plt.clf()

avg_out = open('./avg_out.txt','w')

myAttr = ['load:','TTFB:','time_download:','time_comp:','time_block:','time_download_html:','time_download_css:','time_download_js:','time_download_img:','orig_dl','orig_comp','imp_dl','imp_comp']

myData = gatherData.my_main()
no_cache = myData[0]
cache = myData[1]
no_dns = myData[2]
dns = myData[3]

for attr in myAttr:
    l1 = makeList(no_cache,attr)
    l2 = makeList(cache,attr)
    l1 = dataClean(l1,l2)[0]
    l2 = dataClean(l1,l2)[1]
    avg_out.write(attr + '\n')
    avg_out.write('no_cache:  %f\n'%(sum(l1) / len(l1)))
    avg_out.write('cache:  ' + str(sum(l2) / len(l2)) + '\n\n')
    scatterAttr(l1,'no_cache',l2,'cache',attr[:-1] + '_with_or_without_cache.png')
    cdfAttr(l1,'no_cache',l2,'cache','cdf_' + attr[:-1] + '_with_or_without_cache.png')
l1 = makeList(no_cache,'orig','number')
l2 = makeList(cache,'imp','number')
l1 = dataClean(l1,l2)[0]
l2 = dataClean(l1,l2)[1]
scatterAttr(l1,'no_cache',l2,'cache','download_vs_total_number_with_or_without_cache.png')
cdfAttr(l1,'no_cache',l2,'cache','cdf_download_vs_total_number_with_or_without_cache.png')
l1 = makeList(no_cache,'orig','time')
l2 = makeList(cache,'imp','time')
l1 = dataClean(l1,l2)[0]
l2 = dataClean(l1,l2)[1]
scatterAttr(l1,'no_cache',l2,'cache','download_vs_toal_time_with_or_without_cache.png')
cdfAttr(l1,'no_cache',l2,'cache','cdf_download_vs_total_time_with_or_without_cache.png')

for attr in myAttr:
    l1 = makeList(no_dns,attr)
    l2 = makeList(dns,attr)
    l1 = dataClean(l1,l2)[0]
    l2 = dataClean(l1,l2)[1]
    avg_out.write(attr + '\n')
    avg_out.write('no_dns:  ' + str(sum(l1) / len(l1)) + '\n')
    avg_out.write('dns:  ' + str(sum(l2) / len(l2)) + '\n\n')
    scatterAttr(l1,'no_dns',l2,'dns',attr[:-1] + '_with_or_without_dns.png')
    cdfAttr(l1,'no_dns',l2,'dns','cdf_' + attr[:-1] + '_with_or_without_dns.png')
l1 = makeList(no_dns,'orig','number')
l2 = makeList(dns,'imp','number')
l1 = dataClean(l1,l2)[0]
l2 = dataClean(l1,l2)[1]
scatterAttr(l1,'no_dns',l2,'dns','download_vs_total_number_with_or_without_dns.png')
cdfAttr(l1,'no_dns',l2,'dns','cdf_download_vs_total_number_with_or_without_dns.png')
l1 = makeList(no_dns,'orig','time')
l2 = makeList(dns,'imp','time')
l1 = dataClean(l1,l2)[0]
l2 = dataClean(l1,l2)[1]
scatterAttr(l1,'no_dns',l2,'dns','download_vs_toal_time_with_or_without_dns.png')
cdfAttr(l1,'no_dns',l2,'dns','cdf_download_vs_total_time_with_or_without_dns.png')
avg_out.close()
