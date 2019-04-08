import os
import sys
import Constants
import time
import re
class BaseLogRecord:
    def __init__(self, raw_message, timestr, logtype, stepid):
        self.raw_message = raw_message
        self.timestr = timestr
        self.timestamp = self.timestr_to_timestamp(timestr)
        self.logtype = logtype
        self.stepid = stepid
    def timestr_to_timestamp(self, str):
        return time.mktime(time.strptime(str[0:19], "%Y-%m-%d %H:%M:%S"))+float(str[19:-1])
    def log_print(self):
        print("============================================")
        print(self.timestr)
        print("Log Type: ", self.logtype)
        print("Step Id:", self.stepid)


class ProcessNodeLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, nodename, \
                    nodetype, device, send_device="", recv_device="", tensor_name=""):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.nodename = nodename
        self.nodetype = nodetype
        self.device = device
        # if it is SEND/RECV node, the following var must be init
        if self.nodetype == Constants.SEND_NODE or self.nodetype == Constants.RECV_NODE:
            if send_device=="" or recv_device=="" or tensor_name=="":
                print("ERROR: Lack info when init ProcessNodeLogRecord.",file=sys.stderr)
                os._exit(0)
            else:
                self.send_device = send_device
                self.recv_device = recv_device
                self.tensor_name = tensor_name
    def log_print(self):
        print("============================================")
        print(self.timestr)
        print("Log Type: ", self.logtype)
        print("Step Id: ", self.stepid)
        print("Node Name: ", self.nodename)
        print("Node Type: ", self.nodetype)
        if self.nodetype==Constants.SEND_NODE or self.nodetype == Constants.RECV_NODE:
            print("Send Device: ", self.send_device)
            print("Recv Device: ", self.recv_device)
            print("Tensor Name: ", self.tensor_name)    

class RunPartitionLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, execution_count):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.execution_count = execution_count
    def log_print(self):
        print("============================================")
        print(self.timestr)
        print("Log Type: ", self.logtype)
        print("Step Id: ", self.stepid)
        print("Execution Count: ", self.execution_count)

class SyncDoneLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, nodename):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.nodename = nodename
    def log_print(self):
        print("============================================")
        print(self.timestr)
        print("Log Type: ", self.logtype)
        print("Step Id: ", self.stepid)
        print("Node name: ", self.nodename)
class AsyncDoneLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, nodename):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.nodename = nodename
    def log_print(self):
        print("============================================")
        print(self.timestr)
        print("Log Type: ", self.logtype)
        print("Step Id: ", self.stepid)
        print("Node name: ", self.nodename)

class RequestLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, rendezvous_key, request_id):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.rendezvous_key = rendezvous_key
        self.request_id = request_id
    def log_print(self):
        print("============================================")
        print(self.timestr)
        print("Log Type: ", self.logtype)
        print("Step Id: ", self.stepid)
        print("Rendezvous Key: ", self.rendezvous_key)
        print("Request Id: ", self.request_id)

class DoneCallbackLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, rendezvous_key, request_id, \
                resp_start_ts, tensor_shape):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.rendezvous_key = rendezvous_key
        self.request_id = request_id
        self.resp_start_ts = resp_start_ts
        if tensor_shape==[]:
            print("ERROR: Lack tensor shape when init DoneCallbackLogRecord.",file=sys.stderr)
            os._exit(0)
        self.tensor_shape = tensor_shape
        self.tensor_name = self.get_tensorname(rendezvous_key)
    def get_tensorname(self, rendezvous_key):
        find_tensorname = re.match(r'.*;(edge_\d*_.*);', rendezvous_key)
        if find_tensorname!=None:
            return find_tensorname.group(1)
        else:
            print("ERROR: Cannot find tensorname when init DoneCallbackLogRecord.",file=sys.stderr)
            os._exit(0)

    def log_print(self):
        print("============================================")
        print(self.timestr)
        print("Log Type: ", self.logtype)
        print("Step Id: ", self.stepid)
        print("Rendezvous Key: ", self.rendezvous_key)
        print("Request Id: ", self.request_id)
        print("Response Start Timestamp: ", self.resp_start_ts)
        print("Tensor Name: ", self.tensor_name)
        print("Tensor Shape: ", self.tensor_shape)