class StepInfo:
    def __init__(self, stepid, execution_count, runtime, commtime, machine_commtime):
        self.stepid=stepid
        self.execution_count = execution_count
        self.runtime = runtime
        # NOTE: this commtime is only useful when we only analyse the logrecords of 1PS+1Worker
        self.commtime = commtime 
        self.machine_commtime = machine_commtime
    def stepinfo_print(self):
        print("--------------------------")
        print("Step ID: ", self.stepid)
        print("Execution Count: ", self.execution_count)
        print("Worker Run Time of Step: ", self.runtime)
        print("Communication Time: ", self.commtime)
        print("Machine Comm Time: ", self.machine_commtime)
        print("--------------------------")