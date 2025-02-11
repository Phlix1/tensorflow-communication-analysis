from StepInfo import StepInfo
from utils import *
import pickle
class StepInforMgr:
    def __init__(self):
        self.stepinfo_list = []
    def add_from_commnode_logrecord(self, comm_node_mgr, log_record_mgr):
        execution_count = 1
        start_time = {}
        while True:
            stepids = []
            min_ts = -1.0
            for logrecord in log_record_mgr.runpart_log_records:
                if logrecord.execution_count==str(execution_count) and self.check_stepid(comm_node_mgr, logrecord.stepid):
                    stepids.append(logrecord.stepid)
                    if min_ts<0.0 or min_ts>timestr_to_timestamp(logrecord.timestr):
                        min_ts = timestr_to_timestamp(logrecord.timestr)
            start_time[execution_count] = min_ts
            if stepids==[]:
                break
            stepinfo = StepInfo(stepids, min_ts, execution_count)
            self.stepinfo_list.append(stepinfo)
            execution_count += 1
        self.stepinfo_list = self.stepinfo_list[0:-1]
        for stepinfo in self.stepinfo_list:
            stepinfo.JCT = start_time[stepinfo.execution_count+1]-start_time[stepinfo.execution_count]
            max_comm_ts=-1.0
            for commnode in comm_node_mgr.commnode_list:
                if "worker" in commnode.recvmachine and commnode.get_datasize()*4>=10:
                    for stepid in stepinfo.stepids:
                        if stepid in commnode.response_endtime.keys():
                            if timestr_to_timestamp(commnode.response_endtime[stepid])>max_comm_ts:
                                max_comm_ts = timestr_to_timestamp(commnode.response_endtime[stepid])
            if max_comm_ts>0.0:
                stepinfo.CCT = max_comm_ts - stepinfo.start_ts
    
    def check_stepid(self, comm_node_mgr, stepid):
        for commnode in comm_node_mgr.commnode_list:
            if stepid in commnode.response_endtime.keys():
                return True
        return False

    def show_steps(self):
        for stepinfo in self.stepinfo_list:
            stepinfo.stepinfo_print()

    def save_stepinfos(self, save_path):
        save_list = []
        for stepinfo in self.stepinfo_list:
            save_list.append(stepinfo.serialize_stepinfo())
        with open(save_path,'wb') as f:
            pickle.dump(save_list, f, -1)

    def recover_stepinfos(self, save_path):
        with open(save_path,'rb') as f:
            save_list = pickle.load(f)
        for si in save_list:
            stepinfo = StepInfo()
            stepinfo.deserialize_stepinfo(si)
            self.stepinfo_list.append(stepinfo)
            