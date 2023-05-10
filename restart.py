from __future__ import print_function
import sys
from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event

# connect
d1 = MetaWear('F6:A0:47:DB:70:EE')
d2 = MetaWear('D2:46:9B:FB:64:63')

d1.connect()
d2.connect()
print("Connected to " + d1.address)
print("Connected to " + d2.address)
# stop logging
libmetawear.mbl_mw_logging_stop(d1.board)
libmetawear.mbl_mw_logging_stop(d2.board)
sleep(1.0)

# clear logger
libmetawear.mbl_mw_logging_clear_entries(d1.board)
libmetawear.mbl_mw_logging_clear_entries(d2.board)
sleep(1.0)

# remove events
libmetawear.mbl_mw_event_remove_all(d1.board)
libmetawear.mbl_mw_event_remove_all(d2.board)
sleep(1.0)

# erase macros
libmetawear.mbl_mw_macro_erase_all(d1.board)
libmetawear.mbl_mw_macro_erase_all(d2.board)
sleep(1.0)

# debug and garbage collect
libmetawear.mbl_mw_debug_reset_after_gc(d1.board)
libmetawear.mbl_mw_debug_reset_after_gc(d2.board)
sleep(1.0)

# delete timer and processors
libmetawear.mbl_mw_debug_disconnect(d1.board)
libmetawear.mbl_mw_debug_disconnect(d2.board)
sleep(1.0)

d1.disconnect()
d2.disconnect()
print("Disconnect")
sleep(1.0)
