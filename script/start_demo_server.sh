# Run this script in the root dir of the repo

# port of the web server
PORT=2333
unset FLASK_APP
export FLASK_APP=main.py

# on worker nodes, indicates where G-Miner workers writes logs
export GMINER_LOG_PATH=/home/cghuan/gminer_demo_log/
# on master node, indicates where the G-Miner application logs are merged
export GMINER_MERGE_LOG_PATH=/dev/shm/chhuang/merge-gminer/
export GMINER_HOME=$PWD

#rm -rf web/runtime-infos/*
#rm  web/runtime-infos
#rm -r tmp/*
#ln -s $GMINER_MERGE_LOG_PATH web/runtime-infos


mpirun -n 11 -ppn 1 -f machines.cfg python $GMINER_HOME/script/python/cluster-monitor.py -d $GMINER_MERGE_LOG_PATH > /dev/null &
cd web/
ls main.py
flask run --port $PORT
