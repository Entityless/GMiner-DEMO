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
    param_dic['apps'] = 'tc'
    param_dic['cache-size'] = '2333'
    param_dic['num-comp-thread'] = '23333'
    param_dic['pipe-pop-num'] = '233333'
    param_dic['pop-num'] = '2333333'
    param_dic['subg-size-t'] = '23333333'

    return param_dic

input_path = {}
input_path['skitter'] = {}
input_path['youtube'] = {}
input_path['orkut'] = {}
input_path['friendster'] = {}
input_path['tencent'] = {}
input_path['dblp'] = {}

input_path['skitter']['tc'] = '/chhuang/gm_input/skitter_10/'
input_path['youtube']['tc'] = '/chhuang/gm_input/youtube_10/'
input_path['orkut']['tc'] = '/chhuang/gm_input/orkut_10/'
input_path['friendster']['tc'] = '/chhuang/gm_input/friendster_10/'

input_path['skitter']['mc'] = '/chhuang/gm_input/skitter_10/'
input_path['youtube']['mc'] = '/chhuang/gm_input/youtube_10/'
input_path['orkut']['mc'] = '/chhuang/gm_input/orkut_10/'
input_path['friendster']['mc'] = '/chhuang/gm_input/friendster_10/'

input_path['skitter']['gm'] = '/chhuang/gm_input/skitter_label_10/'
input_path['youtube']['gm'] = '/chhuang/gm_input/youtube_label_10/'
input_path['orkut']['gm'] = '/chhuang/gm_input/orkut_label_10/'
input_path['friendster']['gm'] = '/chhuang/gm_input/friendster_label_10/'

input_path['skitter']['cd'] = '/chhuang/gm_input/skitter_attr_10/'
input_path['youtube']['cd'] = '/chhuang/gm_input/youtube_attr_10/'
input_path['orkut']['cd'] = '/chhuang/gm_input/orkut_attr_10/'
input_path['tencent']['cd'] = '/chhuang/gm_input/tencent_attr_10/'

input_path['skitter']['fco'] = '/chhuang/gm_input/skitter_fco_10/'
input_path['youtube']['fco'] = '/chhuang/gm_input/youtube_fco_10/'
input_path['orkut']['fco'] = '/chhuang/gm_input/orkut_fco_10/'
input_path['dblp']['fco'] = '/chhuang/gm_input/dblp_fco_10/'


def gminer_ini_gen(param_dic):
    cmd = "mpiexec -n 11 -f machines.cfg $GMINER_HOME/release/"
    ini_str = ""

    #### gen ini str
    ini_str = """#Copyright 2018 Husky Data Lab, CUHK
#Authors: Hongzhi Chen, Miao Liu


#ini file for example
#new line to end this ini

[PATH]
;for application I/O and local temporary storage
HDFS_HOST_ADDRESS = master
HDFS_PORT = 9000
"""
    ini_str += "HDFS_INPUT_PATH = " + input_path[param_dic['dataset']][param_dic['apps']] + '\n'
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
    if(param_dic['apps'] == 'tc'):
        #
        cmd += 'tc '

    if(param_dic['apps'] == 'mc'):
        #
        cmd += 'mc '

    if(param_dic['apps'] == 'gm'):
        #
        cmd += 'gm '

    if(param_dic['apps'] == 'cd'):
        #
        cmd += 'cd '
        cmd += str(param_dic['k-threshold'])

    if(param_dic['apps'] == 'fco'):
        #
        cmd += 'fco '
        cmd += str(param_dic['min-weight']) + ' '
        cmd += str(param_dic['min-core-size']) + ' '
        cmd += str(param_dic['min-result-size']) + ' '
        cmd += str(param_dic['diff-ratio']) + ' '
        cmd += str(param_dic['iter-round-max']) + ' '
        cmd += str(param_dic['cand-max-time']) + ' '


    #### gen cmd

    cmd += ' | tee /dev/shm/chhuang/merge-gminer/{}.log'

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
