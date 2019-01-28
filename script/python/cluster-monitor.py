import os
import sys
import json
import argparse
import subprocess
import io
import time
import psutil
# json.encoder.FLOAT_REPR = lambda o: format(o, '.5f') # not works???

from mpi4py import MPI

comm = MPI.COMM_WORLD

my_rank = comm.Get_rank()
comm_sz = comm.Get_size()

if(comm_sz == 1):
    print("run this with mpi.")
    exit(0)

master_rank = comm_sz - 1

#by default, worker 2 is the master
is_master = (my_rank == master_rank)

parser = argparse.ArgumentParser()

#recognized by pssh
#should be positive integer
parser.add_argument('-i', '-interval', '--interval', help='Hostfile', default='0.5')
parser.add_argument('-d', '-localdir', '--localdir', help='Local path of merging outputs', default = '/dev/shm/chhuang/merge-gminer/')

args = vars(parser.parse_args())

space_strs = []
for i in range(1000):
    space_strs.append("")
    for j in range(i):
        space_strs[i] = space_strs[i] + " "

def get_timestamp():
    t = time.time()
    t = int(t * 1000 + 0.5);
    return t

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


def submit_bg_cmd(command):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return proc


def test_wait_bg_cmd(proc):
    #return a dic, ['ok']
    if(proc.poll() == None):
        return {'ok' : False}

    proc.wait() #this works

    lns_content = []
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
        if(line[-1] == '\n'):
            lns_content.append(line[:-1])
        else:
            lns_content.append(line)

    return {'ok' : True, 'out' : lns_content}


def get_hostname():
    return run_bg_cmd('hostname')[0]


def get_mem_swap_sz():
    ret_lns = run_bg_cmd('free -m')
    for ln in ret_lns:
        #if Swap
        if(ln[:3] == 'Swa'):
            swap = int(ln.split()[1])

        #if Mem
        if(ln[:3] == 'Mem'):
            mem = int(ln.split()[1])

    return mem, swap


def get_cur_used_mem():
    #condition1
#                  total        used        free      shared  buff/cache   available
#Mem:        1031824       18753      659891        7433      353179     1003603
#Swap:         20479          21       20458
    
    #condition2
#                 total       used       free     shared    buffers     cached
#Mem:         64183      13988      50195          0        476      10978
#-/+ buffers/cache:       2533      61649
#Swap:        20479        121      20358

    ret_lns = run_bg_cmd('free -m')

    pos_avail = ret_lns[0].find('avail')
    mem_ln_sp = ret_lns[1].split()

    if(pos_avail == -1):
        #condition2
        mem_used = int(mem_ln_sp[2]) - int(mem_ln_sp[5]) - int(mem_ln_sp[6])
    else:
        mem_used = int(mem_ln_sp[2])

    return mem_used


get_cpu_average_usage_async_p_list = []
last_cpu_usage = 0.0


def get_cpu_average_usage_async(sleep_interval):
    global get_cpu_average_usage_async_p_list
    global last_cpu_usage

    to_submit = True
    if(len(get_cpu_average_usage_async_p_list) * sleep_interval > 1.0):
        to_submit = False
    # if(len(get_cpu_average_usage_async_p_list) >= 4):
    #     to_submit = False

    if(to_submit):
        get_cpu_average_usage_async_p_list.insert(0, submit_bg_cmd('mpstat 1 1'))

    #check which column %idle is in, and where the 'average' is start
    test_dic = test_wait_bg_cmd(get_cpu_average_usage_async_p_list[-1])
    if(test_dic['ok']):
        get_cpu_average_usage_async_p_list.pop()
        av_ln_idx = -1
        av_hit = False
        usage_list = []
        for ln in test_dic['out']:
            av_ln_idx += 1
            
            if(ln.find('%idle') >= 0):
                av_hit = True
                # break
                #do not break; parse where '%idle' is
                ln_sp = ln.split()
                idle_idx = ln_sp.index('%idle')

            elif(av_hit):
                #get the idle
                ln_sp = ln.split()
                usage = 100.0 - float(ln_sp[idle_idx])
                usage_list.append(usage)
                break

        # print(test_dic['out'][3])
        last_cpu_usage = usage_list[0]
        return usage_list[0]
    else:
        return last_cpu_usage


em1_network_info_dic = {}

def get_network_em1_usage():
    global em1_network_info_dic

    current_time = time.time()

    #em1_network_info_dic[]
    recv = psutil.net_io_counters(pernic=True).get('em1').bytes_recv
    sent = psutil.net_io_counters(pernic=True).get('em1').bytes_sent

    ret = 0.0

    # max_network = 128 * 1024 * 1024 * 1.0     #1Gbps
    max_network = 128 * 2 * 1024 * 1024 * 1.0 # 2 * 1Gbps

    if('time' in em1_network_info_dic):
        ret = ((recv + sent) - (em1_network_info_dic['sent'] + em1_network_info_dic['recv'])) / max_network
        
    em1_network_info_dic['time'] = current_time
    em1_network_info_dic['sent'] = sent
    em1_network_info_dic['recv'] = recv

    if(ret < 0.0001):
        return 0.0

    return ret

ib0_network_info_dic = {}

def get_network_ib0_usage():
    global ib0_network_info_dic

    current_time = time.time()

    #ib0_network_info_dic[]
    recv = psutil.net_io_counters(pernic=True).get('ib0').bytes_recv
    sent = psutil.net_io_counters(pernic=True).get('ib0').bytes_sent

    ret = 0.0

    # max_network = 40 * 128 * 1024 * 1024 * 1.0     #40Gbps
    max_network = 40 * 128 * 2 * 1024 * 1024 * 1.0 # 2 * 40Gbps

    if('time' in ib0_network_info_dic):
        ret = ((recv + sent) - (ib0_network_info_dic['sent'] + ib0_network_info_dic['recv'])) / max_network
        
    ib0_network_info_dic['time'] = current_time
    ib0_network_info_dic['sent'] = sent
    ib0_network_info_dic['recv'] = recv

    if(ret < 0.0001):
        return 0.0

    return ret


root_disk_info_dic = {}

def get_root_disk_usage():
    # R = 280368(80072)KB/s, W = 192256KB/s, on worker 2 (CONF-1) (disk embedded buf make it hard to measure)
    # R = 313856KB/s, W = 205568KB/s, on worker 21 (CONF-2)
    # temporary treat as CONF-1

    global root_disk_info_dic

    current_time = time.time()

    read = psutil.disk_io_counters().read_bytes
    write = psutil.disk_io_counters().write_bytes

    ret = 0.0

    max_io = (280368 + 192256) * 1024 * 1.0 # (280368 + 192256) * KBps

    if('time' in root_disk_info_dic):
        ret = ((read + write) - (root_disk_info_dic['write'] + root_disk_info_dic['read'])) / max_io
        
    root_disk_info_dic['time'] = current_time
    root_disk_info_dic['write'] = write
    root_disk_info_dic['read'] = read

    if(ret < 0.0001):
        return 0.0

    return ret


if __name__ == "__main__":
    #read the hostfile
    sleep_interval = float(args['interval'])
    if(sleep_interval <= 0):
        sleep_interval = 0.5

    #get sys config
    mem, swap = get_mem_swap_sz()
    hostname = get_hostname()

    my_info_dic = {}

    #online data that will be refreshed
    online_list_of_dic_to_write = []
    offline_list_of_dic_to_write = []

    max_monitor_second = 60.0

    last_time = time.time()
    launch_time = last_time

    append_log_name = "{}/{}".format(args['localdir'], 'monitor-append.log')

    #clear output to append
    # if my_rank == master_rank:
    #     #
    #     f = open(append_log_name, 'w')
    #     f.close()

    while True:
        #run the command
        used_mem = get_cur_used_mem()
        free_mem = mem - used_mem

        cpu_usage = get_cpu_average_usage_async(sleep_interval) #this should be a integer list
        em1_usage = get_network_em1_usage()
        ib0_usage = get_network_ib0_usage()
        disk_usage = get_root_disk_usage()

        my_info_dic = {}
        if(my_rank == master_rank):
            #anyway, do not count the master on
            # my_info_dic['hn'] = hostname
            _ = 1
        else:
            # my_info_dic['hn'] = hostname
            my_info_dic['cpu'] = cpu_usage / 100.0
            my_info_dic['mem'] = (1.0 * used_mem) / mem
            my_info_dic['network'] = em1_usage
            my_info_dic['disk'] = disk_usage
            # my_info_dic['infiniband'] = ib0_usage

        host_info = comm.gather(my_info_dic, root = master_rank)

        my_info_dic['cpu'] = 0.0
        my_info_dic['mem'] = 0.0
        my_info_dic['network'] = 0.0
        my_info_dic['disk'] = 0.0
        # my_info_dic['infiniband'] = 0.0

        if my_rank == master_rank:
            #print the info
            #flush the stdout
            dic_count = 0.0
            for dics in host_info:
                if(not len(dics) == 0):
                    dic_count += 1.0
                    for key in my_info_dic:
                        my_info_dic[key] += dics[key]

            for key in my_info_dic:
                my_info_dic[key] /= dic_count
                if(my_info_dic[key] < 0.0001):
                    my_info_dic[key] = 0.0

            cur_time = time.time()
            for ele in online_list_of_dic_to_write:
                ele['time'] -= (cur_time - last_time)
            last_time = cur_time

            for key in my_info_dic:
                dic_to_append = {}
                dic_to_append['value'] = my_info_dic[key]
                dic_to_append['time'] = max_monitor_second
                dic_to_append['type'] = key
                online_list_of_dic_to_write.append(dic_to_append.copy())

                dic_to_append['time'] = cur_time - launch_time
                offline_list_of_dic_to_write.append(dic_to_append.copy())

                #append to offline json

            my_info_dic['time'] = cur_time
            print(json.dumps(my_info_dic))
            sys.stdout.flush()
            with open(append_log_name, 'a') as out_f:
                out_f.write(json.dumps(my_info_dic) + '\n')

            while(len(online_list_of_dic_to_write) > 0):
                if(online_list_of_dic_to_write[0]['time'] < 0.0):
                    online_list_of_dic_to_write.pop(0)
                else:
                    break

            with open(args['localdir'] + '/monitor-data.json', 'w') as f:
                f.write('[\n')
                for i in range(len(online_list_of_dic_to_write)):
                    f.write(json.dumps(online_list_of_dic_to_write[i]))
                    if(i != len(online_list_of_dic_to_write) - 1):
                        f.write(',\n')
                    else:
                        f.write('\n')
                f.write(']\n')
                f.close()

        # break
        comm.Barrier() #this is critical, because MPI_Gather on small data do not sync all nodes

        #if no barrier, the master will gradually fall behind slaves
        time.sleep(sleep_interval)
