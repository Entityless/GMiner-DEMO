import os
import sys
import json
import argparse
import os
import subprocess
import io
import time
gminer_root = os.environ['GMINER_HOME']
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

input_path['skitter']['fco'] = '/chhuang/gm_input/skitter_focus_10/'
input_path['youtube']['fco'] = '/chhuang/gm_input/youtube_focus_10/'
input_path['orkut']['fco'] = '/chhuang/gm_input/orkut_focus_10/'
input_path['dblp']['fco'] = '/chhuang/gm_input/dblp_focus_10/'

machine_file = {False : os.path.join(gminer_root, 'machines.cfg'), 'ib' : 'ib_machines.cfg'}

def gminer_ini_gen(param_dic):

    ini_str = """#Copyright 2018 Husky Data Lab, CUHK
#Authors: Hongzhi Chen, Miao Liu


#ini file for example
#new line to end this ini

[PATH]
;for application I/O and local temporary storage
HDFS_HOST_ADDRESS = master
HDFS_PORT = 9000
HDFS_INPUT_PATH = {}
HDFS_OUTPUT_PATH = /chhuang/gm_output/gminer_default_output/
LOCAL_TEMP_PATH = /tmp
FORCE_WRITE = TRUE    ;force to write HDFS_OUTPUT_PATH

[COMPUTING]
;for task computing configurations
CACHE_SIZE = {}  ;the size of cachetable in each worker
NUM_COMP_THREAD = {}  ;number of threads in threadpool for task computation
PIPE_POP_NUM = {}  ;number of tasks popped out each batch in the pipeline

[STEALING]
;for task stealing configurations
POP_NUM = {}  ;number of tasks for pque pops tasks to remote worker during one stealing procedure
SUBG_SIZE_T = {}  ;threshold that task can be moved to other workers only if its current subgraph size <= SUBG_SIZE_T
LOCAL_RATE = 0.5  ;threshold that task can be moved to other workers only if its current local rate <= LOCAL_RATE

[SYNC]
;for context and aggregator sync
AGG_SLEEP_TIME = 0        ;unit:second; do context and aggregator sync periodically during computation; if AGG_SLEEP_TIME == 0, then no sync happens during computation
SYS_SLEEP_TIME = 1        ;unit:second; ; do system sync

""".format(input_path[param_dic['dataset']][param_dic['apps']], str(param_dic['cache-size']), 
           str(param_dic['num-comp-thread']), str(param_dic['pipe-pop-num']), 
           str(param_dic['pop-num']), str(param_dic['subg-size-t']))

    if(param_dic['apps'] == 'tc'):
        app_cmd = 'tc'

    if(param_dic['apps'] == 'mc'):
        app_cmd = 'mc '

    if(param_dic['apps'] == 'gm'):
        app_cmd = 'gm '

    if(param_dic['apps'] == 'cd'):
        app_cmd = 'cd {}'.format(str(param_dic['k-threshold']))

    if(param_dic['apps'] == 'fco'):
        app_cmd = 'fco {} {} {} {} {} {} '.format(str(param_dic['min-weight']), str(param_dic['min-core-size']), str(param_dic['min-result-size']),
                                                 str(param_dic['diff-ratio']), str(param_dic['iter-round-max']), str(param_dic['cand-max-time']))

    #### gen cmd

    cmd = "mpiexec -n 11 -f {} $GMINER_HOME/release/{}".format(machine_file[param_dic['ib']], app_cmd)

    return [cmd, ini_str]
