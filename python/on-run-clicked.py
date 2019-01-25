import os
import sys
import json
import argparse
import os
import subprocess
import io
import time

space_strs = []
for i in range(1000):
    space_strs.append("")
    for j in range(i):
        space_strs[i] = space_strs[i] + " "

#run and confirm?

def get_frontend_dic():

    param_dic = {}
    param_dic['dataset'] = 'skitter'
    param_dic['app_name'] = 'TC'
    param_dic['cache-size'] = '2333'
    param_dic['num-comp-thread'] = '23333'
    param_dic['pipe-pop-num'] = '233333'
    param_dic['pop-num'] = '2333333'
    param_dic['subg-size-t'] = '23333333'
    param_dic['app_param'] = {}

    return param_dic

input_path = {}
input_path['skitter'] = {}
input_path['youtube'] = {}
input_path['orkut'] = {}

input_path['skitter']['TC'] = '/chhuang/gm_input/skitter_10/'
input_path['youtube']['TC'] = '/chhuang/gm_input/youtube_10/'
input_path['orkut']['TC'] = '/chhuang/gm_input/orkut_10/'

input_path['skitter']['MC'] = '/chhuang/gm_input/skitter_10/'
input_path['youtube']['MC'] = '/chhuang/gm_input/youtube_10/'
input_path['orkut']['MC'] = '/chhuang/gm_input/orkut_10/'

input_path['skitter']['GM'] = '/chhuang/gm_input/skitter_label_10/'
input_path['youtube']['GM'] = '/chhuang/gm_input/youtube_label_10/'
input_path['orkut']['GM'] = '/chhuang/gm_input/orkut_label_10/'

input_path['skitter']['CD'] = '/chhuang/gm_input/skitter_attr_10/'
input_path['youtube']['CD'] = '/chhuang/gm_input/youtube_attr_10/'
input_path['orkut']['CD'] = '/chhuang/gm_input/orkut_attr_10/'

input_path['skitter']['GC'] = '/chhuang/gm_input/skitter_multi_attr_10/'
input_path['youtube']['GC'] = '/chhuang/gm_input/youtube_multi_attr_10/'
input_path['orkut']['GC'] = '/chhuang/gm_input/orkut_multi_attr_10/'


def gminer_ini_gen(param_dic):
    #param_dic['dataset'] : {skitter, youtube, orkut}
    #param_dic['app_name'] : {TC, GM, MC, CD, GC}
    #param_dic['cache-size'] : 
    #param_dic['num-comp-thread'] : 
    #param_dic['pipe-pop-num'] : 
    #param_dic['pop-num'] : 
    #param_dic['subg-size-t'] : 
    #param_dic['app_param']: a dic, if CD or GC

    cmd = "mpiexec -n 11 -f machines.cfg $GMINER_HOME/release/"
    ini_str = ""

    #### gen ini str
    ini_str = """#Copyright 2018 Husky Data Lab, CUHK
#Authors: Hongzhi Chen, Neko Liu


#ini file for example
#new line to end this ini

[PATH]
;for application I/O and local temporary storage
HDFS_HOST_ADDRESS = master
HDFS_PORT = 9000
"""
    ini_str += "HDFS_INPUT_PATH = " + input_path[param_dic['dataset']][param_dic['app_name']] + '\n'
    ini_str += """HDFS_OUTPUT_PATH = /chhuang/gm_output/gminer_default_output/
LOCAL_TEMP_PATH = /tmp
FORCE_WRITE = TRUE    ;force to write HDFS_OUTPUT_PATH
DEMO_LOG_PATH = /home/cghuan/gminer_demo_log/

[COMPUTING]
;for task computing configurations
"""
    ini_str += "CACHE_SIZE = " + str(param_dic['cache-size']) + "  ;the size of cachetable in each worker\n"
    ini_str += "NUM_COMP_THREAD = " + str(param_dic['num-comp-thread']) + "   ;number of threads in threadpool for task computation\n"
    ini_str += "PIPE_POP_NUM = " + str(param_dic['pipe-pop-num']) + "    ;number of tasks popped out each batch in the pipeline\n"
    ini_str += """
[STEALING]
;for task stealing configurations
"""
    ini_str += "POP_NUM = " + str(param_dic['pop-num']) + "         ;number of tasks for pque pops tasks to remote worker during one stealing procedure\n"
    ini_str += "SUBG_SIZE_T = " + str(param_dic['subg-size-t']) + "      ;threshold that task can be moved to other workers only if its current subgraph size <= SUBG_SIZE_T\n"
    ini_str += """LOCAL_RATE = 0.5      ;threshold that task can be moved to other workers only if its current local rate <= LOCAL_RATE

[SYNC]
;for context and aggregator sync
AGG_SLEEP_TIME = 0        ;unit:second; do context and aggregator sync periodically during computation; if AGG_SLEEP_TIME == 0, then no sync happens during computation
SYS_SLEEP_TIME = 1        ;unit:second; ; do system sync

"""
    if(param_dic['app_name'] == 'TC'):
        #
        cmd += 'tc '

    if(param_dic['app_name'] == 'MC'):
        #
        cmd += 'mc '

    if(param_dic['app_name'] == 'GM'):
        #
        cmd += 'gm '

    if(param_dic['app_name'] == 'CD'):
        #
        cmd += 'cd '
        cmd += str(param_dic['app_param']['k-threshold'])

    if(param_dic['app_name'] == 'GC'):
        #
        cmd += 'fco '
        cmd += str(param_dic['app_param']['min-weight']) + ' '
        cmd += str(param_dic['app_param']['min-core-size']) + ' '
        cmd += str(param_dic['app_param']['min-result-size']) + ' '
        cmd += str(param_dic['app_param']['diff-ratio']) + ' '
        cmd += str(param_dic['app_param']['iter-round-max']) + ' '
        cmd += str(param_dic['app_param']['cand-max-time']) + ' '


    #### gen cmd

    cmd += ' | tee /dev/shm/chhuang/merge-gminer/stdout.log'

    return [cmd, ini_str]

if __name__ == "__main__":

    param_dic = get_frontend_dic()
    #rsync
    #cp master
    [run_cmd, ini_str] = gminer_ini_gen(param_dic)

    print(run_cmd)

    with open('faker.ini', 'w') as f:
        f.write(ini_str)
        f.close()
