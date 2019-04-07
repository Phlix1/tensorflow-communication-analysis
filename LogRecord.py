import os
import sys
import Constants
import time
class BaseLogRecord:
    def __init__(self, raw_message, timestr, logtype, stepid):
        self.raw_message = raw_message
        self.timestr = timestr
        self.timestamp = self.timestr_to_timestamp(timestr)
        self.logtype = logtype
        self.stepid = stepid
    def timestr_to_timestamp(self, str):
        return time.mktime(time.strptime(str[0:19], "%Y-%m-%d %H:%M:%S"))+float(str[19:-1])

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

class RunPartitionLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, execution_count):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.execution_count = execution_count

class SyncDoneLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, nodename):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.nodename = nodename

class AsyncDoneLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, nodename):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.nodename = nodename

class RequestLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, rendezvous_key, request_id):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.rendezvous_key = rendezvous_key
        self.request_id = request_id

class DoneCallbackLogRecord(BaseLogRecord):
    def __init__(self, raw_message, timestr, logtype, stepid, rendezvous_key, request_id, \
                resp_start_ts, tensor_shape):
        BaseLogRecord.__init__(self, raw_message, timestr, logtype, stepid)
        self.rendezvous_key = rendezvous_key
        self.request_id = request_id
        self.resp_start_ts = resp_start_ts
        self.tensor_shape = tensor_shape