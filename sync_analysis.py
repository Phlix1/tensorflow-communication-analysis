from LogRecordMgr import LogRecordMgr
from CommNodeMgr import CommNodeMgr
from StepInfoMgr import StepInforMgr
from utils import *
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import t
import math

if __name__ == '__main__':
    logpath_prefix = "./sync_results/Lenet/lenetsync-1_2-128"
    commnode_savepath = logpath_prefix + "-commnode.pkl"
    logrecord_savepath = logpath_prefix + "-logrecords.pkl"  
    comm_node_mgr = CommNodeMgr()
    comm_node_mgr.recover_commnodes(commnode_savepath)
    log_record_mgr = LogRecordMgr()
    log_record_mgr.recover_logrecords(logrecord_savepath) 
    stepinfo_mgr = StepInforMgr()
    stepinfo_mgr.add_from_commnode_logrecord(comm_node_mgr, log_record_mgr)
    stepinfo_mgr.show_steps()  