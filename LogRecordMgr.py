import Constants
class LogRecordMgr:
    def __init__(self):
        runpart_log_records = []
        process_log_records = []
        syncdone_log_records = []
        asyncdone_log_records = []
        request_log_records = []
        donecall_log_records = []
    def insert_log_record(self, log_record, log_type):
        if log_type==Constants.RUNPARTITION_RECORD:
            self.runpart_log_records.append(log_record)
        if log_type==Constants.PROCESS_RECORD:
            self.process_log_records.append(log_record)
        if log_type==Constants.SYNCDONE_RECORD:
            self.syncdone_log_records.append(log_record)
        if log_type==Constants.ASYNCDONE_RECORD:
            self.asyncdone_log_records.append(log_record)
        if log_type==Constants.REQUEST_RECORD:
            self.request_log_records.append(log_record)
        if log_type==Constants.DONECALLBACK_RECORD:
            self.donecall_log_records.append(log_record) 
    def parse_log_message(self, raw_message):
        # case 1 RunPartitions: 
        
        # case 2 Process node:
        # case 3 Synchronous kernel done: 
        # case 4 Async kernel done: 
        # case 5 RecvTensorAsync req: step_id:(request)
        # case 6 Done call back
        pass

