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
GPIO.setmode(GPIO.BCM)

# Set up GPIO pin 17 as an input
pin = 14
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

# Create an Event object
e1 = threading.Event()
e2 = threading.Event()
# Define a function to run in a separate thread
def monitor_pin():
    last_state = GPIO.input(pin)
    while True:
        current_state = GPIO.input(pin)
        if current_state != last_state and current_state == GPIO.HIGH:
            print("Pin 18 has changed from low to high!")
            e1.set() # Set the Event object
        elif current_state != last_state and current_state == GPIO.LOW:
            print("Pin 18 has changed from low!")
            e2.set() # Set the Event object
        last_state = current_state
##############################################

def main(d2,acc_file2, gyro_file2):
		
	print("Get and log acc/gyro signal")
	
	sleep(1.0)
	acc_signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(d2.board)
	acc_logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(acc_signal, None, fn), resource = "acc_logger")
	gyro_signal = libmetawear.mbl_mw_gyro_bmi160_get_rotation_data_signal(d2.board)
	gyro_logger = create_voidp(lambda fn: libmetawear.mbl_mw_datasignal_log(gyro_signal, None, fn), resource = "gyro_logger")
	
	t = threading.Thread(target=monitor_pin)
	t.start()
	e1.wait()
	e1.clear()
	
	print("Start logging")
	libmetawear.mbl_mw_logging_start(d2.board, 0)
	libmetawear.mbl_mw_acc_enable_acceleration_sampling(d2.board)
	libmetawear.mbl_mw_acc_start(d2.board)
	libmetawear.mbl_mw_gyro_bmi160_enable_rotation_sampling(d2.board)
	libmetawear.mbl_mw_gyro_bmi160_start(d2.board)
		
	#sleep(10.0)
			
	e2.wait()
	e2.clear()	
	
	
	print("Stop acc and gyro")
	libmetawear.mbl_mw_acc_stop(d2.board)
	libmetawear.mbl_mw_acc_disable_acceleration_sampling(d2.board)
	libmetawear.mbl_mw_gyro_bmi160_stop(d2.board)
	libmetawear.mbl_mw_gyro_bmi160_disable_rotation_sampling(d2.board)
	libmetawear.mbl_mw_logging_stop(d2.board)
	print("Downloading data")
	libmetawear.mbl_mw_settings_set_connection_parameters(d2.board, 100, 100, 0, 6000)
	sleep(1.0)
	
	e = Event()
	def progress_update_handler(context, entries_left, total_entries):
		if (entries_left == 0):
			e.set()
		
	fn_wrapper = FnVoid_VoidP_UInt_UInt(progress_update_handler)
	download_handler = LogDownloadHandler(context = None, \
		received_progress_update = fn_wrapper, \
		received_unknown_entry = cast(None, FnVoid_VoidP_UByte_Long_UByteP_UByte), \
		received_unhandled_entry = cast(None, FnVoid_VoidP_DataP))
		
		 #Callback functions for acceleration and gyroscope code 
	def acc_callback(file, ctx, data):
		now = datetime.datetime.now()
		time = now.strftime("%H:%M:%S.%f")[:-3]
		output_str = "{time: %s, acc: %s}\n" % (time, parse_value(data))
		file.write(output_str)
	def gyro_callback(file, ctx, data):
		now = datetime.datetime.now()
		time = now.strftime("%H:%M:%S.%f")[:-3]
		output_str = "{time: %s, gyro: %s}\n" % (time, parse_value(data))
		file.write(output_str)
		
	CallbackType = CFUNCTYPE(None, c_void_p, POINTER(Data))
	acc_callback_pointer = CallbackType(lambda ctx, data: acc_callback(acc_file2, ctx, data))
	gyro_callback_pointer = CallbackType(lambda ctx, data: gyro_callback(gyro_file2, ctx, data))
		
	print("Subscribe to logger")
	libmetawear.mbl_mw_logger_subscribe(acc_logger, None, acc_callback_pointer)
	libmetawear.mbl_mw_logger_subscribe(gyro_logger, None, gyro_callback_pointer)
		
		
	print("Download data")
	libmetawear.mbl_mw_logging_download(d2.board, 0, byref(download_handler))
	e.wait()
	

	print("Resetting device")
	
	e = Event()
	d2.on_disconnect = lambda status: e.set()
	print("Debug reset")
	libmetawear.mbl_mw_debug_reset(d2.board)
	e.wait()
			
if __name__ == "__main__":
    main()
