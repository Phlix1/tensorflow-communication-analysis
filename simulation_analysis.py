from matplotlib import pyplot as plt
from collections import OrderedDict
import numpy as np
linestyles = OrderedDict(
    [('solid',               (0, ())),
     ('loosely dotted',      (0, (1, 10))),
     ('dotted',              (0, (1, 5))),
     ('densely dotted',      (0, (1, 1))),

     ('loosely dashed',      (0, (5, 10))),
     ('dashed',              (0, (5, 5))),
     ('densely dashed',      (0, (5, 1))),

     ('loosely dashdotted',  (0, (3, 10, 1, 10))),
     ('dashdotted',          (0, (3, 5, 1, 5))),
     ('densely dashdotted',  (0, (3, 1, 1, 1))),

     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))])


if __name__ == '__main__':
    order_ratio = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
    ideal_speedup = [2.0,2.0, 2.0, 2.0, 2.0, 2.0]
    lenet_train = [1.037, 0.981, 0.931, 0.892, 0.892, 0.892]
    lenet_inference = [0.477, 0.421, 0.371, 0.332, 0.332, 0.332]
    start = 0
    plt.plot(order_ratio[start:], lenet_inference[0]/np.array(lenet_inference[start:]),linestyle='dashed', label="Lenet",linewidth = 4)
    alexnet_train = [11.070, 11.030, 10.101, 9.874, 9.845, 9.845]
    alexnet_inference = [3.72, 3.681, 2.749, 2.521, 2.492, 2.492]
    plt.plot(order_ratio[start:], alexnet_inference[0]/np.array(alexnet_inference[start:]),linestyle=linestyles['densely dashdotdotted'], label="AlexNet",linewidth = 4)
    vgg16_train = [67.307, 65.964, 60.871, 58.378, 58.098, 58.098]
    vgg16_inference = [22.418, 21.075, 15.983, 13.489, 13.210, 13.210]
    plt.plot(order_ratio[start:], vgg16_inference[0]/np.array(vgg16_inference[start:]), linestyle=linestyles['dashdotted'],label="VGG16",linewidth = 4)
    inception_train = [14.233, 13.748, 13.247, 12.963, 12.812, 12.812]
    inception_inference = [3.619, 3.134, 2.630,2.349,2.198,2.198]
    plt.plot(order_ratio[start:], inception_inference[0]/np.array(inception_inference[start:]),linestyle=linestyles['densely dashed'], label="Inception",linewidth = 4)
    resnet152_train = [25.831, 25.161, 24.378, 22.540, 22.091, 21.809]
    resnet152_inference = [8.779, 8.109, 7.325,5.487,5.039,4.756]
    plt.plot(order_ratio[start:], resnet152_inference[0]/np.array(resnet152_inference[start:]), linestyle=linestyles['densely dotted'],label="ResNet152",linewidth = 4)
    plt.plot(order_ratio[start:], ideal_speedup[start:],linewidth = 4,c='k',label="Ideal Speedup Ratio")
    plt.ylabel("Speedup Ratio",fontsize=22)
    plt.xlabel("Ordered parameter transmission percentage",fontsize=22)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20, loc="best")
    plt.grid()
    plt.show()
