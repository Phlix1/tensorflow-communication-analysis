from StepInfo import StepInfo
class StepInforMgr:
    def __init__(self):
        self.stepinfo_list = []
    def add_from_commnode_logrecord(self, comm_node_mgr, log_record_mgr):
        stepid_list = comm_node_mgr.get_stepids()
        for stepid in stepid_list:
            commtime, machine_commtime = comm_node_mgr.get_commtime_by_stepid(stepid)
            runtime, execution_count = log_record_mgr.get_runtime_by_stepid(stepid)
            if commtime==False or runtime==False:
                continue
            step_info = StepInfo(stepid, execution_count, runtime, commtime, machine_commtime)
            self.stepinfo_list.append(step_info)
    def get_comm_comp_ratio(self):
        average_ratio = 0.0
        stepnum = 0
        for stepinfo in self.stepinfo_list:
            for key in stepinfo.machine_commtime.keys():
                if "worker" in key and stepinfo.machine_commtime[key]/stepinfo.runtime<1.0:
                    average_ratio += stepinfo.machine_commtime[key]/stepinfo.runtime
                    stepnum += 1
        average_ratio /= stepnum
        return average_ratio
            

    def show_steps(self):
        for stepinfo in self.stepinfo_list:
            stepinfo.stepinfo_print()
            