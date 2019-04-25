import os
class op(object):
    def __init__(self, op_name='', optype='', op_size=0.0, op_input=[], op_tensorname='', op_index=-1):
        self.op_name = op_name # name of the op
        self.op_type = optype # N for network and C for computing
        self.op_size = op_size # communicaiton time of this op or computing time of this op
        self.op_input = op_input # input ops of this op
        if self.op_type=='N' and op_tensorname=='' and op_index==-1:
            print("Error: communication node does not have tensorname")
            os._exit(0)
        self.op_tensorname = op_tensorname # just for communication node  
        self.op_index=op_index 
    def op_show(self):
        print("--------------------------")
        print("op name: ", self.op_name) 
        print("op type: ", self.op_type)
        print("op size:", self.op_size)
        print("op input:", self.op_input)
        print("op tensorname", self.op_tensorname)
        print("op index", self.op_index)
        print("--------------------------")
    def serialize_op(self):
        serial_result = [self.op_name, self.op_type, self.op_size, self.op_input, self.op_tensorname, self.op_index]
        return serial_result
    def deserialize_op(self, serial_result):
        self.op_name = serial_result[0]
        self.op_type = serial_result[1]
        self.op_size = serial_result[2]
        self.op_input = serial_result[3]
        self.op_tensorname = serial_result[4]
        self.op_index = serial_result[5]