import sys

class core(object):
    def __init__(self):
        self.task_list = []
        self.time_list = []
        self.next_time = sys.float_info.max
        self.finish_time = sys.float_info.max
    
