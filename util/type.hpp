//Copyright 2018 Husky Data Lab, CUHK
//Authors: Hongzhi Chen, Miao Liu


#ifndef TYPE_HPP_
#define TYPE_HPP_

#include "util/global.hpp"
#include "util/ioser.hpp"
#include "util/serialization.hpp"


// key-task pair
template <class KeyT, class TaskT>
struct ktpair
{
	KeyT key;
	TaskT* task;

	ktpair();
	ktpair(KeyT _key, TaskT * _task);

	bool operator<(const ktpair & tmp) const;
	bool operator<=(const ktpair & tmp) const;

	friend ifbinstream& operator<<(ifbinstream& m, const ktpair& v)
	{
		m << v.key;
		m << v.task;
		return m;
	}

	friend ofbinstream& operator>>(ofbinstream& m, ktpair& v)
	{
		m >> v.key;
		m >> v.task;
		return m;
	}

	friend ibinstream& operator<<(ibinstream& m, const ktpair& v)
	{
		m << v.key;
		m << v.task;
		return m;
	}

	friend obinstream& operator>>(obinstream& m, ktpair& v)
	{
		m >> v.key;
		m >> v.task;
		return m;
	}
};


struct QueueMonitorT
{
	unsigned long long task_num_in_memory;
	unsigned long long task_num_in_disk;
	unsigned long long cmq_size;
	unsigned long long cpq_size;
	unsigned long long taskbuf_size;
};


static inline ibinstream& operator << (ibinstream& m, const QueueMonitorT& v)
{
	m << v.task_num_in_memory;
	m << v.task_num_in_disk;
	m << v.cmq_size;
	m << v.cpq_size;
	m << v.taskbuf_size;
	return m;
}

static inline obinstream& operator >> (obinstream& m, QueueMonitorT& v)
{
	m >> v.task_num_in_memory;
	m >> v.task_num_in_disk;
	m >> v.cmq_size;
	m >> v.cpq_size;
	m >> v.taskbuf_size;
	return m;
}


#include "type.tpp"

#endif /* TYPE_HPP_ */
