//Copyright 2018 Husky Data Lab, CUHK
//Authors: Hongzhi Chen, Miao Liu


#ifndef SLAVE_HPP_
#define SLAVE_HPP_

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <condition_variable>
#include <iostream>
#include <map>
#include <mutex>
#include <queue>
#include <thread>
#include <vector>
#include <chrono>

#include "util/aggregator.hpp"
#include "util/communication.hpp"
#include "util/global.hpp"
#include "util/hdfs_core.hpp"
#include "util/minhash.hpp"
#include "util/serialization.hpp"
#include "util/slave_commun.hpp"
#include "util/type.hpp"

#include "core/ref_cache.hpp"
#include "core/task.hpp"
#include "core/task_pipeline.hpp"
#include "core/task_sorter.hpp"
#include "core/vertex.hpp"
#include "core/vertex_table.hpp"

using namespace std;


template <class TaskT,  class AggregatorT = DummyAgg> //user-defined types for vertexID, adjacency-list items
class Slave
{
public:
	//PART 0 =======================================================
	//typedef

	typedef typename TaskT::VertexT VertexT;
	typedef typename TaskT::NodeT NodeT;

	typedef typename TaskT::AdjVertex AdjVertex;
	typedef typename TaskT::AdjVtxList AdjVtxList;
	typedef typename TaskT::AdjVtxIter AdjVtxIter;

	typedef typename TaskT::AdjNode AdjNode;
	typedef typename TaskT::AdjNodeList AdjNodeList;
	typedef typename TaskT::AdjNodeIter AdjNodeIter;

	typedef typename TaskT::SubgraphT SubgraphT;
	typedef typename TaskT::ContextType ContextT;

	typedef typename VertexT::KeyT KeyT;
	typedef typename VertexT::AttrT AttrT;

	typedef ktpair<signT, TaskT> KTpair;
	typedef vector<TaskT*> TaskVec;

	typedef typename AggregatorT::PartialType PartialT;
	typedef typename AggregatorT::FinalType FinalT;

	typedef hash_map<KeyT, int> CountMap;
	typedef typename CountMap::iterator CountMapIter;

	typedef hash_set<KeyT> IDSet;
	typedef typename IDSet::iterator IDSetIter;

	//PART 1 =======================================================
	//constructor, destructor, public run

	Slave();

	virtual ~Slave()
	{
		local_table_.clear();
		cache_table_.clear();
		rm_dir(PQUE_DIR);
		rm_dir(MERGE_DIR);
	}

	void WriteSignalFile();
	void run(const WorkerParams& params);

	//PART 2 =======================================================
	//user-defined functions
	virtual VertexT* to_vertex(char* line) = 0;
	virtual TaskT* create_task(VertexT* v) = 0;
	virtual VertexT* respond(const VertexT* v);

private:
    
	//PART 3 =======================================================
	//communication primitives

	void set_req(ibinstream & m, vector<KeyT>& request);

	void set_end_tag(ibinstream & m); //negative worker ID means that work has finished its computation

	void set_steal(ibinstream & m);

	int set_resp(ibinstream & m, obinstream & um); //return requester machine ID, -1 means end-tag

	//PART 4 =======================================================
	//high level functions for system

	bool wait_to_start();

	void load_graph(const char* inpath);

	void grow_tasks(int tid);

	void dump_tasks(TaskVec& tasks);

	TaskT * recursive_compute(TaskT* task, int tid);

	void pull_PQ_to_CMQ();

	void pull_CMQ_to_CPQ();

	void pull_CPQ_to_taskbuf(int tid);

	void run_to_no_task();

	void report_to_master(unsigned long long mem_tasks, unsigned long long disk_tasks);

	void recv_run();

	void end_recver();

	void report();

	void end_report();

	void agg_sync();
	void sys_sync();

	void context_sync();

	void end_sync();

	void debug();

	void thread_demo_str_init();
	void thread_demo_str_period();//call in sys_sync, to switch file name
	void thread_demo_str_compute(const string& demo_str, int tid);
	void thread_demo_str_finalize();

	int GetAndIncreaseCounter();
	void IncreaseComputingTaskCount();
	void DecreaseComputingTaskCount();

	//PART 5 =======================================================
	//members

	VertexTable<KeyT, VertexT> local_table_; 	//key-value store of my vertex portion
	RefCache<KeyT, VertexT> cache_table_; 		//cache the remote vertices

	int cache_size_;			//number of vertices allowed in cache
	bool cache_overflow_;  	//record the status of cache

	atomic_int merged_file_num_;
    atomic_int task_count_;
	bool is_end_;
	bool report_end_;

	//---------------------- multiple-threads ----------------------
	int threadpool_size_;	//number of threads in threadpool
	vector<thread> threadpool_;

	TaskPipeline<TaskT> task_pipeline_;
	TaskSorter<TaskT> task_sorter_;

	mutex end_lock_;
	condition_variable end_cond_;

	mutex commun_lock_;
	condition_variable commun_cond_;

	mutex compute_lock_;
	condition_variable compute_cond_;

	mutex agg_lock_;

	static const int VTX_REQ_MAX_GAP = 10;
	atomic_int vtx_req_count_, vtx_resp_count_;
	mutex vtx_req_lock_;
	condition_variable vtx_req_cond_;

	pthread_spinlock_t task_counter_lock_;
	volatile int task_counter_ = 0;//should not directly access this variable!

	struct ThreadDemoT
	{
		FILE* log_file = NULL;
		pthread_spinlock_t file_lock, task_counter_lock;
		volatile int task_counter = 0, fine_task_counter = 0;
		bool force_output = false;
		ThreadDemoT()
		{
			pthread_spin_init(&file_lock, 0);
			pthread_spin_init(&task_counter_lock, 0);
		}

		int GetAndIncreaseCounter()
		{
			pthread_spin_lock(&task_counter_lock);
			int task_counter_before = task_counter++;
			pthread_spin_unlock(&task_counter_lock);
			return task_counter_before;
		}

		int GetAndIncreaseFineCounter()
		{
			pthread_spin_lock(&task_counter_lock);
			int task_counter_before = fine_task_counter++;
			pthread_spin_unlock(&task_counter_lock);
			return task_counter_before;
		}
	} __attribute__((aligned(128))); //act as pair<FILE*, pthread_spinlock_t>, in case of false sharing

	static_assert(sizeof(ThreadDemoT) == (128), "ThreadDemoT struct not aligned to 128B");

	vector<ThreadDemoT> thread_demo_var_;
	int filename_part_ = 0;
	int sys_sync_time_ = 0;

	volatile int task_finished_count_ = 0, task_recycle_count_ = 0, task_to_cmq_count_ = 0, task_to_cpq_count_ = 0;
	// volatile int demo_task_store_ = 0, demo_candidate_retriever_ = 0, demo_task_executor_ = 0;//dedicated for demo monitor
	volatile int computing_task_count_ = 0;
	int last_task_finished_ = 0, last_task_recycle_ = 0, last_task_to_cmq_ = 0, last_task_to_cpq_ = 0;
};


#include "slave.tpp"

#endif /* SLAVE_HPP_ */
