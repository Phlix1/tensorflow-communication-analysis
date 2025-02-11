from opMgr import opMgr
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

if __name__ == '__main__':
    worker_logpath = "./tensorflow_results_2/VGG16/vgg16-1_1-128-logfile-worker0.txt" 
    log_record_mgr = LogRecordMgr()
    graph_def = worker_logfile_processing(worker_logpath, log_record_mgr)
    op_mgr = opMgr()
    op_mgr.add_from_graph(graph_def)
    op_mgr.add_from_logrecord(log_record_mgr)
    op_mgr.save_ops("./tensorflow_results_2/VGG16/test-vgg16-1_1-128-op.pkl")
    #op_mgr.recover_ops("./tensorflow_results_2/VGG16/vgg16-1_1-128-op.pkl")
    op_mgr.ops_show()