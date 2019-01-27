/*-----------------------------------------------------

       @copyright (c) 2018 CUHK Husky Data Lab
              Last modified : 2018-12
  Author(s) : Chenghuan Huang(entityless@gmail.com)
:)
-----------------------------------------------------*/

#include "tid_mapper.hpp"

using namespace std;

TidMapper::TidMapper()
{
    pthread_spin_init(&lock_, 0);
}

void TidMapper::Register(int tid)
{
    pthread_spin_lock(&lock_);

    // unique_tid_map_.insert(make_pair(pthread_self(), unique_tid_map_.size()));
    // manual_tid_map_.insert(make_pair(pthread_self(), tid));
    int last_sz = unique_tid_map_.size();
    unique_tid_map_[pthread_self()] = last_sz;
    manual_tid_map_[pthread_self()] = tid;

    pthread_spin_unlock(&lock_);
}

// //I just don't know why this sometimes happens
// void TidMapper::RegisterFake()
// {
//     unique_tid_map_.insert(make_pair(pthread_self(), unique_tid_map_.size()));
//     manual_tid_map_.insert(make_pair(pthread_self(), unique_tid_map_.size() - 1));
// }

int TidMapper::GetTid()
{
    // pthread_spin_lock(&lock_);
    // if(manual_tid_map_.count(pthread_self()) == 0)
    // {
    //     //debug print
    //     printf("manual_tid_map_.count(pthread_self()) == 0\n");
    //     RegisterFake();
    // }
    // pthread_spin_unlock(&lock_);
    //bugs
    assert(manual_tid_map_.count(pthread_self()) != 0 /*maybe you should initial the instance of TidMapper in sequential region*/);
    return manual_tid_map_[pthread_self()];
}

int TidMapper::GetTidUnique()
{
    // pthread_spin_lock(&lock_);
    // if(unique_tid_map_.count(pthread_self()) == 0)
    // {
    //     //debug print
    //     printf("unique_tid_map_.count(pthread_self()) == 0\n");
    //     RegisterFake();
    // }
    // pthread_spin_unlock(&lock_);
    assert(unique_tid_map_.count(pthread_self()) != 0 /*maybe you should initial the instance of TidMapper in sequential region*/);
    return unique_tid_map_[pthread_self()];
}
