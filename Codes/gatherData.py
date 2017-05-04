import json
import os

dir1 = '/yunke/page_speed/desktop_wifi-fast_top50_cache/temp_files/wprof_300_5_pro_1/'
dir2 = '/yunke/page_speed/desktop_wifi-fast_top50_cache/graphs/'

def path_com(fn):
    f = open(fn,'r')
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

def time_search(Dict,attr):
    if isinstance(Dict,dict):
        for k,v in Dict.items():
            if isinstance(v,str):
                if v == attr.replace(' ','').replace('\n',''):
                    if k == 'id':
                        if 'download' in attr:
                            return (float(Dict['receivedTime']) - float(Dict['s_time']))
                        else:
                            return (float(Dict['e_time']) - float(Dict['s_time']))
            if isinstance(v,dict) or isinstance(v,list):
                temp = time_search(v,attr)
                if not temp == None:
                    return temp
    if isinstance(Dict,list):
        for i in Dict:
            if isinstance(i,dict) or isinstance(i,list):
                temp = time_search(i,attr)
                if not temp == None:
                    return temp

def info_mine(fn,obj_dict):
    item_list = ['load:','TTFB:','time_download:','time_comp:','time_block:','time_download_html:','time_download_css:','time_download_js:','time_download_img:','time_download_o:','time_block_css:','time_block_js:','critical_path:']
    f = open(dir1 + fn,'r')
    res = {}
    for line in f:
        for wd in item_list:
            if wd in line:
                if wd == 'load:':
                    if 'download:' not in line:
                        res[wd] = float((line[len(wd):-1]).replace('\t',''))
                elif wd == 'critical_path:':
                    res[wd] = (line[len(wd):-1]).replace('\t','')
                else:
                    res[wd] = float((line[len(wd):-1]).replace('\t',''))
    f.close()
    if '.json' in fn:
        jfn = fn
    else:
        jfn = fn + '_.json'
    jf = open(dir2 + jfn,'r')
    jDict = json.load(jf)
    for categ,attr_set in obj_dict.items():
        res[categ] = []
        for attr in attr_set:
            res[categ].append(time_search(jDict,attr))
    
    return res

def my_main():
    no_cache = []
    cache = []
    no_dns = []
    dns = []
    rt = os.walk(dir1)
    for allfiles in rt:
        1 == 1
    allfiles = allfiles.__getitem__(2)
    for my_file in allfiles:
        if 'no_cache' in my_file or 'no_dns' in my_file:
            if my_file[3:] in allfiles:
                obj_set = {}
                obj_set['orig_dl'] = []
                obj_set['orig_comp'] = []
                obj_set['imp_dl'] = []
                obj_set['imp_comp'] = []
                cp1 = path_com(dir1 + my_file)
                cp2 = path_com(dir1 + my_file[3:])
                for obj in cp1:
                    if 'download' in obj:
                        obj_set['orig_dl'].append(obj)
                    else:
                        obj_set['orig_comp'].append(obj)
                for obj in cp2:
                    if 'download' in obj:
                        obj_set['imp_dl'].append(obj)
                    else:
                        obj_set['imp_comp'].append(obj)
        
                if 'no_cache' in my_file:
                    no_cache.append(info_mine(my_file,obj_set))
                    cache.append(info_mine(my_file[3:],obj_set))
                if 'no_dns' in my_file:
                    no_dns.append(info_mine(my_file,obj_set))
                    dns.append(info_mine(my_file[3:],obj_set))
    return [no_cache,cache,no_dns,dns]


if __name__ == '__main__':
    my_main()
