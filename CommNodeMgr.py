from CommNode import CommNode
import re
class CommNodeMgr:
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