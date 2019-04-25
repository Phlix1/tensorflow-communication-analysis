from opMgr import opMgr
from core import core
import sys
import networkx as nx
from math import floor
import random

NUM_OF_CORES = 20
HEAD_PERCENT = 0
TAIL_PERCENT = 0.1
FLOW_MAGNIFY = 1

# GLOBAL VARIABLES
# dict for all ops
op_mgr = opMgr()
# dict for all flows
flowPri = {}
flowDep = {}
# list record the task status
finList = []
# unFinList only keep the computing tasks
unFinList = []
# ready computing tasks
readyList = []
# core set (plus one for flows, index 0)
coreList = []

flow_sum = 0.0
computing_sum = 0.0
# init the dict
def initEnv():
    op_mgr.recover_ops("./vgg16-1_1-128-op.pkl")
    for key in op_mgr.op_dict.keys():
        if (op_mgr.op_dict[key].op_type == 'N'):
            op_mgr.op_dict[key].op_size *= FLOW_MAGNIFY
    global computing_sum
    for key in op_mgr.op_dict.keys():
        if (op_mgr.op_dict[key].op_type == 'C'):
            unFinList.append(key)
            computing_sum += op_mgr.op_dict[key].op_size
    for i in range(0,NUM_OF_CORES + 1):
        newCore = core()
        coreList.append(newCore)
    #print(coreList)
    print("Sum load of %d computing is %f" % (len(unFinList), computing_sum))
    #print(len(unFinList))
    #op_mgr.ops_show()

# assign the priorities for all flows
def assignPri():
    flow_num = 0
    global flow_sum
    for key in op_mgr.op_dict.keys():
        if (op_mgr.op_dict[key].op_type == 'N'):
            flow_num += 1
            flow_sum += op_mgr.op_dict[key].op_size
    print("Sum load of %d flow is %f" % (flow_num, flow_sum))


    topo = []
    for i in range(0, flow_num):
        for key in op_mgr.op_dict.keys():
            if (op_mgr.op_dict[key].op_index == i) and op_mgr.op_dict[key].op_type == 'N':
                topo.append(key)
    
    print(topo)
    order = topo
    #order.reverse()
    '''
    # find a topo sort of all flows
    # find the depth of each flow
    # 1. build the digraph of this job
    job_dag = nx.DiGraph()
    for key in op_mgr.op_dict.keys():
        job_dag.add_node(key)
    #print(job_dag.number_of_nodes())
    for key in op_mgr.op_dict.keys():
        if len(op_mgr.op_dict[key].op_input) != 0:
            for input_op in op_mgr.op_dict[key].op_input:
                job_dag.add_edge(input_op, key)
    #print(job_dag.number_of_edges())
    topo = []
    for key in list(nx.topological_sort(job_dag)):
        if (op_mgr.op_dict[key].op_type == 'N'):
            topo.append(key)
    #print(len(topo))
    #rint(topo)
    order = topo
    #order.reverse()
    #print(order)
    head_num = floor(len(topo)*HEAD_PERCENT)
    shuffle_1 = order[head_num:]
    random.shuffle(shuffle_1)
    order[head_num:] = shuffle_1
    #print(len(order))

    '''
    # inser the flows into prio
    for i in range(0, len(order)):
        flowPri[str(i+1)] = order[i]
    #print(flowPri)



# get next time
def nextTime(last_min_time):
    min_time = sys.float_info.max
    for i in range(0, NUM_OF_CORES+1):
        if coreList[i].next_time < min_time and coreList[i].next_time > last_min_time:
            min_time = coreList[i].next_time
    #print("@@@@ time %f, %f, %f" % (coreList[0].next_time, coreList[1].next_time, coreList[2].next_time))
    #print(min_time)
    return min_time 

# check if a computing task is ready
def checkReady(task_name):
    if (len(op_mgr.op_dict[task_name].op_input) == 0):
        return True
    else:
        for parent_task in op_mgr.op_dict[task_name].op_input:
            if parent_task in finList:
                continue
            else:
                return False
        return True

# print simulation stats
def printStats():
    print("========  Simulation Summary ========")
    for i in range(0, NUM_OF_CORES + 1):
        if (len(coreList[i].task_list) > 0):
            print("CORE %d :" % i)
            print("Task number : %d" % len(coreList[i].task_list))
            print("Finish time : %f" % coreList[i].finish_time)
    
# begin simulate
def simulate():
    print("========  Simulation Begin ========")
    step = 0
    while (len(unFinList) != 0):
    #while (step <= 194):
        #print(coreList[1].finish_time)
        step = step + 1
        next_time = nextTime(0.0)
        #print("===step %d, time %f" %(step, next_time))
        #print("= 11 time %f, %f, %f" % (coreList[0].next_time, coreList[1].next_time, coreList[2].next_time))
        # initial state
        if next_time == sys.float_info.max:
            # add first flow to the core[0]
            #print("Initial State")
            coreList[0].task_list.append(flowPri['1'])
            coreList[0].time_list.append(op_mgr.op_dict[flowPri['1']].op_size)
            coreList[0].next_time = coreList[0].time_list[-1]
            coreList[0].finish_time = coreList[0].time_list[-1]
            #print(coreList[0].next_time)
            for task in unFinList:
                if checkReady(task) == True:
                    unFinList.remove(task)
                    readyList.append(task)
            #print(len(readyList))
            if len(readyList) <= NUM_OF_CORES:
                #print("enough cores")
                i = 1
                for task in readyList:
                    coreList[i].task_list.append(readyList[0])
                    coreList[i].time_list.append(op_mgr.op_dict[readyList[0]].op_size)
                    coreList[i].next_time = op_mgr.op_dict[readyList[0]].op_size
                    coreList[i].finish_time = coreList[i].next_time
                    readyList.remove(readyList[0])
                    i = i + 1
            else:
                #print("not enough cores")
                for i in range(1, NUM_OF_CORES + 1):
                    #print(i)
                    coreList[i].task_list.append(readyList[0])
                    coreList[i].time_list.append(op_mgr.op_dict[readyList[0]].op_size)
                    coreList[i].next_time = coreList[i].time_list[-1]
                    #print(coreList[i].next_time)
                    coreList[i].finish_time = coreList[i].next_time
                    readyList.remove(readyList[0])
            #print(len(readyList))
        # normal state
        else:
            # get all new finished tasks in all cores
            for i in range(0, NUM_OF_CORES + 1):
                if coreList[i].next_time == next_time:
                    newFinTask = coreList[i].task_list[-1]
                    if newFinTask not in finList:
                        finList.append(newFinTask)
                        #print("%d tasks have finished, new task is %s . " % (len(finList), newFinTask))
            #print(len(finList))
            #print(newFinTask)
            # get ready tasks
            # 1. get ready computing tasks
            for task in unFinList:
                if checkReady(task) == True:
                    unFinList.remove(task)
                    readyList.append(task)
            #print("Num of ready tasks is %d and flow id is %d" % (len(readyList), len(coreList[0].task_list)))
            # assign ready tasks to all cores
            for i in range(0, NUM_OF_CORES + 1):
                # need action at this time
                if coreList[i].next_time == next_time:
                    # for the network core
                    if i == 0:
                        newFlowIndex = len(coreList[0].task_list) + 1
                        if newFlowIndex <= len(flowPri):
                            coreList[0].task_list.append(flowPri[str(newFlowIndex)])
                            new_time = next_time + op_mgr.op_dict[flowPri[str(newFlowIndex)]].op_size
                            coreList[0].time_list.append(new_time)
                            coreList[0].next_time = new_time
                            coreList[0].finish_time = new_time
                    # for computing cores
                    else:
                        if len(readyList) != 0:
                            coreList[i].task_list.append(readyList[0])
                            new_time = next_time + op_mgr.op_dict[readyList[0]].op_size
                            coreList[i].time_list.append(new_time)
                            coreList[i].next_time = new_time
                            readyList.remove(readyList[0])
                            coreList[i].finish_time = next_time
            #print("= time %f, %f, %f" % (coreList[0].next_time, coreList[1].next_time, coreList[2].next_time))
            # if no task is assigned, the next_time need to be reset
            for i in range(0, NUM_OF_CORES + 1):
                if coreList[i].next_time == next_time:
                    time_2 = nextTime(next_time)
                    #print("########### Reset time to %f" % new_time)
                    coreList[i].next_time = time_2
        #print("= 22 time %f, %f, %f" % (coreList[0].next_time, coreList[1].next_time, coreList[2].next_time))

# do the experiments
def run_experiments():
    pass

# main function 
def main():
    initEnv()
    assignPri()
    simulate()
    printStats()


if __name__ == "__main__":
    main()