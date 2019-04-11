from tensorflow.core.framework import graph_pb2
from google.protobuf import text_format
from LogRecord import *
from LogRecordMgr import LogRecordMgr
from CommNodeMgr import CommNodeMgr
from CommNode import CommNode
from StepInfoMgr import StepInforMgr
import re
def logfile_processing(startline, logfile_path, log_record_mgr):
    line_count = 0
    with open(logfile_path, 'r') as f:
        line = f.readline()
        while line:
            if line_count>=startline and "tensor_content" not in line:
                raw_message = ""
                ismatch = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*]', line)
                if ismatch != None:
                    while line:
                        line = line[0:-1]+" "
                        raw_message += line
                        line = f.readline()
                        is_newrecord = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}):.*]', line)
                        if is_newrecord != None:
                            break
                    log_record_mgr.parse_log_message(raw_message)
                    continue
            line_count += 1
            line = f.readline()

def worker_logfile_processing(worker_logfile_path, log_record_mgr):
    """
    get graph and process the logfile
    return graph_pb2.GraphDef() and processed log record
    """
    total_graph_str = ""
    graph_end_line = 0
    graph = ["",""]
    graph_count = 0
    line_count = 0
    with open(worker_logfile_path, 'r') as f:
        line_count += 1
        line = f.readline()
        while line:
            if "Register node" in line:
                graph[graph_count%2] = "node{\n"
                line_count += 1
                line = f.readline()
                while line and "library {" not in line:
                    graph[graph_count%2] += line
                    line_count += 1
                    line = f.readline()
                graph[graph_count%2] += "library {\n}\nversions {\n  producer:22\n}\n"
                graph_end_line = line_count
                graph_count += 1
            line_count += 1
            line = f.readline()
    total_graph_str = graph[0] + graph[1]
    graph_def = graph_pb2.GraphDef()
    text_format.Merge(total_graph_str, graph_def)
    logfile_processing(graph_end_line, worker_logfile_path, log_record_mgr)
    return graph_def

def ps_logfile_processing(ps_logfile_path, log_record_mgr):
    logfile_processing(0, ps_logfile_path, log_record_mgr)

if __name__ == '__main__':
    worker_logpath = "./tensorflow_results/ResNet152Log/worker0/resnet152-120-logfile-worker0.txt"
    ps_logpath = "./tensorflow_results/ResNet152Log/ps0/resnet152-120-logfile-ps0.txt"
    commnode_savepath = "./tensorflow_results/ResNet152Log/pre/resnet152-120-commnode.pkl"
    logrecord_savepath = "./tensorflow_results/ResNet152Log/pre/resnet152-120-logrecords.pkl"
    comm_node_mgr = CommNodeMgr()
    log_record_mgr = LogRecordMgr()
    #Step 1 read worker and ps log files and save to the log_record_mgr and graph_def
    print("----Step 1: Start formatting the worker log file and the ps log file...")
    print("--------1.1: start working with WORKER log file...")
    graph_def = worker_logfile_processing(worker_logpath, log_record_mgr)
    print("--------1.1: WORKER log file OK")
    print("--------1.2: start working with PS log file...")
    ps_logfile_processing(ps_logpath, log_record_mgr)
    print("--------1.2: PS log file OK")
    print("----Step 1: OK")
    #Step 2 use graph_def to initialize comm_node_mgr
    print("----Step 2: Start working with commnode manager...")
    print("--------2.1: start initing commnode manager with graph_def...")
    comm_node_mgr.add_from_graph(graph_def)
    print("--------2.1: INIT OK")
    print("--------2.2: start working with commnode manager with log records...")
    #Step 3 complete comm_node_mgr based on log records
    comm_node_mgr.add_from_logrecord(log_record_mgr)
    print("--------2.2: COMMNODE MANAGER OK")
    print("----Step 2: OK")
    print("----Step 3: Start saving commnode information and log records...")
    #Step 4 save comm_node_mgr and log_record_mgr
    print("--------3.1: start saving commnode information...")
    comm_node_mgr.save_commnodes(commnode_savepath)
    print("--------3.1: COMMNODE OK")
    print("--------3.2: start saving log records...")
    log_record_mgr.save_logrecords(logrecord_savepath)
    print("--------3.2: LOG OK")
    print("----Step 3: OK")   



