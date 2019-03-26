//Copyright 2018 Husky Data Lab, CUHK
//Authors: Hongzhi Chen, Miao Liu


template <class AggregatorT>
Master<AggregatorT>::Master()
{
	is_end_ = false;
}
template <class AggregatorT>
void Master<AggregatorT>::check_resume_file(){
	const char* GMINER_START_TIMESTAMP = getenv("GMINER_START_TIMESTAMP");
	const char* RESUME_PATH = getenv("GMINER_MERGE_LOG_PATH");
	string filename = string(RESUME_PATH) + "/" + string(GMINER_START_TIMESTAMP) + "/resume_file.txt"; // must be a finished file
	VertexID seed_id;
	map<string, vector<VertexID>> resume_info = {
		{"nodes", vector<VertexID>()},
		{"src", vector<VertexID>()},
		{"dst", vector<VertexID>()}
	};
	while(1){
		ifstream in(filename);
		if(in.is_open()){
			VertexID src, dst;
			in >> seed_id;
      cout << "[check_resume_file] " << filename << " seed_id:" << seed_id << endl;
			// read nodes
			while(!in.eof()){
				in >> src;
				if(src == finish_tag) break;
        cout << "[check_resume_file] delete node "<<src<<endl;
				resume_info["nodes"].push_back(src);
			}
			// read edges
			while(!in.eof()){
				in >> src >> dst;
        cout << "[check_resume_file] delete edge " << src << " " << dst << endl;
				resume_info["src"].push_back(src);
				resume_info["dst"].push_back(dst);
			}
			//master_bcast(seed_id);
			//int slave_id = recv_data<int>(MPI_ANY_SOURCE, DEMO_RESUME_CHANNEL);
			//send_data<map<string, vector<VertexID>>>(resume_info, slave_id, DEMO_RESUME_CHANNEL);
			// delete file stdio
			remove(filename.c_str());
      break;
		}
		this_thread::sleep_for(chrono::milliseconds(1000));
	}
}
template <class AggregatorT>
void Master<AggregatorT>::sys_sync()
{
	vector<QueueMonitorT> parts(get_num_workers());

	// MPI_Barrier(MPI_COMM_WORLD);
	master_gather(parts);

	//write queue info to file
	string file_name = DEMO_LOG_PATH + "master_5q.log";
	FILE* f = fopen(file_name.c_str(), "a");
	if(f)
	{
		fprintf(f, "{\"nodes\":");
		fprintf(f, "%d", parts.size() - 1);
		fprintf(f, ", \"compute_time\":");
		fprintf(f, "%f", get_running_wtime());

		int cnt = 0;

		for(auto v : parts)
		{
			if(cnt == parts.size() - 1)
				break;//the last one is always empty
			fprintf(f, ", \"%d\" : [%ld, %ld, %ld, %ld, %ld, %ld, %ld, %ld, %ld]", cnt, 
					v.task_num_in_memory, v.task_num_in_disk, v.cmq_size, v.cpq_size, v.taskbuf_size,
					v.task_store_to_cmq, v.cmq_to_cpq, v.cpq_to_task_store, v.cpq_finished);
			cnt++;
		}
	}

	//fake agg_sync
	AggregatorT* agg = (AggregatorT*)get_aggregator();
	if (agg != NULL)
	{
		if(!agg->sys_agg_disabled())
		{
			vector<Master<AggregatorT>::PartialT> parts(get_num_workers());
			// printf("before master gather\n");
			fflush(stdout);
			MPI_Barrier(MPI_COMM_WORLD);
			_global_dbg_flag = true;
			master_gather(parts);
			_global_dbg_flag = false;
			MPI_Barrier(MPI_COMM_WORLD);
			// printf("after master gather\n");
			fflush(stdout);

			string agg_str = agg->get_agg_str(parts);
			if(agg_str.size() != 0)
			{
				// printf("void Master<AggregatorT>::sys_sync(), %s\n", agg_str.c_str());
				if(f)
				{
					fprintf(f, ", \"agg_str\" : %s", agg_str.c_str());
				}
				printf("time = %.2f seconds, %s%s\n", get_running_wtime(), agg->sys_print_header().c_str(), agg_str.c_str());
			}
		}
	}

	if(f)
	{
		fprintf(f, "}\n");
		fflush(f);
		fclose(f);
	}
}

template <class AggregatorT>
void Master<AggregatorT>::agg_sync()
{
	AggregatorT* agg = (AggregatorT*)get_aggregator();
	if (agg != NULL)
	{
		vector<Master<AggregatorT>::PartialT> parts(get_num_workers());

		// MPI_Barrier(MPI_COMM_WORLD);
		master_gather(parts);
		for (int i = 0; i < get_num_workers(); i++)
		{
			if(i != MASTER_RANK)
			{
				Master<AggregatorT>::PartialT& part = parts[i];
				agg->step_final(&part);
			}
		}
		Master<AggregatorT>::FinalT* final = agg->finish_final();
		*((Master<AggregatorT>::FinalT*)global_agg) = *final;
		//Bcasting
		master_bcast(*final);
	}
}

template <class AggregatorT>
void Master<AggregatorT>::context_sync()
{
	AggregatorT* agg = (AggregatorT*)get_aggregator();
	if(AGG_SLEEP_TIME == 0.0 && SYS_SLEEP_TIME == 0.0)
	{
		//do agg_sync when all the tasks have been processed
		unique_lock<mutex> lck(end_lock_);
		while (!is_end_)
		{
			end_cond_.wait(lck);  //block the thread until end_cond is notified.
		}
	}
	else if(SYS_SLEEP_TIME == 0.0)//just agg_sync
	{
		while (!all_land(is_end_))  //do agg_sync periodically when at least one worker is still computing
		{
			this_thread::sleep_for(chrono::nanoseconds(uint64_t(AGG_SLEEP_TIME * (1000 * 1000 * 1000))));
			// MPI_Barrier(MPI_COMM_WORLD);
			if(!agg->agg_sync_disabled())
				agg_sync();
		}
	}
	else if(AGG_SLEEP_TIME == 0.0)
	{
		//clear sys file

		string file_name = DEMO_LOG_PATH + "master_5q.log";
		FILE* f = fopen(file_name.c_str(), "w");
		if(f)fclose(f);
		while (!all_land(is_end_))  //do agg_sync periodically when at least one worker is still computing
		{
			this_thread::sleep_for(chrono::nanoseconds(uint64_t(SYS_SLEEP_TIME * (1000 * 1000 * 1000))));
			// MPI_Barrier(MPI_COMM_WORLD);
			sys_sync();
		}
	}
	else
	{
		//clear sys file
		string file_name = DEMO_LOG_PATH + "master_5q.log";
		FILE* f = fopen(file_name.c_str(), "w");
		if(f)fclose(f);

		//do both sys_sync and agg_sync
		//if all worker runs on the same model of CPU, then the sleep_counter counter will be identical
		double sleep_counter = 0.0;
		double last_sys_sync = 0.0;
		double last_agg_sync = 0.0;
		double time_to_sleep = 0.0;

		while (!all_land(is_end_))
		{
			//decide how long to sleep, and which to run
			if(last_sys_sync - last_agg_sync > AGG_SLEEP_TIME - SYS_SLEEP_TIME)
			{
				//run agg
				last_agg_sync += AGG_SLEEP_TIME;

				time_to_sleep  = last_agg_sync - sleep_counter;
				this_thread::sleep_for(chrono::nanoseconds(uint64_t(time_to_sleep * (1000 * 1000 * 1000))));
				// MPI_Barrier(MPI_COMM_WORLD);
				if(!agg->agg_sync_disabled())
					agg_sync();

				sleep_counter = last_agg_sync;
			}
			else
			{
				//run sys
				last_sys_sync += SYS_SLEEP_TIME;

				time_to_sleep  = last_sys_sync - sleep_counter;
				this_thread::sleep_for(chrono::nanoseconds(uint64_t(time_to_sleep * (1000 * 1000 * 1000))));
				// MPI_Barrier(MPI_COMM_WORLD);
				sys_sync();

				sleep_counter = last_sys_sync;
			}
		}
	}
	agg_sync();
	sys_sync();
	print_result();
}

template <class AggregatorT>
void Master<AggregatorT>::end_sync()
{
	if(AGG_SLEEP_TIME == 0.0)
	{
		end_lock_.lock();
		is_end_ = true;
		end_lock_.unlock();
		end_cond_.notify_all();
	}
	else
	{
		is_end_ = true;
	}

	//rename signal file

	string signal_name_str = DEMO_LOG_PATH + "signal-file-gminer." + _given_timestamp_str;
	string signal_name_dst_str = DEMO_LOG_PATH + _given_timestamp_str + ".signal-file-gminer";
	string rm_signal_cmd_str = "mv " + signal_name_str + " " + signal_name_dst_str;
	system(rm_signal_cmd_str.c_str());
}

template <class AggregatorT>
void Master<AggregatorT>::start_to_work()
{
	master_bcastCMD(START);
}

template <class AggregatorT>
void Master<AggregatorT>::terminate()
{
	master_bcastCMD(TERMINATE);
}

template <class AggregatorT>
void Master<AggregatorT>::schedule_listen()
{
	while(1)
	{
		vector<unsigned long long> prog = recv_data<vector<unsigned long long>>(MPI_ANY_SOURCE, SCHEDULE_HEARTBEAT_CHANNEL);
		int src = prog[0];  //the slave ID
		Progress & p = progress_map_[src];
		if(prog[1] != -1)
		{
			p.memory_task_num = prog[1];
			p.disk_task_num = prog[2];
		}
		else
		{
			progress_map_.erase(src);
		}
		if(progress_map_.size() == 0)
			break;
	}
}

template <class AggregatorT>
int Master<AggregatorT>::progress_scheduler(int request_worker_id)
{
	//the result should not be the same worker
	int max = 0;
	int max_index = -1;
	map<int, Progress>::iterator m_iter;
	for(m_iter = progress_map_.begin(); m_iter != progress_map_.end(); m_iter++)
	{
		if(m_iter->second.disk_task_num > max)
		{
			max = m_iter->second.disk_task_num;
			max_index = m_iter->first;
		}
	}
	if(max_index != -1 && max_index != request_worker_id)
		return max_index;
	return NO_WORKER_BUSY;
}

template <class AggregatorT>
void Master<AggregatorT>::task_steal()
{
	int end_count = 0;
	while(end_count < (_num_workers-1))
	{
		int request_worker_id = recv_data<int>(MPI_ANY_SOURCE, SCHEDULE_REPORT_CHANNEL);
		int target_worker_id = progress_scheduler(request_worker_id);
		send_data(target_worker_id, request_worker_id, SCHEDULE_REPORT_CHANNEL);
		if(target_worker_id == NO_WORKER_BUSY)
			end_count++;
	}
}

template <class AggregatorT>
void Master<AggregatorT>::WriteSignalFile()
{
	string signal_name_str = DEMO_LOG_PATH + "signal-file-gminer." + _given_timestamp_str;

	bool to_exit = false;
	//check if signal file exists
	if(fopen(signal_name_str.c_str(), "r"))
	{
		//signal exists
		to_exit = true;

		printf("file \"%s\" found, potential conflict, exit now.\n",
			   signal_name_str.c_str());
	}

	master_bcast(to_exit);

	if(to_exit)
		exit(0);
	// assert(to_exit /*signal file exists*/);

	int name_len;
	char hostname[MPI_MAX_PROCESSOR_NAME];
	MPI_Get_processor_name(hostname, &name_len);

	// printf("my_rank == %d, %s, master\n", _my_rank, hostname);

	//generate signal file

	vector<string> hostnames(get_num_workers());
	master_gather(hostnames);

	string hn_list = "[";

	for(int i = 0; i < get_num_workers(); i++)
	{
		if(hostnames[i].size() > 0)
			hn_list += "\"" + hostnames[i] + "\"";
		if(i < get_num_workers() - 2)
			hn_list += ", ";
	}

	hn_list += "]";

	// printf("gathered slaves: %s\n", hn_list.c_str());
	// fflush(stdout);

	FILE* f = fopen(signal_name_str.c_str(), "w");

	if(f)
	{
		string signal_str = "{\"master\" : \"" + string(hostname) + "\", \"slaves\" : " + hn_list;

		signal_str += ", \"DEMO_LOG_PATH\" : \"" + DEMO_LOG_PATH + "\"";

		AggregatorT* agg = (AggregatorT*)get_aggregator();
		signal_str += ", \"app_name\" : \"" + agg->app_name() + "\"";
		signal_str += ", \"nthreads\" : " + to_string(NUM_COMP_THREAD);

		signal_str += "}\n";
		fprintf(f, signal_str.c_str());
		fclose(f);
	}
}

template <class AggregatorT>
void Master<AggregatorT>::run(const WorkerParams& params)
{
	WriteSignalFile();

	// if (dir_check(params.input_path.c_str(), params.output_path.c_str(), true, params.force_write) == -1)
	// {
	// 	terminate();
	// 	return;
	// }
	printf("Loading data from HDFS...\n");
	fflush(stdout);
	start_to_work();
	//============================================================

	//===========================init=============================
	init_timers();
	AggregatorT* agg = (AggregatorT*)get_aggregator();
	if (agg != NULL)
		agg->init();

	get_running_wtime();

	//============================ RUN ============================
	thread demo_resumer(&Master::check_resume_file, this);
	thread sync(&Master::context_sync, this);
	thread listen(&Master::schedule_listen,this);
	// MPI_Barrier(MPI_COMM_WORLD);
	thread steal(&Master::task_steal,this);
	//ResetTimer(MASTER_TIMER);
	//StopTimer(MASTER_TIMER);
	//MasterPrintTimer("XXX Time", MASTER_TIMER);

	int end_tag = 0;
	while(end_tag < (_num_workers-1))
	{
		int tag = recv_data<int>(MPI_ANY_SOURCE, MSCOMMUN_CHANNEL);
		if(tag == DONE)
		{
			end_tag++;
		}
	}
	end_sync();

	//join the left threads
	sync.join();
	listen.join();
	steal.join();
	demo_resumer.detach();
	
	printf("G-Miner application finished. Thanks for using.\n");
	fflush(stdout);
}
