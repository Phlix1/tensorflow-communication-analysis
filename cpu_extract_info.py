from tensorflow.core.framework import graph_pb2
from google.protobuf import text_format
from LogRecord import *
from LogRecordMgr import LogRecordMgr
import re

def worker_logfile_processing(worker_logfile_path):
    """
    get graph and process the logfile
    return graph_pb2.GraphDef() and processed log record
    """
    log_record_mgr = LogRecordMgr()
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
                graph[graph_count%2] += "node{\n"
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
    line_count = 0
    with open(worker_logfile_path, 'r') as f:
        line = f.readline()
        while line:
            if line_count>graph_end_line:
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
    return graph_def
def ps_logfile_processing():
    pass

# following is test

graph_def = worker_logfile_processing("./LenetLog/lenet-logfile-worker0.txt")
#for node in graph_def.node:
#    print(node.name)

