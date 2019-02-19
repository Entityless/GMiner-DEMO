PORT=2333
unset FLASK_APP
export FLASK_APP=main.py

mpirun -n 11 -ppn 1 -f web/machines.cfg python script/python/cluster-monitor.py > /dev/null 2>&1 &
cd web/
ls main.py
flask run --port $PORT
