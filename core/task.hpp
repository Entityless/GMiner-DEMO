//Copyright 2018 Husky Data Lab, CUHK
//Authors: Hongzhi Chen, Miao Liu


#ifndef TASK_HPP_
#define TASK_HPP_

#include <vector>

#include "core/vertex.hpp"

#include "subgraph/node.hpp"
#include "subgraph/subgraph.hpp"

using namespace std;


template <class KeyT, class ContextT = char, class AttrT=char>
class Task
{
public:
	// comment: only KeyT = VertexID is supported completely,
	// because Subgraph only support VertexID to add\delete\find Node
	typedef KeyT KeyType;
	typedef ContextT ContextType;
	typedef AttrT AttrType;

	typedef Task<KeyT, ContextT, AttrT> TaskT;
	typedef Vertex<TaskT> VertexT;
	typedef Node<TaskT> NodeT;
	typedef Subgraph<NodeT> SubgraphT;

	typedef typename VertexT::AdjVtxT AdjVertex;
	typedef typename VertexT::AdjList AdjVtxList;
	typedef typename VertexT::AdjIter AdjVtxIter;

	typedef typename NodeT::AdjNodeT AdjNode;
	typedef typename NodeT::AdjList AdjNodeList;
	typedef typename NodeT::AdjIter AdjNodeIter;

	KeyT seed_key;
	SubgraphT subG;
	vector<int> to_request;  // vertex to pull from remote workers
	AdjVtxList to_pull;  // vertices to be pulled for using in the next round
	ContextType context;

	int task_counter_ = -1;//indicates how many tasks has been finished by the current thread, assigned in slave.tpp, used in app code
	int fine_task_counter_ = -1;//only record tasks that "check_status() == true"
	string demo_str_;//used for demo or debug. If not empty (modified in app code), will be written to file. Better to be used for logging in granularity of result (a matched graph, a triangle or a cluster), but not recommended for dumping a full task
	// bool demo_empty_ = false;//This flag should be modified in app code, and accessed by the system code. This flag indecates that the task should have get a output string, but not.
	// bool force_output_ = false;//This should be modified in system code, and accessed by the app code. When demo_empty_ of the last task (of a specific task) is true, this shall be true, telling the app code to write demo/debug string

	Task();

	virtual ~Task() {}

	virtual bool compute(SubgraphT & g, ContextType & context, vector<VertexT *> & frontier) = 0;

	//when a task is "completed", it does not means that the task is "successful"
	//user can override this function, and judge this by the context of a specific task
	virtual bool check_status(){return false;}

	//for logging in granularity of task, this function can be overridden
	//you are recommended to use fine_task_counter_ in this function to decide whether to write or not
	// virtual string dump_context(){return "";}
	virtual void dump_context(){}//to improve efficiency

	// to be used by users in UDF compute(.)
	void pull(const AdjVertex & v);
	void pull(AdjVtxList & adjlist);

	// user can implement their self-defined cost model strategy to judge the movability
	bool movable();

	// put remote-items in to_pull into to_request
	void set_to_request();

	bool is_request_empty();
};

template <class KeyT, class ContextT = char, class AttrT=char>
ibinstream& operator<<(ibinstream& m, const Task<KeyT, ContextT, AttrT>& v);

template <class KeyT, class ContextT = char, class AttrT=char>
obinstream& operator>>(obinstream& m, Task<KeyT, ContextT, AttrT>& v);

template <class KeyT, class ContextT = char, class AttrT=char>
ifbinstream& operator<<(ifbinstream& m, const Task<KeyT, ContextT, AttrT>& v);

template <class KeyT, class ContextT = char, class AttrT=char>
ofbinstream& operator>>(ofbinstream& m, Task<KeyT, ContextT, AttrT>& v);


#include "task.tpp"

#endif /* TASK_HPP_ */
