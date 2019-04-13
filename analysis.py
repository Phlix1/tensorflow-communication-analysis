from LogRecordMgr import LogRecordMgr
from CommNodeMgr import CommNodeMgr
from StepInfoMgr import StepInforMgr
from utils import *
from matplotlib import pyplot as plt
import numpy as np
def comm_size_distri(comm_node_mgr_dict):
    # Analyse the distribution of parameter sizes
    # We set three types: 
    # Small: 1B~1KB
    # Medium: 1KB~1MB"
    # Large: >1MB
    sname = ["Small: 1B~1KB","Medium: 1KB~1MB","Large: >1MB"]
    def size_classify(size):
        if size<1000:
            return 0
        elif size>=1000 and size<1000000:
            return 1
        else:
            return 2
    total_distri = []
    model_name = []
    for model in comm_node_mgr_dict.keys():
        model_name.append(model)
        comm_node_mgr = comm_node_mgr_dict[model]
        distri = [0, 0, 0, 0]
        commnode_num = len(comm_node_mgr.commnode_list)
        for commnode in comm_node_mgr.commnode_list:
            size = commnode.get_datasize()*4
            distri[size_classify(size)] += 1/commnode_num
        total_distri.append(distri)
    model_name = tuple(model_name)
    model_num = len(total_distri)
    X = np.arange(model_num)+1
    width = 0.15
    for i in range(3):
        size_list = []
        for j in range(model_num):
            size_list.append(total_distri[j][i])
        plt.bar(X+width*i, size_list, width = width, label=sname[i])
    plt.xticks(np.arange(model_num)+ 1 + 1*width, model_name)
    plt.xticks(fontsize=8)
    plt.legend(loc="upper right")
    plt.show()

def latency_size(comm_node_mgr_dict):
    # Analyse the latency of small medium and large values
    # Note: time skew between machines, we need to use NTP/PTP
    small_num = 0
    small_latency = 0
    medium_num = 0
    medium_latency = 0
    large_num = 0
    large_latency = 0
    for comm_node_mgr in comm_node_mgr_dict.values():
        for commnode in comm_node_mgr.commnode_list:
            size = commnode.get_datasize()*4
            if size<1000:
                for stepid in commnode.response_starttime.keys():
                    latency = timestr_to_timestamp(commnode.response_endtime[stepid]) - \
                                     timestr_to_timestamp(commnode.response_starttime[stepid])
                    if latency>0:
                        small_latency += latency
                        small_num += 1
            elif size>=1000 and size<1000000:
                for stepid in commnode.response_starttime.keys():
                    latency = timestr_to_timestamp(commnode.response_endtime[stepid]) - \
                                      timestr_to_timestamp(commnode.response_starttime[stepid])
                    if latency>0:
                        medium_latency += latency
                        medium_num += 1
            else:
                for stepid in commnode.response_starttime.keys():
                    latency = timestr_to_timestamp(commnode.response_endtime[stepid]) - \
                                     timestr_to_timestamp(commnode.response_starttime[stepid])
                    if latency>0:
                        large_latency += latency
                        large_num += 1
    average_small_latency = small_latency / small_num
    average_medium_latency = medium_latency / medium_num
    average_large_latency = large_latency / large_num
    sname = ["Small","Medium","Large"]
    plt.barh(sname, [average_small_latency, average_medium_latency, average_large_latency])
    plt.show()
    print(average_small_latency, average_medium_latency, average_large_latency)


def comm_ratio_batchsize(stepinfo_mgr_dict):
    # Analyse the relationship betweent batchsize and comm ratio
    comm_comp_ratios = {}
    plot_ratios = []
    batchsize = list(stepinfo_mgr_dict.keys())
    batchsize = [int(i) for i in batchsize]
    batchsize.sort()
    batchsize = [str(i) for i in batchsize]
    for bs in batchsize:
        stepinfo_mgr = stepinfo_mgr_dict[bs]
        comm_comp_ratios[bs] = stepinfo_mgr.get_comm_comp_ratio()
        #plot_ratios.append(stepinfo_mgr.get_comm_comp_ratio())
    #plt.plot(batchsize, plot_ratios)
    #plt.show()
    return comm_comp_ratios

def tensorsize_respend(comm_node_mgr, log_record_mgr):
    # compare tensor sizes and the response end time of tensors
    # we only consider tensors satisfy the following conditions
    # 1. the medium and large size tensors
    # 2. tensors received by workers(sent by ps)
    nodename = []
    tensorsize = []
    respend = []
    for commnode in comm_node_mgr.commnode_list:
        size = commnode.get_datasize()*4
        if size>=1000 and "worker" in commnode.recvmachine:
            step_start_times = log_record_mgr.get_step_starttime()
            average_response_end = 0.0
            stepnum = 0
            for stepid in step_start_times.keys():
                if stepid in commnode.response_endtime.keys():
                    resp_timestamp = timestr_to_timestamp(commnode.response_endtime[stepid])
                    step_start_timestamp = timestr_to_timestamp(step_start_times[stepid])
                    average_response_end += resp_timestamp - step_start_timestamp
                    stepnum += 1
            average_response_end = average_response_end/stepnum
            nodename.append(commnode.nodename)
            tensorsize.append(size/1000000)
            respend.append(average_response_end)
    #plt.plot(nodename, tensorsize)      
    plt.plot(nodename, respend)  
    plt.show()

if __name__ == '__main__':
    
    model_list = ["Lenet", "AlexNet", "LSTM", "Siamese", "VGG16", "Inception", "ResNet152"]
    batchsize = ["1", "5", "10", "20", "40", "80", "120"]
    comm_node_mgr_dict = {}
    stepinfo_mgr_dict = {}
    '''
    for model in model_list:
        commnode_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+batchsize[0]+"-commnode.pkl"
        logrecord_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+batchsize[0]+"-logrecords.pkl"
        comm_node_mgr = CommNodeMgr()
        comm_node_mgr.recover_commnodes(commnode_savepath)
        comm_node_mgr_dict[model] = comm_node_mgr
    #comm_size_distri(comm_node_mgr_dict)
    latency_size(comm_node_mgr_dict)
    
    batchsize = ["20"]
    model_list = ["Lenet", "AlexNet", "LSTM", "Siamese", "VGG16", "Inception", "ResNet152"]
    model_comm_ratio = []
    for model in model_list:
        for bs in batchsize:
            commnode_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+bs+"-commnode.pkl"
            logrecord_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+bs+"-logrecords.pkl" 
            comm_node_mgr = CommNodeMgr()
            comm_node_mgr.recover_commnodes(commnode_savepath)
            log_record_mgr = LogRecordMgr()
            log_record_mgr.recover_logrecords(logrecord_savepath)
            stepinfo_mgr = StepInforMgr()
            stepinfo_mgr.add_from_commnode_logrecord(comm_node_mgr, log_record_mgr) 
            stepinfo_mgr_dict[bs] = stepinfo_mgr 
        comm_ratios = comm_ratio_batchsize(stepinfo_mgr_dict)
        model_comm_ratio.append(comm_ratios[batchsize[0]])
    plt.bar(model_list, model_comm_ratio)
    plt.xticks(fontsize=8)
    plt.show()
    '''
    commnode_savepath = "./tensorflow_results/"+model_list[1]+"Log/pre/"+model_list[1].lower()+"-"+batchsize[0]+"-commnode.pkl"
    logrecord_savepath = "./tensorflow_results/"+model_list[1]+"Log/pre/"+model_list[1].lower()+"-"+batchsize[0]+"-logrecords.pkl"
    comm_node_mgr = CommNodeMgr()
    comm_node_mgr.recover_commnodes(commnode_savepath)
    log_record_mgr = LogRecordMgr()
    log_record_mgr.recover_logrecords(logrecord_savepath)
    tensorsize_respend(comm_node_mgr, log_record_mgr)
