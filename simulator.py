from opMgr import opMgr
from core import core
import sys

NUM_OF_CORES = 1

# GLOBAL VARIABLES
# dict for all ops
op_mgr = opMgr()
# dict for all flows
flowPri = {}
# list record the task status
finList = []
# unFinList only keep the computing tasks
unFinList = []
# ready computing tasks
readyList = []
# core set (plus one for flows, index 0)
coreList = []
# init the dict
def initEnv():
    op_mgr.recover_ops("./resnet152-1_1-128-op.pkl")
    for key in op_mgr.op_dict.keys():
        if (op_mgr.op_dict[key].op_type == 'C'):
            unFinList.append(key)
    for i in range(0,NUM_OF_CORES + 1):
        newCore = core()
        coreList.append(newCore)
    #print(coreList)
    print(len(unFinList))
    #op_mgr.ops_show()

# assign the priorities for all flows
def assignPri():
    flow_num = 0
    for key in op_mgr.op_dict.keys():
        if (op_mgr.op_dict[key].op_type == 'N'):
            flow_num += 1
            flowPri[str(flow_num)] = op_mgr.op_dict[key].op_name
    print(flowPri)
    #print(flow_num)


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
        print("CORE %d :" % i)
        print("Task number : %d" % len(coreList[i].task_list))
        print("Finish time : %f" % coreList[i].finish_time)
    
# begin simulate
def simulate():
    print("========  Simulation Begin ========")
    step = 0
    while (len(unFinList) != 0):
    #while (step <= 194):
        step = step + 1
        next_time = nextTime(0.0)
        print("===step %d, time %f" %(step, next_time))
        #print("= 11 time %f, %f, %f" % (coreList[0].next_time, coreList[1].next_time, coreList[2].next_time))
        # initial state
        if next_time == sys.float_info.max:
            # add first flow to the core[0]
            print("Initial State")
            coreList[0].task_list.append(flowPri['1'])
            coreList[0].time_list.append(op_mgr.op_dict[flowPri['1']].op_size)
            coreList[0].next_time = coreList[0].time_list[-1]
            coreList[0].finish_time = next_time
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
                print("not enough cores")
                for i in range(1, NUM_OF_CORES + 1):
                    #print(i)
                    coreList[i].task_list.append(readyList[0])
                    coreList[i].time_list.append(op_mgr.op_dict[readyList[0]].op_size)
                    coreList[i].next_time = coreList[i].time_list[-1]
                    print(coreList[i].next_time)
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
                        print("%d tasks have finished, new task is %s . " % (len(finList), newFinTask))
            #print(len(finList))
            #print(newFinTask)
            # get ready tasks
            # 1. get ready computing tasks
            for task in unFinList:
                if checkReady(task) == True:
                    unFinList.remove(task)
                    readyList.append(task)
            print("Num of ready tasks is %d and flow id is %d" % (len(readyList), len(coreList[0].task_list)))
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
# main function 
def main():
    initEnv()
    assignPri()
    simulate()
    printStats()


if __name__ == "__main__":
    main()