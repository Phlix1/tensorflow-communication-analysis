class CommNode:
    def __init__(self):
        # send_time and response_starttime are on the send machine
        # request_time and response_endtime are on the recv machine
        # clock skew between source and dest machines may affect the results 
        # especially when the size of data is small
        self.nodename=""
        self.dimnum = 0
        self.dims = []
        self.sendnode = ""
        self.recvnode = ""
        self.recvnode_consumers = []
        self.tensorname= ""
        self.sendmachine = ""
        self.recvmachine = ""
        self.send_time = {}
        self.request_time = {}
        self.response_starttime = {}
        self.response_endtime = {}
        self.using_time = {}
    def get_datasize(self):
        s = 1
        for d in self.dims:
            s = s*d
        return s
    def node_info(self):
        print("--------------------------")
        print("node name: ", self.nodename)
        print("send node: ", self.sendnode)
        print("recv node: ", self.recvnode)
        print("recv consumer: ", self.recvnode_consumers)
        print("tensor name: ", self.tensorname)
        print("send machine: ", self.sendmachine)
        print("recv machine: ", self.recvmachine)
        print("shape: ", self.dims)
        print("send time: ", self.send_time)
        print("request time: ",self.request_time)
        print("response start time: ", self.response_starttime)
        print("response end time: ", self.response_endtime)
        print("using time: ", self.using_time)
        print("step num: ", len(self.send_time))
        print("--------------------------")
    def get_step_num(self):
        slen = len(self.send_time)
        rqlen = len(self.request_time)
        rpslen = len(self.response_starttime)
        rpelen = len(self.response_endtime)
        if slen==rqlen==rpslen==rpelen:
            return slen
        else:
            return False
    def check_node(self):
        if self.nodename=="":
            print("Error: No nodename")
            self.node_info()
            return False
        if self.dimnum==0 or self.dims == []:
            print(self.nodename, "Error: No shape")
            self.node_info()
            return False
        if self.sendnode=="":
            print("Error: No sendnode")
            self.node_info()
            return False
        if self.recvnode=="":
            print("Error: No recvnode")
            self.node_info()
            return False
        if self.tensorname=="":
            print("Error: No tensorname")
            self.node_info()
            return False
        if self.sendmachine=="":
            print("Error: No sendmachine")
            self.node_info()
            return False
        if self.recvmachine=="":
            print("Error: No recvmachine")
            self.node_info()
            return False
        step_num = self.get_step_num()
        if step_num==False:
            print("Error: step num is not the same")
            self.node_info()
            return False
        return True