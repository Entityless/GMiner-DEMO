sh script/use_youtube_label_6.sh
sh 6slaves.sh
mpiexec -genv MPIR_CVAR_CH3_EAGER_MAX_MSG_SIZE=134217728 -n 7 -f machines.cfg -ppn 1 ./release/gm