# This code combines log_orig and adds TDT Event/Threading 
from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value, create_voidp, create_voidp_int
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event
from sys import argv
import datetime
import os
import signal
import sys
###############################33
import threading
import RPi.GPIO as GPIO

# Set up the GPIO pin
GPIO.setmode(GPIO.BCM)

# Set up GPIO pin 17 as an input
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)

# Create an Event object
e1 = threading.Event()
e2 = threading.Event()
# Define a function to run in a separate thread
def monitor_pin():
    last_state = GPIO.input(18)
    while True:
        current_state = GPIO.input(18)
        print("Pin state: ", current_state)
        if current_state != last_state and current_state == GPIO.HIGH:
            print("Pin 18 has changed from low to high!")
            e1.set() # Set the Event object
        elif current_state != last_state and current_state == GPIO.LOW:
            print("Pin 18 has changed from low!")
            e2.set() # Set the Event object
        last_state = current_state
        sleep(1.0)
##############################################

devices = []
ETC_ID = str(input("Enter Date: "))
visit_num = str(input("Enter Trial #: "))
path = ("/home/pi/Desktop/Neuromodulation/storeData/Results/%s_%s" %(ETC_ID, visit_num))
try:
	os.makedirs("%s/IMUs" % path)
except OSError:
	pass
     
MAC_LIST = ['D2:46:9B:FB:64:63','F6:A0:47:DB:70:EE']
for i, MAC in enumerate(MAC_LIST):
    
	print(f"Searching for device {i+1}...")
	d = MetaWear(MAC)
	d.connect()
	print(f"Connected to {d.address}" )
	name = d.address
	acc_file = open(f"{path}/{name}_acc.csv", "w", buffering=4096)
	gyro_file = open(f"{path}/{name}_gyro.csv", "w", buffering=4096)
	devices.append(d)

print("Configuring device")

t = threading.Thread(target=monitor_pin)
t.start()
	
print("Get and log acc/gyro signal")
acc_signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(d.board)
acc_logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(acc_signal, None, fn), resource = "acc_logger")
gyro_signal = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(d.board)
gyro_logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(gyro_signal, None, fn), resource = "gyro_logger")
e1.wait()
e1.clear()
   
print("Start logging")
libmetawear.mbl_mw_logging_start(d.board, 0)
libmetawear.mbl_mw_acc_enable_acceleration_sampling(d.board)
libmetawear.mbl_mw_acc_start(d.board)
libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(d.board)
libmetawear.mbl_mw_gyro_bmi160_start(d.board)

e2.wait()
e2.clear()	
print("Stop acc and gyro")
libmetawear.mbl_mw_acc_stop(d.board)
libmetawear.mbl_mw_acc_disable_acceleration_sampling(d.board)
libmetawear.mbl_mw_gyro_bmi160_stop(d.board)
libmetawear.mbl_mw_gyro_bmi160_disable_rotation_sampling(d.board)
libmetawear.mbl_mw_logging_stop(d.board)

print("Downloading data")
libmetawear.mbl_mw_settings_set_connection_parameters(d.board, 7.5, 7.5, 0, 6000)
e3 = Event()
def progress_update_handler(context, entries_left, total_entries):
	if (entries_left == 0):
		e3.set()
	
fn_wrapper = FnVoid_VoidP_UInt_UInt(progress_update_handler)
download_handler = LogDownloadHandler(context = None, \
	received_progress_update = fn_wrapper, \
	received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), \
	received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))
	
	 #Callback functions for acceleration and gyroscope code 
def acc_callback(file, ctx, data):
	now = datetime.datetime.now()
	time = now.strftime("%H:%M:%S")
	output_str = "{time: %s, acc: %s}\n" % (time, parse_value(data))
	file.write(output_str)
def gyro_callback(file, ctx, data):
	now = datetime.datetime.now()
	time = now.strftime("%H:%M:%S")
	output_str = "{time: %s, gyro: %s}\n" % (time, parse_value(data))
	file.write(output_str)
	
CallbackType = CFUNCTYPE(None, c_void_p, POINTER(Data))
acc_callback_pointer = CallbackType(lambda ctx, data: acc_callback(acc_file, ctx, data))
gyro_callback_pointer = CallbackType(lambda ctx, data: gyro_callback(gyro_file, ctx, data))
	
print("Subscribe to logger")
libmetawear.mbl_mw_logger_subscribe(acc_logger, None, acc_callback_pointer)
libmetawear.mbl_mw_logger_subscribe(gyro_logger, None, gyro_callback_pointer)
	
	
print("Download data")
libmetawear.mbl_mw_logging_download(d.board, 0, byref(download_handler))
e3.wait()

print("Resetting device")
for d in devices:
	e4 = Event()
	d.on_disconnect = lambda status: e4.set()
	print("Debug reset")
	libmetawear.mbl_mw_debug_reset(d.board)
	e4.wait()
