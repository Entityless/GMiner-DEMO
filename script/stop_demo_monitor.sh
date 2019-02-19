ps -efww|grep -w 'cluster-monitor'|grep -v grep|cut -c 9-15|xargs kill -9
