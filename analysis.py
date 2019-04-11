from LogRecordMgr import LogRecordMgr
from CommNodeMgr import CommNodeMgr
if __name__ == '__main__':
    commnode_savepath = "./tensorflow_results/LenetLog/pre/lenet-1-commnode.pkl"
    logrecord_savepath = "./tensorflow_results/LenetLog/pre/lenet-1-logrecords.pkl"
    comm_node_mgr = CommNodeMgr()
    log_record_mgr = LogRecordMgr()
    comm_node_mgr.recover_commnodes(commnode_savepath)
    log_record_mgr.recover_logrecords(logrecord_savepath)
    comm_node_mgr.commnode_print()
    #log_record_mgr.logs_print()