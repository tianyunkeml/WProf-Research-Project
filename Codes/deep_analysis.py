import json
import os
import numpy as np
import matplotlib.pyplot as plt
import sys

RUN_TIME = 18
websites = ['www.wmpic.me','www.mi.com','www.114.com.cn']
obj_type = ['image','text','application','non-eval']
dir1 = '/yunke/page_speed/desktop_wifi-fast_top50_cache/temp_files/wprof_300_5_pro_1/'
dir2 = '/yunke/page_speed/desktop_wifi-fast_top50_cache/graphs/'

def my_merge(a,b):
    for i in b:
        if not i in a:
            a.append(i)
    return a

def get_cp_acts(fn):
    f = open(dir1 + fn,'r')
    for line in f:
        if 'critical_path' in line:
            temp = line[len('critical_path:'):]
    temp = temp.replace('[','')
    temp = temp.replace(']','')
    temp = temp.replace(' ','')
    temp = temp.replace('\t','')
    res = temp.split(',')
    for i in range(len(res)):
        res[i] = res[i][1:-1]
        res[i] = res[i].replace('\'','')
    f.close()
    return res

def Add_Dict(A,B):
    for k,v in B.items():
        if k in A:
            A[k] += v
        else:
            A[k] = v
    return A

def ratio_avg(D,c):
    for k,v in D.items():
        D[k] = float(v) / c
    return D

def get_ratio(time_Dict,type_Dict,fn,site,cond):
    total_t = 0
    acts = get_cp_acts(fn)
    R_Dict = {}
    for act in acts:
        tp = type_Dict[(site,cond,act)]
        if tp == 'eval':
            continue
        if tp in R_Dict:
            R_Dict[tp] += time_Dict[(site,cond,act)]
        else:
            R_Dict[tp] = time_Dict[(site,cond,act)]
        total_t += time_Dict[(site,cond,act)]
    for k,v in R_Dict.items():
        R_Dict[k] = v / total_t
    return [R_Dict,total_t]

def get_type(wd):
    if isinstance(wd,int):
        res = 'non-eval'
    elif wd == None:
        res = 'non-eval'
    elif not wd.find('/') == -1:
        res = wd[:wd.find('/')]
    elif 'eval' in wd:
        res = 'eval'
    else:
        res = 'non-eval'
    return res
    
def scatterAttr(list1,label1,list2,label2,list3,label3,fn):
    plt.plot(list1,label = label1)
    plt.plot(list2,label = label2)
    plt.plot(list3,label = label3)
    plt.title(fn)
    plt.xlabel('activities')
    plt.ylabel('time')
    plt.legend(loc = 'upper right')
    plt.savefig('./new_figures/' + fn)
    plt.clf()

def makepie(list1,label1,label2,label3,label4,fn):
    labels = [label1,label2,label3,label4]
    sizes = list1
    colors = ['red','yellow','blue','green']
    patches,texts = plt.pie(sizes,colors = colors,)
    plt.legend(patches,labels,loc = 'best')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('./new_figures/pies/' + fn)
    plt.clf()

def shorten(site):
    if '114' in site:
        return '114'
    if 'mi' in site:
        return 'mi'
    if 'wmpic' in site:
        return 'wmpic'

def info_search(Dict,attr):
    if isinstance(Dict,dict):
        for k,v in Dict.items():
            if isinstance(v,str):
                if v == attr.replace(' ','').replace('\n',''):
                    if k == 'id':
                        if 'download' in attr:
                            return [float(Dict['receivedTime']) - float(Dict['s_time']),get_type(Dict['type'])]
                        else:
                            return [float(Dict['e_time']) - float(Dict['s_time']),get_type(Dict['type'])]
            if isinstance(v,dict) or isinstance(v,list):
                temp = info_search(v,attr)
                if not temp == None:
                    return temp
    if isinstance(Dict,list):
        for i in Dict:
            if isinstance(i,dict) or isinstance(i,list):
                temp = info_search(i,attr)
                if not temp == None:
                    return temp


Dict = {'www.wmpic.me':[],'www.mi.com':[],'www.114.com.cn':[]}
rt = os.walk(dir1)
for fn_list in rt:
    1 == 1
fn_list = fn_list.__getitem__(2)
for fn in fn_list:
    for w in websites:
        if w in fn:
            Dict[w] = my_merge(Dict[w],get_cp_acts(fn))

type_Dict = {}
time_Dict = {}
for site in websites:
    for fn in fn_list:
        if '.json' in fn:
            jfn = fn
        else:
            jfn = fn + '_.json'
        jf = open(dir2 + jfn,'r')
        jDict = json.load(jf)
        if site in fn:
            for act in Dict[site]:
                if 'cache' in fn and 'no_cache' not in fn:
                    temp = info_search(jDict,act)
                    if temp == None or temp[0] > 50000 or temp[0] < 0:
                        print('Value error: ' + fn + '   ' + act)
                        continue
                    if (site,'cache',act) in time_Dict:
                        time_Dict[(site,'cache',act)].append(temp[0])
                        type_Dict[(site,'cache',act)] = temp[1]
                    else:
                        time_Dict[(site,'cache',act)] = [temp[0]]
                        type_Dict[(site,'cache',act)] = temp[1]
                if 'dns' in fn:
                    temp = info_search(jDict,act)
                    if temp == None or temp[0] > 50000 or temp[0] < 0:
                        print('Value error: ' + fn + '   ' + act)
                        continue
                    if (site,'dns',act) in time_Dict:
                        time_Dict[(site,'dns',act)].append(temp[0])
                        type_Dict[(site,'dns',act)] = temp[1]
                    else:
                        time_Dict[(site,'dns',act)] = [temp[0]]
                        type_Dict[(site,'dns',act)] = temp[1]
                if 'no_cache' in fn:
                    temp = info_search(jDict,act)
                    if temp == None or temp[0] > 50000 or temp[0] < 0:
                        print('Value error: ' + fn + '   ' + act)
                        continue
                    if (site,'no_cache',act) in time_Dict:
                        time_Dict[(site,'no_cache',act)].append(temp[0])
                        type_Dict[(site,'no_cache',act)] = temp[1]
                    else:
                        time_Dict[(site,'no_cache',act)] = [temp[0]]
                        type_Dict[(site,'no_cache',act)] = temp[1]
        jf.close()

R_Dict_cache = {'www.wmpic.me':{},'www.mi.com':{},'www.114.com.cn':{}}
R_Dict_dns = {'www.wmpic.me':{},'www.mi.com':{},'www.114.com.cn':{}}
R_Dict_no_cache = {'www.wmpic.me':{},'www.mi.com':{},'www.114.com.cn':{}}
count_cache = 0
count_dns = 0
count_no_cache = 0

for k,v in time_Dict.items():
    time_Dict[k] = float(sum(v)) / len(v)
for site in websites:
    for fn in fn_list:
        if site in fn:
            for run_no in range(RUN_TIME):
                if '_' + str(run_no) in fn:
                    if 'cache' in fn and 'no_cache' not in fn:
                        R_Dict_cache[site] = Add_Dict(R_Dict_cache[site],get_ratio(time_Dict,type_Dict,fn,site,'cache')[0])
                        count_cache += 1
                    if 'dns' in fn:
                        R_Dict_dns[site] = Add_Dict(R_Dict_dns[site],get_ratio(time_Dict,type_Dict,fn,site,'dns')[0])
                        count_dns += 1
                    if 'no_cache' in fn:
                        R_Dict_no_cache[site] = Add_Dict(R_Dict_no_cache[site],get_ratio(time_Dict,type_Dict,fn,site,'no_cache')[0])
                        count_no_cache += 1

for site in websites:
    R_Dict_cache[site] = ratio_avg(R_Dict_cache[site],8)
    R_Dict_dns[site] = ratio_avg(R_Dict_dns[site],8)
    R_Dict_no_cache[site] = ratio_avg(R_Dict_no_cache[site],8)
'''print('time_Dict:')
print(time_Dict)
print('type_Dict:')
print(type_Dict)
print('R_Dict_cache:')
print(R_Dict_cache)
print('R_Dict_dns:')
print(R_Dict_dns)
print('R_Dict_no_cache:')
print(R_Dict_no_cache)'''

time_of_type = {}
for site in websites:
    for cond in ['cache','dns','no_cache']:
        for k,v in type_Dict.items():
            if cond in k and site in k:
                if not v == 'eval':
                    if (site,cond,v) in time_of_type:
                        time_of_type[(site,cond,v)].append(time_Dict[k])
                    else:
                        time_of_type[(site,cond,v)] = [time_Dict[k]]

for site in websites:
    for tp in obj_type:
        cache_list = time_of_type[(site,'cache',tp)]
        label1 = shorten(site) + '_cache_' + tp + ' (avg = ' + str(sum(cache_list) / len(cache_list))[:-11] + ')'
        dns_list = time_of_type[(site,'dns',tp)]
        label2 = shorten(site) + '_dns_' + tp + ' (avg = ' + str(sum(dns_list) / len(dns_list))[:-11] + ')'
        no_cache_list = time_of_type[(site,'no_cache',tp)]
        label3 = shorten(site) + '_no_cache_' + tp + ' (avg = ' + str(sum(no_cache_list) / len(no_cache_list))[:-11] + ')'
        fn = site + '_' + tp + '.png'
        scatterAttr(cache_list,label1,dns_list,label2,no_cache_list,label3,fn)

for site in websites:
    pielist = []
    for tp in obj_type:
        if tp in R_Dict_cache[site]:
            pielist.append(R_Dict_cache[site][tp])
    fn = 'pie_' + site + '_cache.png'
    makepie(pielist,'image','text','application','non-eval_computation',fn)
    pielist = []
    for tp in obj_type:
        if tp in R_Dict_dns[site]:
            pielist.append(R_Dict_dns[site][tp])
    fn = 'pie_' + site + '_dns.png'
    makepie(pielist,'image','text','application','non-eval_computation',fn)
    pielist = []
    for tp in obj_type:
        if tp in R_Dict_no_cache[site]:
            pielist.append(R_Dict_no_cache[site][tp])
    fn = 'pie_' + site + '_no_cache.png'
    makepie(pielist,'image','text','application','non-eval_computation',fn)





