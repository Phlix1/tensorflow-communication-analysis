class StepInfo:
    def __init__(self, stepids, start_ts, execution_count):
        self.stepids=stepids
        self.start_ts = start_ts
        self.execution_count = execution_count
        self.JCT = 0.0
        self.CCT = 0.0
    def stepinfo_print(self):
        print("--------------------------")
        print("Execution Count: ", self.execution_count)
        print("Step IDs: ", self.stepids) 
        print("Step JCT: ", self.JCT)    
        print("Step CCT: ", self.CCT)           
        print("--------------------------")