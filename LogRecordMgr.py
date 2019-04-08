import Constants
import re
from LogRecord import *
class LogRecordMgr:
    def __init__(self):
        self.runpart_log_records = []
        self.process_log_records = []
        self.syncdone_log_records = []
        self.asyncdone_log_records = []
        self.request_log_records = []
        self.donecall_log_records = []
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
        # case 0 RunPartitions: 
        find_runpart = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] RunPartitions '\
                                +'step_id (\d*) execution_count (\d*)', raw_message)
        if find_runpart!=None:
            timestr = find_runpart.group(1)
            logtype = Constants.RUNPARTITION_RECORD
            stepid = find_runpart.group(2)
            execution_count = find_runpart.group(3)
            runpart_log = RunPartitionLogRecord(raw_message, timestr, logtype, stepid, execution_count)
            self.insert_log_record(runpart_log, logtype)
            return True
        # case 1-0 Process send node:
        find_process = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] Process node: '\
                                +'\d* step (\d*) {{node (.*)}} = _Send.*, recv_device="(.*)", '\
                                +'send_device="(.*)", .* tensor_name="(.*)", .*device: (.*)', raw_message)
        if find_process!=None:
            timestr = find_process.group(1)
            logtype = Constants.PROCESS_RECORD
            stepid = find_process.group(2)
            nodename = find_process.group(3)
            nodetype = Constants.SEND_NODE
            recv_device = find_process.group(4)
            send_device = find_process.group(5)            
            tensor_name = find_process.group(6)
            device = find_process.group(7)
            process_log = ProcessNodeLogRecord(raw_message, timestr, logtype, stepid, nodename,\
                            nodetype, device, send_device, recv_device, tensor_name)
            self.insert_log_record(process_log, logtype)  
            return True          
        # case 1-1 Process recv node:
        find_process = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] Process node: '\
                                +'\d* step (\d*) {{node (.*)}} = _Recv.*, recv_device="(.*)", '\
                                +'send_device="(.*)", .* tensor_name="(.*)", .*device: (.*)', raw_message)
        if find_process!=None:
            timestr = find_process.group(1)
            logtype = Constants.PROCESS_RECORD
            stepid = find_process.group(2)
            nodename = find_process.group(3)
            nodetype = Constants.RECV_NODE
            recv_device = find_process.group(4)
            send_device = find_process.group(5)            
            tensor_name = find_process.group(6)
            device = find_process.group(7)
            process_log = ProcessNodeLogRecord(raw_message, timestr, logtype, stepid, nodename,\
                            nodetype, device, send_device, recv_device, tensor_name)
            self.insert_log_record(process_log, logtype)  
            return True
        # case 1-2 Process common node:
        find_process = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] Process node: '\
                                +'\d* step (\d*) {{node (.*)}}.* device: (.*)', raw_message)
        if find_process!=None:
            timestr = find_process.group(1)
            logtype = Constants.PROCESS_RECORD
            stepid = find_process.group(2)
            nodename = find_process.group(3)
            nodetype = Constants.COMM_NODE 
            device = find_process.group(4)
            process_log = ProcessNodeLogRecord(raw_message, timestr, logtype, stepid, nodename,\
                            nodetype, device)  
            self.insert_log_record(process_log, logtype) 
            return True                     
        # case 2 Synchronous kernel done: 
        find_syncdone = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] Synchronous kernel '\
                                +'done: \d* step (\d*) {{node (.*)}}', raw_message)
        if find_syncdone!=None:
            timestr = find_syncdone.group(1)
            logtype = Constants.SYNCDONE_RECORD
            stepid = find_syncdone.group(2)
            nodename = find_syncdone.group(3)
            syncdone_log = SyncDoneLogRecord(raw_message, timestr, logtype, stepid, nodename)
            self.insert_log_record(syncdone_log, logtype)
            return True
        # case 3 Async kernel done: 
        find_asyncdone = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] Async kernel '\
                                +'done: \d* step (\d*) {{node (.*)}}', raw_message)
        if find_asyncdone!=None:
            timestr = find_asyncdone.group(1)
            logtype = Constants.ASYNCDONE_RECORD
            stepid = find_asyncdone.group(2)
            nodename = find_asyncdone.group(3)
            asyncdone_log = AsyncDoneLogRecord(raw_message, timestr, logtype, stepid, nodename)
            self.insert_log_record(asyncdone_log, logtype)
            return True       
        # case 4 RecvTensorAsync req: step_id:(request)
        find_request = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] RecvTensorAsync '\
                                +'req: step_id: (\d*) rendezvous_key: "(.*)" request_id: (.*)  '\
                                , raw_message)
        if find_request!=None:
            timestr = find_request.group(1)
            logtype = Constants.REQUEST_RECORD
            stepid = find_request.group(2)
            rendezvous_key = find_request.group(3)
            request_id = find_request.group(4)
            request_log = RequestLogRecord(raw_message, timestr, logtype, stepid, \
                            rendezvous_key, request_id)
            self.insert_log_record(request_log, logtype)
            return True
        # case 5 Done call back
        find_callback = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*] done callback, '\
                                +'req: step_id: (\d*) rendezvous_key: "(.*)" request_id: (.*)  '\
                                +'response (.*)send_start_micros: (\d*) ', raw_message)
        if find_callback!=None:
            timestr = find_callback.group(1)
            logtype = Constants.DONECALLBACK_RECORD
            stepid = find_callback.group(2)
            rendezvous_key = find_callback.group(3)
            request_id = find_callback.group(4)
            resp_start_ts = find_callback.group(6)
            tensor_shape = []
            shape_str = find_callback.group(5)
            shape_info =  re.findall(r'size: (\d*)  ', shape_str)
            dimnum = len(shape_info)
            if dimnum == 0:
                tensor_shape.append(1)
            else:
                for x in shape_info:
                    tensor_shape.append(int(x))
            donecallback_log = DoneCallbackLogRecord(raw_message, timestr, logtype, stepid, rendezvous_key, request_id,\
                                    resp_start_ts, tensor_shape)
            self.insert_log_record(donecallback_log, logtype)
            return True
    def get_shape_by_tensorname(self, tensorname):
        for log_record in self.donecall_log_records:
            if tensorname==log_record.tensor_name:
                return log_record.tensor_shape
    def get_sendtimes_by_sendnode(self, sendnode, send_time):
        for log_record in self.syncdone_log_records:
            if log_record.nodename == sendnode:
                stepid = log_record.stepid
                send_time[stepid] = log_record.timestr
    def get_req_resp_start_times_by_rendezvouskey(self, sendmachine, recvmachine, \
                                                tensorname, request_time, response_starttime):
        for log_record in self.request_log_records:
            rendezvous_key = log_record.rendezvous_key
            if recvmachine in rendezvous_key and sendmachine in rendezvous_key \
                and tensorname in rendezvous_key:
                stepid = log_record.stepid
                requestid = log_record.request_id
                request_time[stepid] = log_record.timestr
                self.get_response_starttimes_by_requestid(requestid, response_starttime)
        
    def get_response_starttimes_by_requestid(self, requestid, response_starttime):
        for log_record in self.donecall_log_records:
            if requestid==log_record.request_id:
                stepid = log_record.stepid
                resp_start_ts = log_record.resp_start_ts
                resp_start_str = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(resp_start_ts[0:10])))
                resp_start_str += '.'+resp_start_ts[10:]
                response_starttime[stepid] = resp_start_str
                break
    
    def get_using_time_by_consumers(self, consumers, using_time):
        for log_record in self.process_log_records:
            stepid = log_record.stepid
            for consumer in consumers:
                if log_record.nodename == consumer:
                    if stepid not in using_time.keys():
                        using_time[stepid] = log_record.timestr
                    else:
                        curtime = log_record.timestr_to_timestamp(using_time[stepid])
                        if curtime>log_record.timestr_to_timestamp(log_record.timestr):
                            using_time[stepid] = log_record.timestr


    def get_response_endtimes_by_recvnode(self, recvnode, response_endtime):
        for log_record in self.asyncdone_log_records:
            if log_record.nodename == recvnode:
                stepid = log_record.stepid
                response_endtime[stepid] = log_record.timestr
    def logs_print(self):
        for log in self.runpart_log_records:
            log.log_print()
        for log in self.process_log_records:
            log.log_print()
        for log in self.syncdone_log_records:
            log.log_print()
        for log in self.asyncdone_log_records:
            log.log_print()
        for log in self.request_log_records:
            log.log_print()
        for log in self.donecall_log_records:
            log.log_print()
