def worker_logfile_processing(worker_logfile_path):
    # get graph and process the logfile
    graph = ["",""]
    graph_count = 0
    with open(worker_logfile_path, 'r') as f:
        line = f.readline()
        while line:
            if "Register node" in line:
                graph[graph_count%2] += "node{\n"
                line = f.readline()
                while line and "library {" not in line:
                    graph[graph_count%2] += line
                    line = f.readline()
                graph[graph_count%2] += "library {\n}\nversions {\n  producer:22\n}\n"
                graph_count += 1
    print(graph[0])
    print(graph[1])

def ps_logfile_processing():
    pass