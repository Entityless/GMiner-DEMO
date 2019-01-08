sh script/use_orkut_10.sh
sh 10slaves.sh
mpiexec -genv MPIR_CVAR_CH3_EAGER_MAX_MSG_SIZE=134217728 -n 11 -f machines.cfg -ppn 1 ./release/mc