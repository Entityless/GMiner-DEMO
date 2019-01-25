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

gminer_datasets = ['youtube', 'skitter', 'orkut']

gminer_apps = [
            {'tc': {'name':'Triangle Counting', 'param':None}} , 
            {'mc': {'name':'Max Clique', 'param':None}} , 
            {'gm': {'name':'Graph Matching', 'param':None}} , 
            {'cd': {'name': 'Community Detection', 'param': [cd_param]}}, 
            {'fco': {'name': 'Graph Clustering', 'param': [min_weight, min_core_size, min_result_size, diff_ratio, iter_round_max, cand_max_time]}}
            ]

gminer_persons = [
    {'name': 'xxx', 'img': 'husky.jpg', 'info': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'}    
    ]
gminer_sysconfig = [
    cache_size, num_comp_th, pipe_pop_num, pop_num, subg_size_t 
]
