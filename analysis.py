from LogRecordMgr import LogRecordMgr
from CommNodeMgr import CommNodeMgr
from matplotlib import pyplot as plt
import numpy as np
def comm_size_distri(comm_node_mgr_dict):
    sname = ["Small: 1B~1KB","Medium: 1KB~1MB","Large: >1MB"]
    def size_classify(size):
        if size<1000:
            return 0
        elif size>=1000 and size<1000000:
            return 1
        else:
            return 2
    total_distri = []
    model_name = []
    for model in comm_node_mgr_dict.keys():
        model_name.append(model)
        comm_node_mgr = comm_node_mgr_dict[model]
        distri = [0, 0, 0, 0]
        commnode_num = len(comm_node_mgr.commnode_list)
        for commnode in comm_node_mgr.commnode_list:
            size = commnode.get_datasize()*4
            distri[size_classify(size)] += 1/commnode_num
        total_distri.append(distri)
    model_name = tuple(model_name)
    model_num = len(total_distri)
    X = np.arange(model_num)+1
    width = 0.15
    for i in range(3):
        size_list = []
        for j in range(model_num):
            size_list.append(total_distri[j][i])
        plt.bar(X+width*i, size_list, width = width, label=sname[i])
    plt.xticks(np.arange(model_num)+ 1 + 1*width, model_name)
    plt.xticks(fontsize=8)
    plt.legend(loc="upper right")
    plt.show()

if __name__ == '__main__':
    model_list = ["Lenet", "AlexNet", "LSTM", "Siamese", "VGG16", "Inception", "ResNet152"]
    batchsize = "1"
    comm_node_mgr_dict = {}
    log_record_mgr_dict = {}
    for model in model_list:
        commnode_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+batchsize+"-commnode.pkl"
        logrecord_savepath = "./tensorflow_results/"+model+"Log/pre/"+model.lower()+"-"+batchsize+"-logrecords.pkl"
        comm_node_mgr = CommNodeMgr()
        #log_record_mgr = LogRecordMgr()
        comm_node_mgr.recover_commnodes(commnode_savepath)
        #log_record_mgr.recover_logrecords(logrecord_savepath)
        comm_node_mgr_dict[model] = comm_node_mgr
        #log_record_mgr_dict[model] = log_record_mgr