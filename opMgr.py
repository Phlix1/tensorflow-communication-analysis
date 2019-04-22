from op import op
import re
import pickle
import Constants
from utils import *
import os
class opMgr:
    def __init__(self):
        self.op_dict = {}
    def add_from_graph(self, graph_def):
        for node in graph_def.node:
            if "worker" in node.device: # we only consider the reducer(worker)
                op_name = node.name
                op_type = ''
                op_size = 0.0
                op_tensorname = ''
                op_input = []
                if node.op=="_Recv" and node.attr["recv_device"].s!=node.attr["send_device"].s:
                    op_type = 'N'
                    op_tensorname = str(node.attr["tensor_name"].s, encoding = "utf-8")
                else:
                    op_type = 'C'
                for item in node.input:
                    if item[0]=='^':
                        item = item[1:]
                    op_input.append(item)
                opnode = op(op_name, op_type, op_size, op_input, op_tensorname)
                self.op_dict[op_name] = opnode
    def add_from_logrecord(self, log_record_mgr):
        for key in self.op_dict.keys():
            op_item = self.op_dict[key]
            if op_item.op_type=='N':
                tensorshape = log_record_mgr.get_shape_by_tensorname(op_item.op_tensorname)
                size = 4.0*8.0
                for i in tensorshape:
                    size *= i
                op_item.op_size = size/Constants.BITS_PER_SECOND
            else:
                compnode_size = log_record_mgr.get_opsize_by_nodename(op_item.op_name)
                if compnode_size==False:
                    print("Error: cannot get the computation time of op ", op_item.op_name)
                    os._exit(0)
                op_item.op_size = compnode_size
    def save_ops(self, save_path):
        save_list = []
        for key in self.op_dict:
            save_list.append(self.op_dict[key].serialize_op())
        with open(save_path,'wb') as f:
            pickle.dump(save_list, f, -1)        
    def recover_ops(self, save_path):
        with open(save_path,'rb') as f:
            save_list = pickle.load(f)
        for opinfo in save_list:
            opitem = op()
            opitem.deserialize_op(opinfo)
            self.op_dict[opitem.op_name] = opitem     
    def ops_show(self):
        count = 0
        for key in self.op_dict.keys():
            self.op_dict[key].op_show()
            count += 1
        print("Total op num: ", count)
            
                

        