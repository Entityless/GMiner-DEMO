# Run this script in the root dir of the repo

export GMINER_MERGE_LOG_PATH=/dev/shm/chhuang/merge-gminer/

mpirun -n 11 -ppn 1 -f web/machines.cfg python script/python/cluster-monitor.py -d $GMINER_MERGE_LOG_PATH > /dev/null 2>&1 &
