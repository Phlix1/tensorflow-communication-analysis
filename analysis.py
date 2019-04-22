from LogRecordMgr import LogRecordMgr
from CommNodeMgr import CommNodeMgr
from StepInfoMgr import StepInforMgr
from utils import *
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import t

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

def comm_size_CDF(comm_node_mgr_dict):
    X= ['$\mathrm{10}^{1}$', '$\mathrm{10}^{2}$', '$\mathrm{10}^{3}$', '$\mathrm{10}^{4}$', \
        '$\mathrm{10}^{5}$', '$\mathrm{10}^{6}$', '$\mathrm{10}^{7}$', '$\mathrm{10}^{8}$']
    MaxX = 8
    Xnum = 8
    for model in comm_node_mgr_dict.keys():
        comm_node_mgr = comm_node_mgr_dict[model]
        commnode_num = len(comm_node_mgr.commnode_list)
        temp_y = []
        for i in range(Xnum):
            cnum = 0
            for commnode in comm_node_mgr.commnode_list:
                if commnode.get_datasize()*4<pow(10,MaxX*(i+1)/Xnum):
                    cnum += 1
            temp_y.append(cnum/commnode_num)
        plt.plot(X, temp_y, '--', label=model)
    plt.legend()
    plt.xlabel("Parameter size(Bytes)")
    plt.ylabel("CDF")
    plt.grid()
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

def runtime_analysis(comm_node_mgr, log_record_mgr, model_name):
    # analyse the runtime information
    # we only consider tensors satisfy the following conditions
    # 1. the medium and large size tensors
    # 2. tensors received by workers(sent by ps)
    # we draw 4 subfigs
    # tensor size
    # receive time and using time
    # ready time and send time
    # request time
    nodename = []
    tensorsize = []
    respend = []
    usingtime = []
    sendtime = []
    respstart = []
    requesttime = []

    for commnode in comm_node_mgr.commnode_list:
        size = commnode.get_datasize()*4
        if size>=10 and "worker" in commnode.recvmachine:
            step_start_times = log_record_mgr.get_step_starttime()
            average_response_end = 0.0
            average_using_time = 0.0
            average_send_time = 0.0
            average_response_start = 0.0
            average_request_time = 0.0
            stepnum = 0
            stepid_list = list(step_start_times.keys())
            for stepid in stepid_list:
                if stepid in commnode.response_endtime.keys() and stepid in commnode.using_time.keys()\
                   and stepid in commnode.send_time.keys() and stepid in commnode.response_starttime.keys()\
                   and stepid in commnode.request_time.keys():
                    resp_timestamp = timestr_to_timestamp(commnode.response_endtime[stepid])
                    using_timestamp = timestr_to_timestamp(commnode.using_time[stepid])
                    send_timestamp = timestr_to_timestamp(commnode.send_time[stepid])
                    resp_start_timestamp = timestr_to_timestamp(commnode.response_starttime[stepid])
                    request_timestamp = timestr_to_timestamp(commnode.request_time[stepid])
                    step_start_timestamp = timestr_to_timestamp(step_start_times[stepid])
                    if using_timestamp - step_start_timestamp<0 or resp_timestamp - step_start_timestamp<0\
                       or request_timestamp - step_start_timestamp<0 or send_timestamp - step_start_timestamp<-1000\
                       or resp_start_timestamp - step_start_timestamp<-1000:
                        continue
                    average_response_end += resp_timestamp - step_start_timestamp
                    average_using_time += using_timestamp - step_start_timestamp
                    average_send_time += send_timestamp - step_start_timestamp
                    average_response_start += resp_start_timestamp - step_start_timestamp
                    average_request_time += request_timestamp - step_start_timestamp
                    stepnum += 1
            average_response_end = average_response_end/stepnum
            average_using_time = average_using_time/stepnum
            average_send_time = average_send_time/stepnum
            average_response_start = average_response_start/stepnum
            average_request_time = average_request_time/stepnum
            nodename.append(commnode.nodename)
            tensorsize.append(size/1000000)
            respend.append(average_response_end)
            usingtime.append(average_using_time)
            sendtime.append(average_send_time)
            respstart.append(average_response_start)
            requesttime.append(average_request_time)
    X = list(range(len(tensorsize)))
    #X = [str(i) for i in X]
    plt.subplot(221)
    plt.xlabel("Layer Index")
    plt.ylabel("Tensor Size(MB)")
    plt.title("Size of communication tensor")
    plt.bar(X, tensorsize, label="Size") 
    plt.grid()   
    #plt.xticks(fontsize=5) 
    plt.subplot(222)
    plt.xlabel("Layer Index")
    plt.ylabel("Time Stamp(s)")
    plt.title("Receiving time and Using time")
    plt.scatter(X, respend, color='r', s=10, label="receive time")
    plt.plot(X, usingtime, color='g',marker='x',markersize=5, label="using time")
    plt.legend()
    plt.grid()   
    #plt.xticks(fontsize=5)
    plt.subplot(223) 
    plt.xlabel("Layer Index")
    plt.ylabel("Time Stamp(s)")
    plt.title("Ready time and Send time")
    plt.scatter(X, sendtime, color='y', marker='x', s=10, label="ready time") 
    plt.scatter(X, respstart, color='k', marker='v', s=10, label="send time")
    plt.legend()
    plt.grid()  
    #plt.xticks(fontsize=5) 
    plt.subplot(224)
    plt.xlabel("Layer Index")
    plt.ylabel("Time Stamp(s)")
    plt.title("Request time")
    plt.scatter(X, requesttime, color='r', marker='^',s=10, label="request time")
    plt.grid()  
    #plt.xticks(fontsize=5)  
    plt.suptitle(model_name)
    plt.show()

def latency_vs_parasize(comm_node_mgr):
    para_latency_size = []
    X_size = []
    Xnum = 20
    MaxX = 8
    for i in range(Xnum):
        latency = []
        for commnode in comm_node_mgr.commnode_list:
            if "worker" in commnode.recvmachine and commnode.get_datasize()*4<pow(10,MaxX*(i+1)/Xnum) and \
               commnode.get_datasize()*4>pow(10,MaxX*(i)/Xnum):
                for stepid in commnode.request_time.keys():
                    if stepid in commnode.response_endtime.keys():
                        if timestr_to_timestamp(commnode.response_endtime[stepid])-\
                                        timestr_to_timestamp(commnode.request_time[stepid]) >10:
                            continue
                        latency.append(timestr_to_timestamp(commnode.response_endtime[stepid])-\
                                        timestr_to_timestamp(commnode.request_time[stepid]))
        if latency==[]:
            continue
        X_size.append(MaxX*(i+1)/Xnum)
        para_latency_size.append(np.array(latency))
    
    latency_mean = []
    latency_conf_interval = []

    for latency_value in para_latency_size:
        n = latency_value.size
        latency_mean.append(np.mean(latency_value))
        dof = n - 1         # degrees of freedom
        alpha = 1.0 - 0.65
        latency_std = np.std(latency_value)
        conf_interval = t.ppf(1-alpha/2., dof) * latency_std*np.sqrt(1.+1./n)
        latency_conf_interval.append(conf_interval)
    plt.errorbar(X_size,latency_mean, yerr=conf_interval, fmt='o',ecolor='r',color='b',elinewidth=2,capsize=4)
    plt.plot(X_size,latency_mean)
    plt.xlabel("Parameter Size( 10^i B)")
    plt.grid()
    plt.show()

def latency_vs_layerindex(comm_node_mgr):
    latency = []
    for commnode in comm_node_mgr.commnode_list:
        node_latency = []
        if "worker" in commnode.recvmachine:
            for stepid in commnode.request_time.keys():
                if stepid in commnode.response_endtime.keys():
                    if timestr_to_timestamp(commnode.response_endtime[stepid])-\
                                    timestr_to_timestamp(commnode.request_time[stepid]) >10:
                        continue
                    node_latency.append(timestr_to_timestamp(commnode.response_endtime[stepid])-\
                                        timestr_to_timestamp(commnode.request_time[stepid]))
        if node_latency==[]:
            continue        
        latency.append(np.array(node_latency))
    latency_mean = []
    latency_conf_interval = []
    for latency_value in latency:
        n = latency_value.size
        latency_mean.append(np.mean(latency_value))
        dof = n - 1         # degrees of freedom
        alpha = 1.0 - 0.95
        latency_std = np.std(latency_value)
        conf_interval = t.ppf(1-alpha/2., dof) * latency_std*np.sqrt(1.+1./n)
        latency_conf_interval.append(conf_interval)
    plt.errorbar(range(len(latency_mean)),latency_mean, yerr=latency_conf_interval, fmt='o',ecolor='r',color='b',elinewidth=1,capsize=5,markersize=3)
    #plt.plot(range(len(latency_mean)),latency_mean)
    plt.grid()
    plt.show()

def waittime_vs_layerindex(comm_node_mgr):
    waittime = []
    for commnode in comm_node_mgr.commnode_list:
        node_waittime = []
        if "worker" in commnode.recvmachine:
            for stepid in commnode.response_endtime.keys():
                if stepid in commnode.using_time.keys():
                    if timestr_to_timestamp(commnode.using_time[stepid])-\
                                    timestr_to_timestamp(commnode.response_endtime[stepid]) <0:
                        continue
                    #print(commnode.using_time[stepid], commnode.response_endtime[stepid])
                    node_waittime.append(timestr_to_timestamp(commnode.using_time[stepid])-\
                                        timestr_to_timestamp(commnode.response_endtime[stepid]))
        if node_waittime==[]:
            continue        
        waittime.append(np.array(node_waittime))
    waittime_mean = []
    waittime_conf_interval = []
    for waittime_value in waittime:
        n = waittime_value.size
        waittime_mean.append(np.mean(waittime_value))
        dof = n - 1         # degrees of freedom
        alpha = 1.0 - 0.95
        waittime_std = np.std(waittime_value)
        conf_interval = t.ppf(1-alpha/2., dof) * waittime_std*np.sqrt(1.+1./n)
        waittime_conf_interval.append(conf_interval)
    plt.errorbar(range(len(waittime_mean)),waittime_mean, yerr=waittime_conf_interval, fmt='o',ecolor='r',color='b',elinewidth=1,capsize=5,markersize=3)
    #plt.plot(range(len(waittime_mean)),waittime_mean)
    plt.grid()
    plt.show()

def Batchsize_vs_JCT_CCT(comm_node_mgr_dict):
    batchsize = list(comm_node_mgr_dict.keys())
    batchsize = [int(i) for i in batchsize]
    batchsize.sort()
    batchsize = [str(i) for i in batchsize]    
    JCT_CCT = []
    CCT = []
    for bs in batchsize:
        step_JCT_CCT = []
        step_CCT = []
        comm_node_mgr = comm_node_mgr_dict[bs]
        for stepid in comm_node_mgr.commnode_list[0].response_endtime.keys(): 
            max_FCT = -1.
            max_using = -1.
            for commnode in comm_node_mgr.commnode_list:
                if "worker" in commnode.recvmachine and stepid in commnode.response_endtime.keys()\
                   and stepid in commnode.using_time.keys() and commnode.get_datasize()*4>=10:
                   if max_FCT<timestr_to_timestamp(commnode.response_endtime[stepid]):
                       max_FCT = timestr_to_timestamp(commnode.response_endtime[stepid])
                   if max_using<timestr_to_timestamp(commnode.using_time[stepid]):
                       max_using = timestr_to_timestamp(commnode.using_time[stepid])         
            if max_FCT>0. and max_using>0. and max_using-max_FCT < 100:  
                step_JCT_CCT.append(max_using-max_FCT)
                step_CCT.append(max_FCT)
        if step_JCT_CCT!=[]:
            JCT_CCT.append(np.array(step_JCT_CCT))
            CCT.append(np.array(step_CCT))
    JCT_CCT_mean = []
    JCT_CCT_max = []
    JCT_CCT_min = []
    JCT_CCT_median = []
    JCT_CCT_conf_interval = []

    CCT_mean = []
    CCT_max = []
    CCT_min = []
    list_len = len(JCT_CCT)
    for i in range(list_len):
        batch_jct_cct = JCT_CCT[i]
        batch_cct = CCT[i]
        n = batch_jct_cct.size
        JCT_CCT_mean.append(np.mean(batch_jct_cct))
        JCT_CCT_median.append(np.median(batch_jct_cct))
        JCT_CCT_min.append(batch_jct_cct.min())
        JCT_CCT_max.append(batch_jct_cct.max())
        CCT_mean.append(np.mean(batch_cct))
        CCT_min.append(batch_cct.min())
        CCT_max.append(batch_cct.max())
        dof = n - 1         # degrees of freedom
        alpha = 1.0 - 0.95
        JCT_CCT_std = np.std(batch_jct_cct)    
            
        conf_interval = t.ppf(1-alpha/2., dof) * JCT_CCT_std*np.sqrt(1.+1./n)
        JCT_CCT_conf_interval.append(conf_interval)
    
    plt.errorbar(batchsize,JCT_CCT_median, yerr=[JCT_CCT_min,JCT_CCT_max], fmt='o',ecolor='b',color='b',elinewidth=1,capsize=5,markersize=5)      
    plt.plot(batchsize,JCT_CCT_mean,marker='o',color='r')
    #plt.errorbar(batchsize,CCT_mean, yerr=[CCT_min,CCT_max], fmt='o',ecolor='b',color='b',elinewidth=1,capsize=5,markersize=5)      
    #plt.plot(batchsize,CCT_mean,marker='o',color='r')    
    plt.xlabel("Batch Size")
    plt.ylabel("JCT-CCT")
    plt.grid()
    plt.show()     

def JCT_vs_CCT(comm_node_mgr, log_record_mgr):
    step_JCT = []
    step_CCT = []
    step_JCT_CCT = []
    stepid_list = list(comm_node_mgr.commnode_list[0].response_endtime.keys())
    for stepid in stepid_list:
        step_start_time = log_record_mgr.get_step_starttime_by_stepid(stepid)
        if step_start_time==False:
            continue
        step_start_time = timestr_to_timestamp(step_start_time)
        max_respend = -1.0
        max_using = -1.0
        for commnode in comm_node_mgr.commnode_list:
            if "worker" in commnode.recvmachine and stepid in commnode.response_endtime.keys() and\
               stepid in commnode.using_time.keys() and commnode.get_datasize()*4>=10:
                if timestr_to_timestamp(commnode.response_endtime[stepid])>max_respend:
                    max_respend = timestr_to_timestamp(commnode.response_endtime[stepid])
                if timestr_to_timestamp(commnode.using_time[stepid])>max_using:
                    max_using = timestr_to_timestamp(commnode.using_time[stepid])
        if max_respend>0.0 and max_using>0.0:
            step_CCT.append(max_respend-step_start_time)
            step_JCT.append(max_using-step_start_time)
            step_JCT_CCT.append(max_using-max_respend)
    max_time = max(step_JCT)
    #plt.plot(range(len(step_CCT)), np.array(step_JCT)-np.array(step_CCT))
    #plt.plot(range(len(step_CCT)), step_CCT)
    #plt.plot(range(len(step_JCT)), step_JCT)
    plt.scatter(np.array(step_CCT)/max_time, np.array(step_JCT)/max_time)
    #plt.plot([0,10],[0,10])
    plt.show()

def JCT_vs_Waittime(comm_node_mgr, log_record_mgr):
    step_JCT = []
    step_average_waittime = []
    stepid_list = list(comm_node_mgr.commnode_list[0].response_endtime.keys())
    for stepid in stepid_list:
        step_start_time = log_record_mgr.get_step_starttime_by_stepid(stepid)
        if step_start_time==False:
            continue
        step_start_time = timestr_to_timestamp(step_start_time)
        max_using = -1.0 
        average_waittime = 0.0    
        nodenum = 0   
        for commnode in comm_node_mgr.commnode_list:
            if "worker" in commnode.recvmachine and stepid in commnode.response_endtime.keys() and\
               stepid in commnode.using_time.keys() and commnode.get_datasize()*4>=10:
                if timestr_to_timestamp(commnode.using_time[stepid])>max_using:
                    max_using = timestr_to_timestamp(commnode.using_time[stepid])
                if timestr_to_timestamp(commnode.using_time[stepid])-timestr_to_timestamp(commnode.response_endtime[stepid])>0:
                    average_waittime += timestr_to_timestamp(commnode.using_time[stepid])-timestr_to_timestamp(commnode.response_endtime[stepid])
                    nodenum += 1
        if nodenum>0 and max_using>0.0:
            step_JCT.append(max_using-step_start_time)
            step_average_waittime.append(average_waittime/nodenum)
    plt.scatter(step_average_waittime, step_JCT)
    plt.show()

def JCT_vs_Overlap(comm_node_mgr, log_record_mgr):
    step_JCT = []
    step_overlap = []
    stepid_list = list(comm_node_mgr.commnode_list[0].response_endtime.keys())
    for stepid in stepid_list:
        step_start_time = log_record_mgr.get_step_starttime_by_stepid(stepid)
        if step_start_time==False:
            continue
        step_start_time = timestr_to_timestamp(step_start_time)
        max_using = -1.0 
        min_using = -1.0
        max_respend = -1.0
        min_request = -1.0
        for commnode in comm_node_mgr.commnode_list:
            if "worker" in commnode.recvmachine and stepid in commnode.response_endtime.keys() and\
               stepid in commnode.using_time.keys() and stepid in commnode.request_time.keys() and\
               commnode.get_datasize()*4>=1:
                if timestr_to_timestamp(commnode.response_endtime[stepid])>max_respend:
                    max_respend = timestr_to_timestamp(commnode.response_endtime[stepid])
                if timestr_to_timestamp(commnode.using_time[stepid])>max_using:
                    max_using = timestr_to_timestamp(commnode.using_time[stepid])
                if min_using<0 or timestr_to_timestamp(commnode.using_time[stepid])<min_using:
                    min_using = timestr_to_timestamp(commnode.using_time[stepid])
                if min_request<0 or timestr_to_timestamp(commnode.request_time[stepid])<min_request:
                    min_request = timestr_to_timestamp(commnode.request_time[stepid])
        if max_respend>0.0 and max_using>0.0 and min_using>0.0 and min_request>0.0 and\
           (max_respend-min_using)/(max_using-min_request)<1.0:
            step_JCT.append(max_using-step_start_time) 
            step_overlap.append((max_respend-min_using)/(max_using-min_request))
    plt.scatter(step_overlap, step_JCT)
    plt.show()    

def Disorder_Degree(comm_node_mgr):
    def plot_confusion_matrix(cm):
        cm = np.array(cm)
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]  
        plt.imshow(cm, interpolation='nearest')   
        plt.colorbar()   
    workernode = []
    for commnode in comm_node_mgr.commnode_list:
        if "worker" in commnode.recvmachine:
            workernode.append(commnode)
    nodenum = len(workernode)
    map = []
    for i in range(nodenum):
        temp = []
        for j in range(nodenum):
            temp.append(0)
        map.append(temp)
    stepids = comm_node_mgr.commnode_list[0].response_endtime.keys()
    for stepid in stepids:
        respts = []
        for node in workernode:
            if stepid not in node.response_endtime.keys():
                break
            respts.append(timestr_to_timestamp(node.response_endtime[stepid]))
        if len(respts)<nodenum:
            continue
        sorted_respts = sorted(respts)
        for x in range(nodenum):
            for y in range(nodenum):
                if respts[x] == sorted_respts[y]:
                    map[x][y] += 1
    plot_confusion_matrix(map)
    plt.show()

def order_respstart_respend():
    pass

def bandwidth_distr(comm_node_mgr):
    average_bw = []
    min_bw = []
    max_bw = []
    for commnode in comm_node_mgr.commnode_list:
        if "worker" in commnode.recvmachine:
            step_bw = []
            stepids = commnode.response_endtime.keys()
            for stepid in stepids:
                if stepid in commnode.response_starttime.keys() and stepid in commnode.response_endtime.keys():
                    latency = timestr_to_timestamp(commnode.response_endtime[stepid]) - \
                                timestr_to_timestamp(commnode.response_starttime[stepid])
                    if latency>0.0:
                        step_bw.append(commnode.get_datasize()*4/10000000/latency)
            if len(step_bw)>0:
                min_bw.append(min(step_bw))
                max_bw.append(max(step_bw))
                average_bw.append(sum(step_bw)/len(step_bw))
    plt.bar(range(len(average_bw)),average_bw)
    print(sum(average_bw))
    plt.errorbar(range(len(average_bw)),average_bw, yerr=[min_bw,max_bw], fmt='o',ecolor='r',color='b',elinewidth=1,capsize=5,markersize=3)
    plt.show()

def random_degree(comm_node_mgr):
    def plot_confusion_matrix(cm):
        x = len(cm)
        y = len(cm[0])
        cm = np.array(cm).reshape(y,x)
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]  
        plt.imshow(cm, interpolation='nearest')   
        plt.colorbar()  
    workernode = []
    for commnode in comm_node_mgr.commnode_list:
        if "worker" in commnode.recvmachine:
            workernode.append(commnode)  
    nodenum = len(workernode)
    orders = []
    stepids = comm_node_mgr.commnode_list[0].response_endtime.keys()
    for stepid in stepids:
        step_resp = []
        step_order = []
        for node in workernode:
            if stepid not in node.response_endtime.keys():
                break
            step_resp.append(timestr_to_timestamp(node.response_endtime[stepid])) 
        if len(step_resp)<nodenum:
            continue
        sorted_resp = sorted(step_resp)
        for resp in step_resp:
            step_order.append(sorted_resp.index(resp))
        orders.append(step_order)
        #if len(orders)>180:
        #    break
    plot_confusion_matrix(orders)
    plt.show()    

def JCT_CCT_vs_Step(comm_node_mgr, log_record_mgr):
    JCT = []
    CCT = []
    Step_Count = []
    stepids = comm_node_mgr.commnode_list[0].response_endtime.keys()
    for stepid in stepids:
        step_start_time = log_record_mgr.get_step_starttime_by_stepid(stepid)
        if step_start_time==False:
            continue
        step_start_time = timestr_to_timestamp(step_start_time)
        max_respend = -1.0
        for commnode in comm_node_mgr.commnode_list:
            if "worker" in commnode.recvmachine and stepid in commnode.response_endtime.keys() and\
               stepid in commnode.using_time.keys() and commnode.get_datasize()*4>=10:
                if timestr_to_timestamp(commnode.response_endtime[stepid])>max_respend:
                    max_respend = timestr_to_timestamp(commnode.response_endtime[stepid])                           
        jct, count = log_record_mgr.get_runtime_by_stepid(stepid)
        if jct!=False and count!=-1 and max_respend>0.0 and jct>0.0:
            JCT.append(jct)
            CCT.append(max_respend-step_start_time) 
            Step_Count.append(count)
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot(Step_Count, JCT)
    ax2.plot(Step_Count, CCT)
    plt.show()
    
    



if __name__ == '__main__':
    model_list = ["Lenet", "AlexNet", "LSTM", "Siamese", "VGG16", "Inception", "ResNet152"]
    batchsize = ["1", "5", "10", "20", "40", "80", "120"]
    comm_node_mgr_dict = {}
    stepinfo_mgr_dict = {}
    model_index = 5
    batch_index = 3
    
    #commnode_savepath = "./tensorflow_results/"+model_list[model_index]+"Log/pre/"+model_list[model_index].lower()+"-"+batchsize[batch_index]+"-commnode.pkl"
    #logrecord_savepath = "./tensorflow_results/"+model_list[model_index]+"Log/pre/"+model_list[model_index].lower()+"-"+batchsize[batch_index]+"-logrecords.pkl"
    commnode_savepath = "./tensorflow_results_2/"+model_list[model_index]+"/"+model_list[model_index].lower()+"-1_1-128-commnode.pkl"
    logrecord_savepath = "./tensorflow_results_2/"+model_list[model_index]+"/"+model_list[model_index].lower()+"-1_1-128-logrecords.pkl"
    comm_node_mgr = CommNodeMgr()
    comm_node_mgr.recover_commnodes(commnode_savepath)
    log_record_mgr = LogRecordMgr()
    log_record_mgr.recover_logrecords(logrecord_savepath)
    #random_degree(comm_node_mgr)
    JCT_CCT_vs_Step(comm_node_mgr, log_record_mgr)
    #Disorder_Degree(comm_node_mgr)
    #bandwidth_distr(comm_node_mgr)
    #JCT_vs_CCT(comm_node_mgr, log_record_mgr)
    #JCT_vs_Waittime(comm_node_mgr, log_record_mgr)
    #JCT_vs_Overlap(comm_node_mgr, log_record_mgr)
    
    '''
    for model in model_list:
        if model=="LSTM":
            commnode_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+batchsize[3]+"-commnode.pkl"
        else:
            commnode_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+batchsize[6]+"-commnode.pkl"
        comm_node_mgr = CommNodeMgr()
        comm_node_mgr.recover_commnodes(commnode_savepath)
        comm_node_mgr_dict[model] = comm_node_mgr
    #comm_size_distri(comm_node_mgr_dict)
    #comm_size_CDF(comm_node_mgr_dict)
    #latency_size(comm_node_mgr_dict)
    '''
    '''
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
    '''
    model_index = 4
    batch_index = 6
    commnode_savepath = "./tensorflow_results/"+model_list[model_index]+"Log/pre/"+model_list[model_index].lower()+"-"+batchsize[batch_index]+"-commnode.pkl"
    logrecord_savepath = "./tensorflow_results/"+model_list[model_index]+"Log/pre/"+model_list[model_index].lower()+"-"+batchsize[batch_index]+"-logrecords.pkl"
    comm_node_mgr = CommNodeMgr()
    comm_node_mgr.recover_commnodes(commnode_savepath)
    log_record_mgr = LogRecordMgr()
    log_record_mgr.recover_logrecords(logrecord_savepath)
    runtime_analysis(comm_node_mgr, log_record_mgr, model_list[model_index])
    '''
    '''
    model_index = 1
    batch_index = 6
    commnode_savepath = "./tensorflow_results/"+model_list[model_index]+"Log/pre/"+model_list[model_index].lower()+"-"+batchsize[batch_index]+"-commnode.pkl" 
    comm_node_mgr = CommNodeMgr()
    comm_node_mgr.recover_commnodes(commnode_savepath)
    #latency_vs_parasize(comm_node_mgr)
    #latency_vs_layerindex(comm_node_mgr)
    waittime_vs_layerindex(comm_node_mgr)
    '''
    '''
    model_index = 5
    #batchsize = ["1","10","20"]
    for bs in batchsize:
        commnode_savepath = "./tensorflow_results/"+model_list[model_index]+"Log/pre/"+model_list[model_index].lower()+"-"+bs+"-commnode.pkl"   
        comm_node_mgr = CommNodeMgr()
        comm_node_mgr.recover_commnodes(commnode_savepath)    
        comm_node_mgr_dict[bs] = comm_node_mgr
    Batchsize_vs_JCT_CCT(comm_node_mgr_dict)
    '''
    
