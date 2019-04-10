import time
def timestr_to_timestamp(str):
    return time.mktime(time.strptime(str[0:19], "%Y-%m-%d %H:%M:%S"))+float(str[19:-1])