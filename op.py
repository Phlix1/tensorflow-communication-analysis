import os
class op(object):
    def __init__(self, op_name, optype, op_size, op_input, op_tensorname=''):
        self.op_name = op_name # name of the op
        self.op_type = optype # N for network and C for computing
        self.op_size = op_size # communicaiton time of this op or computing time of this op
        self.op_input = op_input # input ops of this op
        if self.op_type=='N' and op_tensorname=='':
            print("Error: communication node does not have tensorname")
            os._exit(0)
        self.op_tensorname = op_tensorname # just for communication node   
    def op_show(self):
        print("--------------------------")
        print("op name: ", self.op_name) 
        print("op type: ", self.op_type)
        print("op size:", self.op_size)
        print("op input:", self.op_input)
        print("op tensorname", self.op_tensorname)
        print("--------------------------")