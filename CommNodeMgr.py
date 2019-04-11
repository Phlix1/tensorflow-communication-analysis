from CommNode import CommNode
import re
import pickle
from utils import *
class CommNodeMgr:
    '''
    TODO: Add functions to analyse the communication nodes
    '''
    def __init__(self):
        self.commnode_list = []
    def add_from_graph(self, graph_def):
        sendnode_list = []
        for node in graph_def.node:
            if node.op=="_Send" and node.attr["recv_device"].s!=node.attr["send_device"].s:
                tensorname = str(node.attr["tensor_name"].s, encoding = "utf-8")
                recvmachine = str(node.attr["recv_device"].s, encoding = "utf-8") 
                sendmachine = str(node.attr["send_device"].s, encoding = "utf-8")
                index = self.find_node_by_tensorname_recvmachin(tensorname, sendmachine, recvmachine)
                if index==False:
                    commnode = CommNode()
                    commnode.nodename = re.match(r'(.*)_S\d*', node.name).group(1)
                    commnode.sendnode = node.name
                    commnode.tensorname = tensorname
                    commnode.sendmachine = sendmachine
                    commnode.recvmachine = recvmachine
                    self.commnode_list.append(commnode)
                else:
                    self.commnode_list[index-1].sendnode = node.name
            if node.op=="_Recv" and node.attr["recv_device"].s!=node.attr["send_device"].s:            
                tensorname = str(node.attr["tensor_name"].s, encoding = "utf-8")
                recvmachine = str(node.attr["recv_device"].s, encoding = "utf-8") 
                sendmachine = str(node.attr["send_device"].s, encoding = "utf-8")
                index = self.find_node_by_tensorname_recvmachin(tensorname, sendmachine, recvmachine)
                if index==False:
                    commnode = CommNode()
                    commnode.nodename = re.match(r'(.*)_S\d*', node.name).group(1)
                    commnode.recvnode = node.name
                    commnode.tensorname = tensorname
                    commnode.sendmachine = sendmachine
                    commnode.recvmachine = recvmachine
                    self.commnode_list.append(commnode)                 
                else:
                    self.commnode_list[index-1].recvnode = node.name 
        for commnode in self.commnode_list:
            for node in graph_def.node:
                for inputnode in node.input:
                    if commnode.recvnode == inputnode:
                        commnode.recvnode_consumers.append(node.name)
                        break   

    def add_from_logrecord(self, log_record_mgr):
        for commnode in self.commnode_list:
            tensorname = commnode.tensorname
            tensorshape = log_record_mgr.get_shape_by_tensorname(tensorname)
            commnode.dimnum = len(tensorshape)
            commnode.dims = tensorshape
            log_record_mgr.get_sendtimes_by_sendnode(commnode.sendnode, commnode.send_time)
            log_record_mgr.get_req_resp_start_times_by_rendezvouskey(commnode.sendmachine, commnode.recvmachine,\
                                                                    commnode.tensorname, commnode.request_time, \
                                                                    commnode.response_starttime)
            log_record_mgr.get_response_endtimes_by_recvnode(commnode.recvnode, commnode.response_endtime)
            log_record_mgr.get_using_time_by_consumers(commnode.recvnode_consumers, commnode.using_time)
            
    def find_node_by_tensorname_recvmachin(self, tensorname, sendmachine, recvmachine):
        cnode_num = len(self.commnode_list)
        for index in range(cnode_num):
            if tensorname==self.commnode_list[index].tensorname \
                and recvmachine==self.commnode_list[index].recvmachine \
                and sendmachine==self.commnode_list[index].sendmachine:
                return index+1
        return False
    def commnode_print(self):
        for commnode in self.commnode_list:
            commnode.node_info()
        print("Total Communication Data: ", len(self.commnode_list))

    def get_commtime_by_stepid(self, stepid):
        commtime = 0.0
        machine_commtime = {}
        recvmachine_list = []
        for commnode in self.commnode_list:
            if commnode.recvmachine not in recvmachine_list:
                recvmachine_list.append(commnode.recvmachine)
        for recvmachine in recvmachine_list:
            min_comm_ts = "2200-01-01 00:00:00.000000"
            max_comm_ts = "2000-01-01 00:00:00.000000"
            for commnode in self.commnode_list:
                if commnode.recvmachine == recvmachine:
                    req_ts = commnode.request_time[stepid]
                    resp_ts = commnode.response_endtime[stepid]
                    if timestr_to_timestamp(req_ts) < timestr_to_timestamp(min_comm_ts):
                        min_comm_ts = req_ts
                    if timestr_to_timestamp(resp_ts) > timestr_to_timestamp(max_comm_ts):
                        max_comm_ts = resp_ts
            if max_comm_ts == "2000-01-01 00:00:00.000000" or min_comm_ts == "2200-01-01 00:00:00.000000":
                return False
            else:
                machine_commtime[recvmachine] = timestr_to_timestamp(max_comm_ts)-timestr_to_timestamp(min_comm_ts)
                commtime += timestr_to_timestamp(max_comm_ts)-timestr_to_timestamp(min_comm_ts)
        return commtime, machine_commtime

    def get_stepids(self):
        return list(self.commnode_list[0].request_time.keys())
    
    def save_commnodes(self, save_path):
        save_list = []
        for commnode in self.commnode_list:
            save_list.append(commnode.serialize_node())
        with open(save_path,'wb') as f:
             pickle.dump(save_list, f, -1)

    def recover_commnodes(self, save_path):
        with open(save_path,'rb') as f:
            save_list = pickle.load(f)
        for nodeinfo in save_list:
            commnode = CommNode()
            commnode.deserialize_node(nodeinfo)
            self.commnode_list.append(commnode)