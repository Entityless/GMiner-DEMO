sh script/use_skitter_label_8.sh
sh 8slaves.sh
mpiexec -genv MPIR_CVAR_CH3_EAGER_MAX_MSG_SIZE=134217728 -n 9 -f machines.cfg -ppn 1 ./release/gm