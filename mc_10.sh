sh script/use_orkut_9.sh
sh 9slaves.sh
mpiexec -genv MPIR_CVAR_CH3_EAGER_MAX_MSG_SIZE=134217728 -n 10 -f machines.cfg -ppn 1 ./release/mc