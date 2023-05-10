from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value, create_voidp, create_voidp_int
from mbientlab.metawear.cbindings import *
from time import sleep
from sys import argv
import datetime
import os
import signal
import sys
import threading
import logOrigS1
import logOrigS2
import restart
from threading import Event


t3 = threading.Thread(target=restart)

now = datetime.datetime.now()
date_string = now.strftime("%Y-%m-%d %H:%M:%S")

path = f"/home/pi/Desktop/Neuromodulation/storeData/Results/{date_string}" 
try:
	os.makedirs("%s/IMUs" % path)
except OSError:
	pass





MAC_LIST = ['F6:A0:47:DB:70:EE', 'D2:46:9B:FB:64:63']	
d = MetaWear(MAC_LIST[0])
d.connect()
d2 = MetaWear(MAC_LIST[1])
d2.connect()



name = d.address
name2 = d2.address
acc_file = open(f"{path}/{name}_acc.csv", "w", buffering=4096)
gyro_file = open(f"{path}/{name}_gyro.csv", "w", buffering=4096)
acc_file2 = open(f"{path}/{name2}_acc.csv", "w", buffering=4096)
gyro_file2 = open(f"{path}/{name2}_gyro.csv", "w", buffering=4096)

t1 = threading.Thread(target=logOrigS1.main, args=(d,acc_file, gyro_file))
t2 = threading.Thread(target=logOrigS2.main, args=(d2,acc_file2, gyro_file2))

t1.start()
t2.start()
t1.join()
t2.join()


