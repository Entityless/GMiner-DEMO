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
parser.add_argument('-m', '-maxmonitoritem', '--maxmonitoritem', help = 'Maximum count for web cluster monitor', default='300')

args = vars(parser.parse_args())

merger_dir = args['localdir']
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

#for SlavesLineReader
slave_line_history_list = []
slave_line_history_dic = {}
slave_finished_cnt = {}
slave_last_ret = ""

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

    dic_to_write['task_store_to_cmq'] = 0
    dic_to_write['cmq_to_cpq'] = 0
    dic_to_write['cpq_to_task_store'] = 0
    dic_to_write['cpq_finished'] = 0

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
        slave_finished_cnt[hostname] = 0

    os.system("mkdir -p " + args['localdir'] + "/" + local_signal_dic['master'])
    os.system("mkdir -p " + local_signal_dic['master'])

    #get the latest timestamp from runtime-infos/monitor-data.json
    # global_monitor_data_fn = "{}/{}".format(merger_dir, 'monitor-data.json')
    global_monitor_append_data_fn = "{}/{}".format(merger_dir, 'monitor-append.log')
    lns = run_bg_cmd('tail -n 4 {}'.format(global_monitor_append_data_fn))
    for ln in lns:
        lns_content = ln
        if(lns_content[-1] == '\n'):
            lns_content = lns_content[:-1]

        if(lns_content[-1] == ','):
            lns_content = lns_content[:-1]

        if(not lns_content[-1] == '}'):
            continue

        # print(lns_content)
        pln = json.loads(lns_content)
        if('time' in pln):
            local_signal_dic['time'] = pln['time']

    if(not 'time' in local_signal_dic):
        local_signal_dic['time'] = time.time()

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

dedicated_monitor_history = []
def GenDedicatedMonitorData(signal_dic):
    global dedicated_monitor_history
    #
    global_monitor_data_fn = "{}/{}".format(merger_dir, 'monitor-data.json')
    global_monitor_append_data_fn = "{}/{}".format(merger_dir, 'monitor-append.log')

    local_monitor_data_fn = "{}/{}/{}".format(merger_dir, args['timestamp'], 'monitor-data.json')

    time_to_append_min = signal_dic['time']
    if(len(dedicated_monitor_history) > 0):
        time_to_append_min = dedicated_monitor_history[-1]['time']

    # print("time_to_append_min = ", time_to_append_min)

    # tmp_timestamp_counter = {} #[<TS>] = [<monitor items>], pop atomically

    #if the history list is empty, load them all
    with open(global_monitor_data_fn, 'r') as in_f:
        in_f.close() #test
        # lns = in_f.readlines()
        lns = run_bg_cmd("tail -n 40 {}".format(global_monitor_append_data_fn))
        #atmoic append: only all keys inside a monitor

        for ln in lns:
            lns_content = ln
            if(lns_content[-1] == '\n'):
                lns_content = lns_content[:-1]

            if(lns_content[-1] == ','):
                lns_content = lns_content[:-1]

            if(not lns_content[-1] == '}'):
                continue

            # print(lns_content)
            pln = json.loads(lns_content)

            if(pln['time'] > time_to_append_min):
                # print("(pln['time'] > time_to_append_min)", pln)
                # if(not pln['time'] in tmp_timestamp_counter):
                #     tmp_timestamp_counter[pln['time']] = []
                #append to the list, pop when len == monitorkey
                # if(len(tmp_timestamp_counter[pln['time']]) == int(args['monitorkey'])):
                pln['time'] -= signal_dic['time']
                dedicated_monitor_history.append(pln)

                # turn out to be
                # with open(local_monitor_data_fn, 'a') as out_f:
                #     #
                #     out_f.write(str(json.dumps(pln) + '\n'))

    #from dedicated_monitor_history (list) to real data to display
    #potential stretch and compress

    max_item = int(args['maxmonitoritem'])
    #a mapping to dedicated_monitor_history
    history_len = len(dedicated_monitor_history)

    mappint_list = []

    if(history_len > 0):
        #get the keys
        key_list = []
        for key in dedicated_monitor_history[-1]:
            if(not key == 'time'):
                key_list.append(key)

        for i in range(max_item):
            int_mapping = int(((1.0 * i) / max_item) * history_len)

            if(int_mapping >= history_len):
                int_mapping = history_len - 1
            if(int_mapping < 0):
                int_mapping = 0

            mappint_list.append(int_mapping)

        with open(local_monitor_data_fn, 'w') as out_f:
            out_f.write('[\n')
            for i in range(max_item):
                # out_f.write(json.dumps(dedicated_monitor_history[mappint_list[i]]))
                for l in range(len(key_list)):
                    #
                    tmp_dic = {'value' : dedicated_monitor_history[mappint_list[i]][key_list[l]], 'time' : dedicated_monitor_history[mappint_list[i]]['time'], 'type' : key_list[l]}
                    out_f.write(json.dumps(tmp_dic))
                    if(not (i == max_item - 1 and l == len(key_list) - 1)):
                        out_f.write(',')
                    out_f.write('\n')
            out_f.write(']\n')

#called by post processing; always return a newest line of slaves' output
def SlavesLineReader(signal_dic):
    global slave_line_history_list
    global slave_line_history_dic
    global slave_finished_cnt
    global slave_last_ret

    #append history
    node_id = 0
    for hostname in signal_dic['slaves']:
        local_path = args['localdir'] + '/' + hostname + '/'
        finish_lns = run_bg_cmd("ls -l " + local_path + "| grep 'finish'") #somehow wasting

        #last glance to part slave_finished_cnt[hostname]
        if(len(finish_lns) != slave_finished_cnt[hostname]):
            #
            for tid in range(signal_dic['nthreads']):
                newest_possible_fn = local_path + 'demo_node_' + str(node_id) + '_thread_' + str(tid) + '_part_' + str(slave_finished_cnt[hostname]) + '.log'
                cmd = 'tail -n 1 ' + newest_possible_fn

                if(os.path.isfile(newest_possible_fn)):
                    tail_ret = run_bg_cmd(cmd)
                    if(len(tail_ret) == 0):
                        continue
                    ln = tail_ret[0]
                    if(ln[-1] == '}'):
                        #append this line
                        if(not ln in slave_line_history_dic):
                            slave_line_history_dic[ln] = 0
                            slave_line_history_list.append(ln)

            slave_finished_cnt[hostname] = len(finish_lns)

        #normal glance
        for tid in range(signal_dic['nthreads']):
            newest_possible_fn = local_path + 'demo_node_' + str(node_id) + '_thread_' + str(tid) + '_part_' + str(len(finish_lns)) + '.log'
            cmd = 'tail -n 1 ' + newest_possible_fn

            if(os.path.isfile(newest_possible_fn)):
                tail_ret = run_bg_cmd(cmd)
                if(len(tail_ret) == 0):
                    continue
                ln = tail_ret[0]
                if(ln[-1] == '}'):
                    #append this line
                    if(not ln in slave_line_history_dic):
                        slave_line_history_dic[ln] = 0
                        slave_line_history_list.append(ln)
        node_id += 1

    ret = ""

    #pop history
    if(len(slave_line_history_list) > 0):
        ret = slave_line_history_list.pop()
        slave_last_ret = ret
    else:
        ret = slave_last_ret

    return ret

def PostProcessing(signal_dic):
    # dedicated monitor data
    GenDedicatedMonitorData(signal_dic)

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

    with open(master_5q_path, 'w') as f:
        dic_to_write = {}
        dic_to_write['task_num_in_memory'] = 0
        dic_to_write['task_num_in_disk'] = 0
        dic_to_write['cmq_size'] = 0
        dic_to_write['cpq_size'] = 0
        dic_to_write['taskbuf_size'] = 0
        dic_to_write['task_store_to_cmq'] = 0
        dic_to_write['cmq_to_cpq'] = 0
        dic_to_write['cpq_to_task_store'] = 0
        dic_to_write['cpq_finished'] = 0

        if(len(global_master_dic_list) > 0):
            #[task_num_in_memory, task_num_in_disk, cmq_size, cpq_size, taskbuf_size]
            for i in range(global_master_dic_list[-1]['nodes']):
                stri = str(i)          
                dic_to_write['task_num_in_memory'] += global_master_dic_list[-1][stri][0]
                dic_to_write['task_num_in_disk'] += global_master_dic_list[-1][stri][1]
                dic_to_write['cmq_size'] += global_master_dic_list[-1][stri][2]
                dic_to_write['cpq_size'] += global_master_dic_list[-1][stri][3]
                dic_to_write['taskbuf_size'] += global_master_dic_list[-1][stri][4]
                dic_to_write['task_store_to_cmq'] += global_master_dic_list[-1][stri][5]
                dic_to_write['cmq_to_cpq'] += global_master_dic_list[-1][stri][6]
                dic_to_write['cpq_to_task_store'] += global_master_dic_list[-1][stri][7]
                dic_to_write['cpq_finished'] += global_master_dic_list[-1][stri][8]

        dic_to_write['task_num_in_memory_float'] = EvilMapping(dic_to_write['task_num_in_memory'])
        dic_to_write['task_num_in_disk_float'] = EvilMapping(dic_to_write['task_num_in_disk'])
        dic_to_write['cmq_size_float'] = EvilMapping(dic_to_write['cmq_size'])
        dic_to_write['cpq_size_float'] = EvilMapping(dic_to_write['cpq_size'])
        dic_to_write['taskbuf_size_float'] = EvilMapping(dic_to_write['taskbuf_size'])

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
    ## this cound be somehow complex; juse pick one line
    ## multiple file need to be processed
    if(signal_dic['app_name'] == 'GM' or signal_dic['app_name'] == 'TC'):
        slaves_path = args['localdir'] + "/slaves.json"

        # result_dic = json.loads(SlavesLineReader(signal_dic))
        result_line = SlavesLineReader(signal_dic)

        with open(slaves_path, 'w') as f:
            f.write(result_line + '\n')
            f.close()

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
