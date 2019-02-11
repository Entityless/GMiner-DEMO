//Copyright 2018 Husky Data Lab, CUHK
//Authors: Hongzhi Chen, Miao Liu


#define USE_ATTRIBUTE

#include "core/subg-dev.hpp"

using namespace std;


struct gMatchContext
{
	unsigned long long count;
	int round;
};

ibinstream& operator << (ibinstream& m, const gMatchContext& v)
{
	m << v.count;
	m << v.round;
	return m;
}

obinstream& operator >> (obinstream& m, gMatchContext& v)
{
	m >> v.count;
	m >> v.round;
	return m;
}

ifbinstream& operator << (ifbinstream& m, const gMatchContext& v)
{
	m << v.count;
	m << v.round;
	return m;
}

ofbinstream& operator >> (ofbinstream& m, gMatchContext & v)
{
	m >> v.count;
	m >> v.round;
	return m;
}


class CountAgg :public Aggregator<gMatchContext, unsigned long long, unsigned long long>  //Context = unsigned long long
{
public:

	virtual ~CountAgg() {}

	virtual void init()
	{
		count_ = 0;
	}

	virtual void step_partial(gMatchContext &  v)
	{
		count_ += v.count;
	}

	virtual void step_final(unsigned long long * part)
	{
		count_ += *part;
	}

	virtual unsigned long long* finish_partial()
	{
		return &count_;
	}
	virtual unsigned long long* finish_final()
	{
		return &count_;
	}

	string get_agg_str(const vector<unsigned long long>& parts) override
	{
		unsigned long long total_parts = 0;

		for(auto v : parts)
		{
			total_parts += v;
		}

		char c[64];

		sprintf(c, "%ld", total_parts);

		return string(c);
	}

	string app_name() override
	{
		return "GM";
	}

	string sys_print_header() override
	{
		return "Current matched subgraph: ";
	}

	bool agg_sync_disabled() override
	{
		return true;
	}

	bool sys_agg_disabled() override
	{
		return false;
	}

private:
	unsigned long long count_;
};


class gMatchTask :public Task<VertexID, gMatchContext, char>
{
public:
	bool has_label(NodeT & node, char label)
	{
		AdjNodeList & adjlist = node.get_adjlist();
		for (int i = 0; i < adjlist.size(); i++)
		{
			if (adjlist[i].attr == label)
			{
				return true;
			}
		}
		return false;
	}

	void print_Q(vector<VertexID> & Q)
	{
		for (int i = 0; i < Q.size(); i++)
		{
			cout << Q[i] << "  ";
		}
		cout << endl;
	}

	void back_track(int level, SubgraphT & g, vector<VertexID> & Q, vector<VertexID> & nodes, unsigned long long & count)
	{
		level++;
		if (level == 1)
		{
			//match C
			for (int i = 0; i < nodes.size(); i++)
			{
				Q.push_back(nodes[i]);
				NodeT * c = g.get_node(nodes[i]);
				AdjNodeList & adjlist = c->get_adjlist();
				vector<VertexID> b_vec;
				for (int j = 0; j < adjlist.size(); j++)
				{
					if (adjlist[j].attr == 'b')
						b_vec.push_back(adjlist[j].id);
				}

				if (b_vec.size() >= 2)
				{
					for (int j = 0; j < b_vec.size(); j++)
					{
						VertexID n = b_vec[j];
						NodeT * b = g.get_node(n);
						if (has_label(*b, 'a')) //match in_b
						{
							Q.push_back(n);
							vector<VertexID> out_b = b_vec;
							out_b.erase(out_b.begin() + j);
							back_track(level, g, Q, out_b, count);
							Q.pop_back();
						}
					}
				}
				Q.pop_back();
			}
		}
		else if (level == 2)
		{
			//match out_b
			for (int i = 0; i < nodes.size(); i++)
			{
				Q.push_back(nodes[i]);
				NodeT * out_b = g.get_node(nodes[i]);
				AdjNodeList & adj = out_b->get_adjlist();
				for (int j = 0; j < adj.size(); j++)
				{
					if (adj[j].attr == 'd')
					{
						Q.push_back(adj[j].id);
						//print_Q(Q);
						
						// //append demo string; to_output_ is set by dump_context
						if(to_output_)
						{
							string to_append;
							if(count == 0)
							{
								to_append = "[";
							}
							else
							{
								to_append = ",[";
							}

							for(int i = 0; i < Q.size(); i++)
							{
								to_append += to_string(Q[i]);
								if(i != Q.size() - 1)
									to_append += ",";
							}
							to_append += "]";
							demo_str_ += to_append;
						}

						count++;
						Q.pop_back();
					}
				}
				Q.pop_back();
			}
		}
	}

	virtual bool compute(SubgraphT & g, ContextType & context, vector<VertexT *> & frontier)
	{
		int & round = context.round;
		round++;
		if (round == 1)
		{
			hash_map<VertexID, VertexT *> label_b;
			vector<VertexT *> label_c;
			//get the b,c vertexes from a.adjList
			for (int i = 0; i < frontier.size(); i++)
			{
				if (frontier[i]->attr == 'b')
					label_b[frontier[i]->id] = frontier[i];
				else if (frontier[i]->attr == 'c')
					label_c.push_back(frontier[i]);
			}
			set<AdjVertex> bcheck;
			for (int k = 0; k < label_c.size(); k++)
			{
				VertexT * node_c = label_c[k];
				AdjVtxList & adjlist = node_c->get_adjlist();
				AdjVtxList in_bset; //b vertexes already exist in subg
				AdjVtxList out_bset; //b vertexes need to be pulled in next round
				for (int i = 0; i < adjlist.size(); i++)
				{
					AdjVertex & node = adjlist[i];
					if (node.attr == 'b')
					{
						if (label_b.find(node.id) != label_b.end())
						{
							in_bset.push_back(node); //find node b in label_b
						}
						else
						{
							out_bset.push_back(node);
						}
					}
				}
				bool match_c = false;
				//in following two cases:
				//c is matched
				//case 1:
				//has only one in_b in a.adjList and at least one out_b to be pulled
				if (in_bset.size() == 1 && out_bset.size() > 0)
				{
					match_c = true;
					for (int i = 0; i < out_bset.size(); i++)
					{
						bcheck.insert(out_bset[i]);
					}
				}
				//case 2:
				//has at least two in_b in a.adjList, all of them are the candidates of out_b, pull them all
				else if (in_bset.size() >= 2)
				{
					match_c = true;
					for (int i = 0; i < in_bset.size(); i++)
					{
						bcheck.insert(in_bset[i]);
					}
					for (int i = 0; i < out_bset.size(); i++)
					{
						bcheck.insert(out_bset[i]);
					}
				}
				if (match_c)
				{
					NodeT c(node_c->id, node_c->attr);
					NodeT & a = g.get_nodes().front();
					g.add_edge(a, c);
					for (int i = 0; i < in_bset.size(); i++)
					{
						AdjVertex & v = in_bset[i];
						if (g.has_node(v.id))
						{
							NodeT * b = g.get_node(v.id);
							g.add_edge(*b, c);
						}
						else
						{
							NodeT & a = g.get_nodes().front();
							NodeT b(v.id, v.attr);
							g.add_edge(b, c);
							g.add_edge(a, b);
							g.add_node(b);
						}
					}
					g.add_node(c);
				}
			}

			//pull bcheck
			set<AdjVertex>::iterator s_iter;
			for (s_iter = bcheck.begin(); s_iter != bcheck.end(); s_iter++)
			{
				pull(*s_iter);
			}
			return true;

		}
		else if (round == 2)
		{
			//get all c vertexes in subg
			list<NodeT> & tmp = g.get_nodes();
			set<VertexID> c_set;
			for (list<NodeT>::iterator it = tmp.begin(); it != tmp.end(); ++it)
				if (it->attr == 'c')
					c_set.insert(it->id);

			for (int i = 0; i < frontier.size(); i++)
			{
				VertexT * b_p = frontier[i];
				AdjVtxList & adjlist = b_p->get_adjlist();
				set<VertexID> c_nb;
				AdjVtxList d_vec;
				for (int j = 0; j < adjlist.size(); j++)
				{
					AdjVertex & n = adjlist[j];
					if (n.attr == 'c')
					{
						c_nb.insert(n.id);
					}
					else if (n.attr == 'd')
					{
						d_vec.push_back(n);
					}
				}
				if (!d_vec.empty())
				{
					if (g.has_node(b_p->id))
					{
						for (int j = 0; j < d_vec.size(); j++)
						{
							AdjVertex & v = d_vec[j];
							NodeT * b = g.get_node(b_p->id);
							if (g.has_node(v.id))
							{
								NodeT * d = g.get_node(v.id);
								g.add_edge(*b, *d);
							}
							else
							{
								NodeT d(v.id, v.attr);
								g.add_edge(*b, d);
								g.add_node(d);
							}
						}
					}
					else
					{
						set<VertexID> interC;
						set<VertexID>::iterator sIter;
						set_intersection(c_nb.begin(), c_nb.end(), c_set.begin(), c_set.end(), inserter(interC, interC.begin()));

						NodeT b(b_p->id, b_p->attr);
						for (sIter = interC.begin(); sIter != interC.end(); sIter++)
						{
							NodeT * c = g.get_node(*sIter);
							g.add_edge(b, *c);
						}
						for (int j = 0; j < d_vec.size(); j++)
						{
							AdjVertex & v = d_vec[j];
							if (g.has_node(v.id))
							{
								NodeT * d = g.get_node(v.id);
								g.add_edge(b, *d);
							}
							else
							{
								NodeT d(v.id, v.attr);
								g.add_edge(b, d);
								g.add_node(d);
							}
						}
						g.add_node(b);
					}
				}
			}

			//count subgraph by backtracking
			list<NodeT> & nodes = g.get_nodes();
			VertexID a = nodes.front().id;

			vector<VertexID> c_nodes;
			for (list<NodeT>::iterator it = (++nodes.begin()); it != nodes.end(); ++it)
			{
				if (it->attr == 'c')
					c_nodes.push_back(it->id);
			}
			vector<VertexID> Q;
			Q.push_back(a);
			unsigned long long & count = context.count;

			back_track(0, g, Q, c_nodes, count);

			if(check_status())
			{
				//backup variables for back_track, enables dump_context
				Q_to_dump_ = Q;
				c_nodes_to_dump_ = c_nodes;
			}

			return false;
		}
	}

	//for dump context
	bool to_output_ = false;
	vector<VertexID> Q_to_dump_, c_nodes_to_dump_;

	bool check_status() override
	{
		if(context.count > 3 && context.count < 10)
		{
			return true;
		}
		return false;
	}

	void dump_context() override
	{
		//filter
		if(fine_task_counter_ % 2 != 0)
		{
			return;
		}

		to_output_ = true;
		if(!to_output_)
			return;

		demo_str_ = "{\"subg\":[";
		unsigned long long count = 0;

		back_track(0, subG, Q_to_dump_, c_nodes_to_dump_, count);

		demo_str_ += "], \"count\" : " + to_string(count);

		list<NodeT> & nodes = subG.get_nodes();

		//subG node list
		int tmp_cnt = 0;
		int nodes_sz = nodes.size();

		vector<pair<VertexID, VertexID>> edges;

		// set<VertexID> vtx_id_set; // adj must in this set
		// for (auto node : nodes)
		// {
		// 	vtx_id_set.insert(node.id);
		// }

		demo_str_ += ", \"subg_size\" : " + to_string(nodes_sz) + ", \"subg_list\" : [";
		for (auto node : nodes)
		{
			demo_str_ += to_string(node.id);
			if(tmp_cnt != nodes_sz - 1)
			{
				demo_str_ += ",";
			}

			for(auto adj : node.adjlist)
			{
				// if(vtx_id_set.count(adj.id) == 0)
				// {
				// 	continue;
				// }
				if(adj.id > node.id)
				{
					edges.push_back(make_pair(node.id, adj.id));
				}
			}

			tmp_cnt++;
		}

		demo_str_ += "], \"label_list\" : [";
		char tmp_str[2];
		tmp_str[1] = 0;
		tmp_cnt = 0;
		for (auto node : nodes)
		{
			// demo_str_ += "\"" + to_string(node.attr) + "\"";
			tmp_str[0] = node.attr;
			demo_str_ += "\"" + string(tmp_str) + "\"";
			if(tmp_cnt != nodes_sz - 1)
			{
				demo_str_ += ",";
			}
			tmp_cnt++;
		}
		//print the label

		demo_str_ += "], \"conn_list\" : [";

		for(int i = 0; i < edges.size(); i++)
		{
			demo_str_ += "[" + to_string(edges[i].first) + "," + to_string(edges[i].second) + "]";
			if(i != edges.size() - 1)
			{
				demo_str_ += ",";
			}
		}

		demo_str_ += "], \"conn_size\" : " + to_string(edges.size());

		demo_str_ += ", \"task_id\" : " + to_string(task_counter_);

		demo_str_ += "}\n";

		to_output_ = false;
	}
};

class gMatchSlave :public Slave<gMatchTask, CountAgg>
{
public:
	virtual gMatchTask * create_task(VertexT * v)
	{
		if (v->attr == 'a')
		{
			AdjVtxList & adjlist = v->get_adjlist();
			AdjVtxList label_b;
			AdjVtxList label_c;

			for (int i = 0; i < adjlist.size(); i++)
			{
				if (adjlist[i].attr == 'b')
					label_b.push_back(adjlist[i]);
				else if (adjlist[i].attr == 'c')
					label_c.push_back(adjlist[i]);
			}

			if (!label_b.empty() && !label_c.empty())
			{
				gMatchTask * task = new gMatchTask;
				task->pull(label_b);
				task->pull(label_c);
				NodeT node;
				v->set_node(node);
				task->subG.add_node(node);
				task->context.count = 0;
				task->context.round = 0;

				return task;
			}
			else
			{
				return NULL;
			}
		}
		else
		{
			return NULL;
		}
	}

	virtual VertexT* to_vertex(char* line)
	{
		VertexT* v = new VertexT;
		char * pch;
		pch = strtok(line, " ");
		v->id = atoi(pch);
		pch = strtok(NULL, " ");
		v->attr = *pch;
		strtok(NULL, "\t");
		while ((pch = strtok(NULL, " ")) != NULL)
		{
			AdjVertex item;
			item.id = atoi(pch);
			pch = strtok(NULL, " ");
			item.attr = *pch;
			pch = strtok(NULL, " ");
			item.wid = atoi(pch);
			v->adjlist.push_back(item);
		}

		sort(v->adjlist.begin(), v->adjlist.end());
		return v;
	}
};

class gMatchMaster :public Master<CountAgg>
{
public:
	virtual void print_result()
	{
		unsigned long long* agg = (unsigned long long*)get_agg();
		cout << "The size of matched subgraph is " << *agg << endl;
	}
};

class gMatchWorker :public Worker<gMatchMaster, gMatchSlave, CountAgg> {};

int main(int argc, char* argv[])
{
	init_worker(&argc, &argv);

	WorkerParams param;
	load_system_parameters(param);
	load_hdfs_config();

	gMatchWorker worker;
	CountAgg agg;
	worker.set_aggregator(&agg, 0);
	worker.run(param);

	worker_finalize();
	return 0;
}
