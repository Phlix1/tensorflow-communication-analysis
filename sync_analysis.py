from LogRecordMgr import LogRecordMgr
from CommNodeMgr import CommNodeMgr
from StepInfoMgr import StepInforMgr
from utils import *
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import t
import math
import sys

def plot_confusion_matrix(cm):
    x = len(cm)
    y = len(cm[0])
    cm = np.array(cm).reshape(y,x)
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]  
    plt.imshow(cm, interpolation='nearest')   
    plt.colorbar()  

def resp_order(comm_node_mgr, stepinfo_mgr):
    orders = []
    for stepinfo in stepinfo_mgr.stepinfo_list:
        step_order = []
        tensor_list = []
        tensor_resp_ts = {}
        stepids = stepinfo.stepids
        for commnode in comm_node_mgr.commnode_list:
            if "worker" not in commnode.recvmachine or commnode.get_datasize()*4<10:
                continue
            for stepid in stepids:
                if stepid in commnode.response_endtime.keys():
                    tensorname = commnode.tensorname
                    if tensorname in tensor_resp_ts.keys():
                        if timestr_to_timestamp(commnode.response_endtime[stepid])>tensor_resp_ts[tensorname]:
                            tensor_resp_ts[tensorname] = timestr_to_timestamp(commnode.response_endtime[stepid])
                    else:
                        tensor_list.append(tensorname)
                        tensor_resp_ts[tensorname] = timestr_to_timestamp(commnode.response_endtime[stepid])
        tensor_resp_temp = []
        for tensor in tensor_list:
            tensor_resp_temp.append(tensor_resp_ts[tensor])
        sorted_resp = sorted(tensor_resp_temp)
        for resp in tensor_resp_temp:
            step_order.append(sorted_resp.index(resp))
        orders.append(step_order)
    plot_confusion_matrix(orders)
    plt.show()

def JCT_vs_CCT(stepinfo_mgr):
    JCT = []
    CCT = []
    for stepinfo in stepinfo_mgr.stepinfo_list:
        JCT.append(stepinfo.JCT)
        CCT.append(stepinfo.CCT)
    plt.scatter(CCT, JCT)
    plt.show()

if __name__ == '__main__':
    root_dir = sys.argv[1]
    model_name = sys.argv[2]
    sync_stat = sys.argv[3]
    ps_num = sys.argv[4]
    worker_num = sys.argv[5]
    batchsize = sys.argv[6]
    if sync_stat != "sync":
        sync_stat = ""
    logpath_prefix = root_dir+"/"+model_name+"/"+model_name.lower()+sync_stat+"-"+ps_num+"_"+worker_num+"-"+batchsize
    commnode_savepath = logpath_prefix + "-commnode.pkl"
    logrecord_savepath = logpath_prefix + "-logrecords.pkl"  
    stepinfos_savepath = logpath_prefix + "-stepinfos.pkl"
    #comm_node_mgr = CommNodeMgr()
    #comm_node_mgr.recover_commnodes(commnode_savepath)
    #log_record_mgr = LogRecordMgr()
    #log_record_mgr.recover_logrecords(logrecord_savepath) 
    stepinfo_mgr = StepInforMgr()
    #stepinfo_mgr.add_from_commnode_logrecord(comm_node_mgr, log_record_mgr)
    stepinfo_mgr.recover_stepinfos(stepinfos_savepath)
    stepinfo_mgr.show_steps() 
    #resp_order(comm_node_mgr, stepinfo_mgr)
    #JCT_vs_CCT(stepinfo_mgr)