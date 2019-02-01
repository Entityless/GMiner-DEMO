__all__ = ['gminer_datasets', 'gminer_apps', 'gminer_sysconfig']
cd_param = {
        'name':'k-threshold',
        'type':None,
        'help':'',
        'default': 3,
        }

min_weight = {
        'name': 'min-weight',
        'type': None,
        'help': 'threshold that only add the new candidates into subgraph with weight >= MIN_WEIGHT',
        'default': 0.92,
        }

min_core_size = {
        'name': 'min-core-size',
        'type': None,
        'help': 'threshold that only compute the seedtask with its subgraph size >= MIN_CORE_SIZE',
        'default': 3
        }

min_result_size = {
        'name': 'min-result-size',
        'type': None,
        'help':'threshold that only store the result cluster with size >= MIN_RESULT_SIZE',
        'default': 5
        }

diff_ratio = {
        'name': 'diff-ratio',
        'type': None,
        'help': 'threshold for judging two weight is similarity or not',
        'default': 0.001
        }

iter_round_max = {
        'name': 'iter-round-max',
        'type': None,
        'help': 'threshold that only compute number of iterations < ITER_ROUND_MAX with each task',
        'default': 10
        }

cand_max_time = {
        'name': 'cand-max-time',
        'type': None,
        'help': 'threshold that only compute the top CAND_MAX_TIME*subgraph_size candidates in each round during computation',
        'default': 3
        }

cache_size = {
        'name': 'cache-size',
        'help': 'the size of cachetable in each worker',
        'default': 1000000
        }
num_comp_th = {
        'name': 'num-comp-thread',
        'help': 'number of threads in threadpool for task computation',
        'default': 10
        }
pipe_pop_num = {
        'name': 'pipe-pop-num',
        'help': 'number of tasks popped out each batch in the pipeline',
        'default': 100
        }
pop_num = {
        'name': 'pop-num',
        'help': 'number of tasks for pque pops tasks to remote worker during one stealing procedure',
        'default': 100
        }
subg_size_t = {
        'name': 'subg-size-t',
        'help': 'threshold that task can be moved to other workers only if its current subgraph size <= SUBG_SIZE_T',
        'default': 30
        }

gminer_datasets = ['youtube', 'skitter', 'orkut', 'friendster', 'dblp', 'tencent']

gminer_apps = [
            {'tc': {'name':'Triangle Counting', 'param':None}} , 
            {'mc': {'name':'Max Clique', 'param':None}} , 
            {'gm': {'name':'Graph Matching', 'param':None}} , 
            {'cd': {'name': 'Community Detection', 'param': [cd_param]}}, 
            {'fco': {'name': 'Graph Clustering', 'param': [min_weight, min_core_size, min_result_size, diff_ratio, iter_round_max, cand_max_time]}}
            ]

gminer_persons = [
    {'name': 'Hongzhi Cheng', 'img': 'chz.jpg', 'info': ' is a PhD student in the Department of Computer Science and Engineering, The Chinese University of Hong Kong. His research interests cover the broad area of distributed systems and databases, with special emphasis on large-scale graph processing systems, distributed data analytics systems.'},
    {'name': 'Xiaoxi Wang', 'img': 'noimage.jpg', 'info': ' is working as a research assistant in CUHK. She is interested in distributed machine learning'},
    {'name': 'Chenghuan Huang', 'img': 'hch.jpg', 'info': ' is a Research Assistant in the Department of Computer Science and Engineering, Chinese University of Hong Kong. He is familiar with parallel programming.'},
    {'name': 'Juncheng Fang', 'img': 'jc.jpg', 'info': ' is an undergraduate in the Department of Computer Science and Engineering, The Chinese University of Hong Kong. He is now interested in distributed system.'},
    {'name': 'Yifan Hou', 'img': 'hyf.jpg', 'info': ' is working toward the MPhil degree in the Department of Computer Science and Engineering, Chinese University of Hong Kong. He is interested in large-scale graph processing and graph embedding'},
    {'name': 'Changji Li', 'img': 'lcj.jpg', 'info': ' is currently a Master student in Department of Computer Science and Engineering, Chinese University of Hong Kong. He will pursue MPhil degree in CSE, CUHK as well whose research interests are about distributed computing system and large-scale graph processing.'},
    {'name': 'Jian Zhang', 'img': 'zj.jpg', 'info': ' is a PhD student in the Department of Computer Science and Engineering, The Chinese University of Hong Kong. He is now interested in distributed systems and high-performanced computation.'},
    ]
gminer_sysconfig = [
    cache_size, num_comp_th, pipe_pop_num, pop_num, subg_size_t 
]

def get_gminer_codes():
    keys = ['tc','mc','gm','cd','fco']
    filen = ['trianglecount.cpp','maxclique.cpp','graphmatch.cpp','community.cpp','focusCO.cpp']
    res = []
    for k, name in zip(keys, filen):
        with open('./apps/' + name) as f:
            a = f.read()
            res.append((k, a))
    return res

gminer_codes = get_gminer_codes()
