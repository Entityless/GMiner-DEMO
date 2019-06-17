#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/demo-env.sh

# port of the web server
export FLASK_APP=main.py
export FLASK_ENV=deployment

export GMINER_HOME=$DIR/../
cd $GMINER_HOME

mkdir -p $GMINER_MERGE_LOG_PATH

rm $GMINER_HOME/web/runtime-infos
ln -s $GMINER_MERGE_LOG_PATH $GMINER_HOME/web/runtime-infos
rm -r $GMINER_HOME/web/runtime-infos/*

if [[ -d tmp ]]; then
  rm -r tmp/*
fi

# cluster monitor
mpirun -n $NUM_WORKER -ppn 1 -f machines.cfg python $GMINER_HOME/script/python/cluster-monitor.py \
                                            -d $GMINER_MERGE_LOG_PATH \
                                            -nd $NETWORK_DEVICE \
                                            -nt $MAX_NETWORK_THROUGHPUT_MB \
                                            -dt $MAX_DISK_THROUGHPUT_MB > /dev/null &

# web server
cd web/
ls main.py
flask run --port $FLASK_PORT
