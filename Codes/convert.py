import glob

__author__ = 'jnejati'

import subprocess
import os
import shutil
import fileinput
import time


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class Convert():

    def clean_dir(self):
        dir_tobe_cleaned = ['./data/wprof_300_5_pro_1', './graphs', './temp_files/wprof_300_5_pro_1']
        for my_dir in dir_tobe_cleaned:
            if os.path.isdir(my_dir):
                for root, dirs, l_files in os.walk(my_dir):
                    for f in l_files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                os.makedirs(my_dir)

    def do_analysis(self, profile, orig_modified, imp_type,cache_or_not,run_no):

        return_value = True
        graphs_dir = ''
        if orig_modified == 'cache':
            graphs_dir = profile['device_type'] + '_' + profile['conn_type'] + '_' + profile['page_type'] + '_' + orig_modified
        elif orig_modified == 'modified':
            graphs_dir = profile['device_type'] + '_' + profile['conn_type'] + '_' + profile['page_type'] + '_' + orig_modified
        else:
            print('cache or not?')
            return False

        if not os.path.isdir(graphs_dir):
            os.makedirs(graphs_dir)
            os.makedirs(os.path.join(graphs_dir, 'graphs'))
            os.makedirs(os.path.join(graphs_dir, 'temp_files/pre_log_pro'))
	

        with cd('./tests/analysis_t'):
            self.clean_dir()
            print("Current directory:" + os.getcwd())
            if profile['device_type'] == 'desktop':
                com1 = 'perl' + ' ' + 'slice.pl' + ' ' + './pre_log'
            elif profile['device_type'] == 'mobile':
                com1 = 'perl' + ' ' + 'slicemobile-old.pl' + ' ' + './pre_log'

            #com2 = 'cp' + ' ' + './pre_log_pro/*' + ' ' + './data/wprof_300_5_pro_1/'
            com3 = 'perl' + ' ' + './analyze.pl'
            #com4 = 'cp' + ' ' + './graphs/* ' + graphs_dir + '/'
            """with cd('./pre_log'):
                for dirpath, dirnames, files in os.walk('./'):
                    if files:
                        print(dirpath, 'has files: ', files)
                        if orig_modified == 'orig':
                            print('current Directory:', os.getcwd())
                            for line in fileinput.input(files, inplace=1):
                                line = line.replace("original.testbed.localhost/", "")
                                line = line.replace("original.testbed.localhost_", "")
                                line = line.replace('original.testbed.localhost%2F', '')
                                print(line)
                        if orig_modified == 'modified':
                            for line in fileinput.input(files, inplace=1):
                                line = line.replace("modified.testbed.localhost/", "")
                                line = line.replace("modified.testbed.localhost_", "")
                                line = line.replace('modified.testbed.localhost%2F', '')
                                print(line)
                    if not files:
                        print(dirpath, 'is empty')"""
            try:
                proc = subprocess.call(com1.split(), shell=False, timeout=15)
                print("slicing")
                subprocess.call(['ls','./pre_log_pro'], shell=False, timeout=15)
            except subprocess.TimeoutExpired:
                print("Killed process " + " after timeout")
            print("slice done")
            for filename in glob.glob(os.path.join('./pre_log_pro/', '*.*')):
                shutil.copy(filename, './data/wprof_300_5_pro_1/')
            try:
                shutil.copytree('./pre_log_pro/', './data/pre_log_pro/')
            except FileExistsError:
                shutil.rmtree('./data/pre_log_pro/')
                shutil.copytree('./pre_log_pro/', './data/pre_log_pro/')

            start_time = time.time()
            try:
                proc = subprocess.call(com3.split(), shell=False, timeout=3000)
            except subprocess.TimeoutExpired:
                print("Killed process " + " after timeout")
            print("analyze done")
            print("--- %s seconds ---" % (time.time() - start_time))

        for dirpath, dirnames, files in os.walk('/yunke/page_speed/tests/analysis_t/graphs/'):
            if files:
                os.system('cp -n /yunke/page_speed/tests/analysis_t/graphs/' + files[0] + ' ' + os.path.join('/yunke/page_speed/' + graphs_dir, 'graphs/' + cache_or_not + run_no + files[0]))
                print("json files copied ")
                break
            else:
                print(dirpath, 'is empty, No Json file copied')
                return_value = False

       
        for dirpath, dirnames, files in os.walk('/yunke/page_speed/tests/analysis_t/temp_files/pre_log_pro/'):
            if files:
                os.system('cp -n /yunke/page_speed/tests/analysis_t/temp_files/pre_log_pro/* ' + os.path.join('/yunke/page_speed/' + graphs_dir, 'temp_files/' + cache_or_not + run_no + files[0]))
                print("json files copied ")
                break
            else:
                print(dirpath, 'is empty, No Json file copied')


        with cd('./tests/analysis_t'):
            shutil.rmtree('./pre_log_pro')
            shutil.rmtree('./temp_files/pre_log_pro')
            shutil.rmtree('./data/pre_log_pro')
        return return_value
