import os
import sys
import json
import argparse
import os
import subprocess
import io
import time
import numpy as np

parser = argparse.ArgumentParser()

#recognized by pssh
parser.add_argument('-l', '-logpath', '--logpath', help='Local path of unmerged outputs', default = '/home/cghuan/gminer_demo_log/')
parser.add_argument('-d', '-localdir', '--localdir', help='Local path of merging outputs', default = '/dev/shm/chhuang/merge-gminer/')
parser.add_argument('-b', '-bkpdir', '--bkpdir', help='Merged output backup', default = '/home/cghuan/bkp_gm/')
parser.add_argument('-i', '-interval', '--interval', help='Interval', default='0.5')
parser.add_argument('-s', '-slave_interval', '--slave_interval', help='How many times is the interval of slaves than the master', default='4')
parser.add_argument('-t', '-timestamp', '--timestamp', help = 'the timestamp when GMiner application was launched', required = True)

args = vars(parser.parse_args())

args['localdir'] += '/' + args['timestamp'] + '/'
args['bkpdir'] += '/' + args['timestamp'] + '/'
args['logpath'] += '/' + args['timestamp'] + '/'

signal_file_name = args['logpath'] + 'signal-file-gminer.' + args['timestamp']

space_strs = []
for i in range(1000):
    space_strs.append("")
    for j in range(i):
        space_strs[i] = space_strs[i] + " "

def run_bg_cmd(command):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    proc.wait() #this works
    lns_content = []
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        if(line[-1] == '\n'):
            lns_content.append(line[:-1])
        else:
            lns_content.append(line)
    return lns_content

node_max_q = 2
global_post_processing_history = {}
global_master_dic_list = []
global_post_processing_len = 0

def OnAppStart():
    #write some file that needed by the frontend
    os.system("mkdir -p " + args['localdir'])

    master_5q_path = args['localdir'] + "/master_5q.json"
    dic_to_write = {}
    dic_to_write['task_num_in_memory'] = 0
    dic_to_write['task_num_in_disk'] = 0
    dic_to_write['cmq_size'] = 0
    dic_to_write['cpq_size'] = 0
    dic_to_write['taskbuf_size'] = 0

    dic_to_write['task_num_in_memory_float'] = 0.0
    dic_to_write['task_num_in_disk_float'] = 0.0
    dic_to_write['cmq_size_float'] = 0.0
    dic_to_write['cpq_size_float'] = 0.0
    dic_to_write['taskbuf_size_float'] = 0.0
    
    with open(master_5q_path, 'w') as f:
        f.write(json.dumps(dic_to_write) + '\n')
        f.close()

#begin
def OnSignalAppear():
    global global_post_processing_history
    global global_master_dic_list
    global global_post_processing_len
    global_post_processing_history = {}
    global_master_dic_list = []
    global_post_processing_len = 0

    f = open(signal_file_name, 'r')
    ln = f.readline()
    f.close()
    local_signal_dic = json.loads(ln)
    print("OnSignalAppear ", local_signal_dic)

    for hostname in local_signal_dic['slaves']:
        os.system("mkdir -p " + args['localdir'] + "/" + hostname)
        global_post_processing_history[hostname] = []

    os.system("mkdir -p " + args['localdir'] + "/" + local_signal_dic['master'])
    os.system("mkdir -p " + local_signal_dic['master'])

    return local_signal_dic

procs = []

#running
def RunningMaster(signal_dic):
    # print("RunningMaster")
    command = "rsync -avzP --delete " + signal_dic['master'] + ":" + signal_dic['DEMO_LOG_PATH'] + " " + args['localdir'] + "/" + signal_dic['master']
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    # procs.append(proc)
    proc.wait()
    return 0

def RunningSlave(signal_dic):
    # print("RunningSlave")
    for hostname in signal_dic['slaves']:
        ib_name = 'ib' + hostname[6:]
        command = "rsync -avzP --delete " + ib_name + ":" + signal_dic['DEMO_LOG_PATH'] + " " + args['localdir'] + "/" + hostname
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        procs.append(proc)
    return 0

def UglyTanh(x, f):
    return 1.0 -  1.0 / (np.log(x / f + 1) * np.log(x / f + 1) + 1)

def EvilMapping(x):
    #x: any numerical value
    if(x <= 0.0):
        return 0.0
    if(not x >= 0.0):
        return 0.0
    return 0.2 * UglyTanh(x, 1) + 0.175 * UglyTanh(x, 10) + 0.175 * UglyTanh(x, 100) + 0.175 * UglyTanh(x, 1000) + 0.175 * UglyTanh(x, 10000) + 0.1 * UglyTanh(x, 100000)

def PostProcessing(signal_dic):
    #ramdom pick

    #### master.json
    # master_agg_path = args['localdir'] + "/master_agg.json"
    master_5q_path = args['localdir'] + "/master_5q.json"
    master_append_path = args['localdir'] + "/master_append.json"
    # cmd = 'cp ' + args['localdir'] + '/' + signal_dic['master'] + '/master_5q.log ' + master_agg_path
    # # print(cmd)
    # os.system(cmd)

    global global_master_dic_list

    master_5q_log_last_line = ""

    if(os.path.isfile(args['localdir'] + '/' + signal_dic['master'] + '/master_5q.log')):
        # print("os.path.isfile(args['localdir'] + '/' + signal_dic['master'] + '/master_5q.log')")
        with open(args['localdir'] + '/' + signal_dic['master'] + '/master_5q.log') as f:
            #
            lns = f.readlines()
            f.close()

            # print(lns)

            tmp_len = len(global_master_dic_list)
            for i in range(tmp_len, len(lns)):
                ln = lns[i]
                master_5q_log_last_line = ln
                if(len(ln) < 2):
                    break
                if(not (ln[-1] == '\n' or ln[-1] == '}')):
                    continue
                # print(ln)
                # no rsync bug because the master rsync process is finished, see function RunningMaster
                # if(not ln[-1] == '\n'):
                #     print('break')
                #     break
                global_master_dic_list.append(json.loads(ln))
                # print('global_master_dic_list.append ', global_master_dic_list[-1])
    #dump master_5q.json

    #或许需要处理文件短暂为空的逻辑
    with open(master_5q_path, 'w') as f:
        dic_to_write = {}
        dic_to_write['task_num_in_memory'] = 0
        dic_to_write['task_num_in_disk'] = 0
        dic_to_write['cmq_size'] = 0
        dic_to_write['cpq_size'] = 0
        dic_to_write['taskbuf_size'] = 0

        if(len(global_master_dic_list) > 0):
            #[task_num_in_memory, task_num_in_disk, cmq_size, cpq_size, taskbuf_size]
            for i in range(global_master_dic_list[-1]['nodes']):
                stri = str(i)          
                dic_to_write['task_num_in_memory'] += global_master_dic_list[-1][stri][0]
                dic_to_write['task_num_in_disk'] += global_master_dic_list[-1][stri][1]
                dic_to_write['cmq_size'] += global_master_dic_list[-1][stri][2]
                dic_to_write['cpq_size'] += global_master_dic_list[-1][stri][3]
                dic_to_write['taskbuf_size'] += global_master_dic_list[-1][stri][4]

        dic_to_write['task_num_in_memory_float'] = EvilMapping(dic_to_write['task_num_in_memory'])
        dic_to_write['task_num_in_disk_float'] = EvilMapping(dic_to_write['task_num_in_disk'])
        dic_to_write['cmq_size_float'] = EvilMapping(dic_to_write['cmq_size'])
        dic_to_write['cpq_size_float'] = EvilMapping(dic_to_write['cpq_size'])
        dic_to_write['taskbuf_size_float'] = EvilMapping(dic_to_write['taskbuf_size'])

        dic_to_write['task_transfer_1'] = dic_to_write['task_num_in_disk']
        dic_to_write['task_transfer_2'] = dic_to_write['cmq_size']
        dic_to_write['task_transfer_3'] = dic_to_write['cpq_size']
        dic_to_write['task_transfer_4'] = dic_to_write['cpq_size']

        # print(json.dumps(dic_to_write))
        f.write(json.dumps(dic_to_write) + '\n')
        f.close()

        #debug
        with open(master_append_path, 'a') as f2:
            f2.write(json.dumps(dic_to_write) + '\n')
            f2.close()

    global global_post_processing_history
    global global_post_processing_len

    ##### slaves.json
    ## this cound be somehow complex; random pick
    ## multiple file need to be processed
    if(signal_dic['app_name'] == 'GM' or signal_dic['app_name'] == 'TC'):
        

        slaves_path = args['localdir'] + "/slaves.json"
        post_processing_history = global_post_processing_history

        #post_processing_history[worker_name][tid]可以得到某个节点的某个线程最新挖出来的行。数量可以指定，默认为1

        node_id = 0
        for hostname in signal_dic['slaves']:
            local_path = args['localdir'] + '/' + hostname + '/'
            lns = run_bg_cmd("ls -l " + local_path + "| grep 'finish'") #somehow wasting

            # print(hostname + ', len(lns) = ', len(lns))

            fs = os.listdir(args['localdir'] + "/" + hostname)
            # print(lns) len(lns)就是现在的某个节点有多少个输出part

            #e.g., demo_node_5_thread_0_part_0.log

            node_counter = 0

            #check if to scan for the history
            if(len(lns) != global_post_processing_len):
                for tid in range(signal_dic['nthreads']):
                    newest_possible_fn = 'demo_node_' + str(node_id) + '_thread_' + str(tid) + '_part_' + str(global_post_processing_len) + '.log'

                    cmd = 'tail -n ' + str(node_max_q) + " " + local_path + newest_possible_fn

                    if(os.path.isfile(local_path + newest_possible_fn)):
                        
                        # print(cmd)
                        tail_ret = run_bg_cmd(cmd)

                        for ln in tail_ret:
                            # print('pln = json.loads ', ln)
                            if(ln[-1] == '}'):
                                pln = json.loads(ln)
                                post_processing_history[hostname].insert(0, pln['Q'])
                                node_counter += 1

                    if(node_counter > node_max_q):
                        break
                global_post_processing_len = len(lns)

            for tid in range(signal_dic['nthreads']):
                newest_possible_fn = 'demo_node_' + str(node_id) + '_thread_' + str(tid) + '_part_' + str(len(lns)) + '.log'

                cmd = 'tail -n ' + str(node_max_q) + " " + local_path + newest_possible_fn

                if(os.path.isfile(local_path + newest_possible_fn)):
                    
                    # print(cmd)
                    tail_ret = run_bg_cmd(cmd)

                    for ln in tail_ret:
                        # print('pln = json.loads ', ln)
                        if(ln[-1] == '}'):
                            pln = json.loads(ln)
                            post_processing_history[hostname].insert(0, pln['Q'])
                            node_counter += 1

                if(node_counter > node_max_q):
                    break

                # break

            while(len(post_processing_history[hostname]) > node_max_q):
                post_processing_history[hostname].pop()

            node_id += 1

        with open(slaves_path, 'w') as f:
            f.write(json.dumps(post_processing_history) + '\n')
            f.close()

        global_post_processing_history = post_processing_history

    if(signal_dic['app_name'] == 'MC'):
        #
        #given: {"count" : 2, "size" : 3, "group1" : [1,2,3], "group2" : [2,4,5]}
        #ori: {"mc" : 3, "count" : 2, "0" : [786496, 945665, 945664], "1" : [983073, 1012607, 989527]}
        slaves_path = args['localdir'] + "/slaves.json"
        # print("if(signal_dic['app_name'] == 'MC'):")
        # just read info from master_5q.log
        if(len(master_5q_log_last_line) > 1):
            pln = json.loads(master_5q_log_last_line)['agg_str']
            # print(pln)
            pln['size'] = pln.pop('mc')

            for i in range(pln['count']):
                ori_key = str(i)
                new_key = 'group' + str(i + 1)
                pln[new_key] = pln.pop(ori_key)

            with open(slaves_path, 'w') as f:
                f.write(json.dumps(pln) + '\n')
                f.close()

    #cp file
    return 0


#exits
def OnSignalDisappear(signal_dic):
    # global global_post_processing_history
    # global global_master_dic_list
    # global_post_processing_history = {}
    # global_master_dic_list = []
    # 

    bkp_path = args['bkpdir']

    cmd = 'mkdir -p ' + bkp_path
    print(cmd)
    os.system(cmd)

    cmd = 'cp -r ' + args['localdir'] + "/* " + bkp_path
    print(cmd)
    os.system(cmd)

    # cmd = 'rm -rf ' + args['localdir'] + "/*"
    # just remove slave folders
    for hostname in signal_dic['slaves']:
        cmd = 'rm -r ' + args['localdir'] + "/" + hostname
        print(cmd)
        os.system(cmd)

    #todo: remove slaves' folders
    return 0


if __name__ == "__main__":

    #rsync
    #cp master

    master_interval = float(args['interval'])
    slave_times = int(args['slave_interval'])

    print("master_interval: ", master_interval)
    print("slave_times: ", slave_times)
    print("localdir: ", args['localdir'])

    if(slave_times < 1):
        print("bad argument slave_interval")
        exit(0)

    OnAppStart()

    sleep_cnt = 0
    gminer_running = False
    while True:

        #暂时不考虑突然连续两次启动的情况
        run_bg_cmd("ls -al .")
        if(os.path.isfile(signal_file_name)):
            # print("os.path.isfile(signal_file_name)")
            if(not gminer_running):
                signal_dic = OnSignalAppear()
                gminer_running = True
                sleep_cnt = 0
            else:
                for proc in procs:
                    proc.wait()
                procs = []

            RunningMaster(signal_dic)

            if(sleep_cnt % slave_times == 0):
                RunningSlave(signal_dic)

            PostProcessing(signal_dic)

            sleep_cnt += 1
        else:
            if(gminer_running):
                #wait for procs
                for proc in procs:
                    proc.wait()
                procs = []

                #always performs the last sync
                RunningMaster(signal_dic)
                RunningSlave(signal_dic)

                for proc in procs:
                    proc.wait()
                procs = []

                PostProcessing(signal_dic)
                OnSignalDisappear(signal_dic)
                gminer_running = False
                exit(0)

        time.sleep(master_interval)
