from cpu_extract_info import *
import os

if __name__ == '__main__':
    logpath_prefix = "./sync_results/Lenet/lenetsync-1_2-128"
    logpath_suffix = ".txt"
    commnode_savepath = logpath_prefix + "-commnode.pkl"
    logrecord_savepath = logpath_prefix + "-logrecords.pkl"     
    worker_logpath_list = []
    ps_logpath_list = []
    i = 0
    while True:
        worker_logpath = logpath_prefix+"-logfile-worker"+str(i)+logpath_suffix
        if os.path.exists(worker_logpath):
            worker_logpath_list.append(worker_logpath)
            i += 1
        else:
            break
    i = 0
    while True:
        ps_logpath = logpath_prefix+"-logfile-ps"+str(i)+logpath_suffix
        if os.path.exists(ps_logpath):
            ps_logpath_list.append(ps_logpath)
            i += 1
        else:
            break
    comm_node_mgr = CommNodeMgr()
    log_record_mgr = LogRecordMgr()
    graph_def_list = []
    for worker_logpath in worker_logpath_list:
        graph_def = worker_logfile_processing(worker_logpath, log_record_mgr)  
        comm_node_mgr.add_from_graph(graph_def)
    print("Graph OK!")
    comm_node_mgr.commnode_print()
    for ps_logpath in ps_logpath_list:
        ps_logfile_processing(ps_logpath, log_record_mgr) 
    print("Logfile OK!")
    comm_node_mgr.add_from_logrecord(log_record_mgr)
    comm_node_mgr.save_commnodes(commnode_savepath)
    log_record_mgr.save_logrecords(logrecord_savepath)
   