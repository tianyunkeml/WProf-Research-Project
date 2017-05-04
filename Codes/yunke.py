__author__ = 'jnejati'

#import experiments
import convert
import post_analyze
import apache_conf
import network_emulator
from urllib.parse import urlparse
import  chromium_driver
import time
import modifications as modify
from bs4 import BeautifulSoup
import urllib.request
import urllib.response
import io
import gzip
import subprocess
import os
import shutil
import json_dag

class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def main():
    input_file = 'top50.txt'
    #exp_type = 'compression'
    #exp_type = 'minification'
    exp_type = ''
    my_profiles = [
                   # Wi-Fi ac
                   {'conn_type':'wifi-fast',
                  'device_type': 'desktop',
                  'page_type': 'top50',
                  'cache': 'no_cache',
                  'download_rate':'100Mbit',
                  'download_delay':'1ms',
                  'download_loss':'0.1%',
                  'upload_rate':'90Mbit',
                  'upload_delay':'1ms',
                  'upload_loss':'0.1%'}
                                        ]
    net_profile = my_profiles[0]
    graph_dir = net_profile['device_type'] + '_' + net_profile['conn_type'] + '_' + net_profile['page_type'] + '_' + 'cache'
    cmd = 'rm -r ' + graph_dir
    subprocess.call(cmd.split(),shell = False)

    #apache_conf.rm_dir(arch_dir)
    #apache_conf.fetch_all_sites(input_file, arch_dir)
    for run_no in range(1):
        top_sites = (l.strip().split() for l in open("./res/" + input_file).read().splitlines())
        un_pop_sites = (l.strip().split() for l in open("./res/" + 'un_pop.txt').read().splitlines())
        prelog_dir = '/yunke/page_speed/tests/analysis_t/pre_log_repo'
        cmd1 = 'service dnsmasq restart'
        cmd2 = 'service dnsmasq stop'
        if os.path.isdir(prelog_dir):
            subprocess.call(['rm','-r',prelog_dir],shell=False)
        os.makedirs(prelog_dir)
        for site in top_sites:
            s1 = urlparse(site[0])
            my_run = chromium_driver.RunChromium(site[0],'no_cache',net_profile,'','not_record')
            my_run_no_cache = chromium_driver.RunChromium(site[0],'no_cache',net_profile,'','record')
            my_run_cache = chromium_driver.RunChromium(site[0],'cache',net_profile,'','record')
            my_run.main_run()
            my_run_no_cache.main_run()
            my_run_cache.main_run()
        for site in un_pop_sites:
            s1 = urlparse(site[0])
            my_run_no_dns = chromium_driver.RunChromium(site[0],'no_cache',net_profile,'no_dns','record')
            my_run_dns = chromium_driver.RunChromium(site[0],'no_cache',net_profile,'dns','record')
            subprocess.call(cmd1.split(),shell = False)
            my_run_no_dns.main_run()
            my_run_dns.main_run()
            subprocess.call(cmd2.split(),shell = False)
        prelog_dir = '/yunke/page_speed/tests/analysis_t/pre_log'
        if os.path.isdir(prelog_dir):
            for root, dirs, l_files in os.walk(prelog_dir):
                for f in l_files:
                    os.unlink(os.path.join(root,f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root,d))
        else:
            os.makedirs(prelog_dir)

        rt = os.walk('/yunke/page_speed/tests/analysis_t/pre_log_repo')
        for pre_files in rt:
            1 == 1
        pre_files = pre_files.__getitem__(2)
        for pre_file in pre_files:
            cmd = 'cp -b /yunke/page_speed/tests/analysis_t/pre_log_repo/' + pre_file + ' /yunke/page_speed/tests/analysis_t/pre_log/'
            subprocess.call(cmd.split(),shell=False)
            for net_profile in my_profiles:
                #netns = network_emulator.NetworkEmulator(net_profile)
                #netns.set_profile(net_profile['conn_type'])
                if 'no_cache' in pre_file:
                    cache_or_not = 'no_cache_'
                else:
                    cache_or_not = 'cache_'
                if 'dns' in pre_file:
                    cache_or_not = 'dns_'
                if 'no_dns' in pre_file:
                    cache_or_not = 'no_dns_'
                conv_orig = convert.Convert()
                if conv_orig.do_analysis(net_profile,'cache','',cache_or_not):
                    print("Origin json file analyzed")
                else:
                    print("No origin json file for this site")
                    break
                """if conv_orig.do_analysis(net_profile, 'orig', exp_type):
                    print("Origin json file analyzed")
                    my_exp = experiments.SetExperiment(exp_type)
                    my_exp.run(site[0], net_profile)
                    conv_mod = convert.Convert()
                    conv_mod.do_analysis(net_profile, 'modified', exp_type)
                    apachectl_modified.archive_site(s1.netloc)

                else:
                    print("No origin json file for this site")
                    break"""
                print("Origin json file analyzed")
                '''my_exp = experiments.SetExperiment(exp_type)
                my_exp.run(site[0], net_profile)
                conv_mod = convert.Convert()
                conv_mod.do_analysis(net_profile, 'modified', exp_type)
                apachectl_modified.archive_site(s1.netloc)
                time.sleep(60)'''
            cmd = 'rm /yunke/page_speed/tests/analysis_t/pre_log/' + pre_file
            subprocess.call(cmd.split(),shell=False)
    with cd(graph_dir):
        print('current directory: ', graph_dir)
        json_dag.json_to_dag()
        time.sleep(3)

if __name__ == '__main__':
    main()
