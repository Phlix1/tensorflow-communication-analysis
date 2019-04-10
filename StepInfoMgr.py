from StepInfo import StepInfo
class StepInforMgr:
    def __init__(self):
        self.stepinfo_list = []
    def add_from_commnode_logrecord(self, comm_node_mgr, log_record_mgr):
        stepid_list = comm_node_mgr.get_stepids()
        for stepid in stepid_list:
            commtime, machine_commtime = comm_node_mgr.get_commtime_by_stepid(stepid)
            runtime = log_record_mgr.get_runtime_by_stepid(stepid)
            if commtime==False or runtime==False:
                continue
            step_info = StepInfo(stepid, runtime, commtime, machine_commtime)
            self.stepinfo_list.append(step_info)
    def show_steps(self):
        for stepinfo in self.stepinfo_list:
            stepinfo.stepinfo_print()
            