class StepInfo:
    def __init__(self, stepids=[], start_ts='', execution_count=-1):
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
    def serialize_stepinfo(self):
        return [self.stepids, self.start_ts, self.execution_count, self.JCT, self.CCT]
    def deserialize_stepinfo(self, serial_result):
        self.stepids = serial_result[0]
        self.start_ts = serial_result[1]
        self.execution_count = serial_result[2]
        self.JCT = serial_result[3]
        self.CCT = serial_result[4]