# MetaWear_IMU_logging
Set of code to log from two separate IMUs at the same time following a TDT pulse. 

Main.py
  This is the main script that connects to the metawear sensors via their mac address. This code uses the metawear library for establishing connection. After establishing the connection 4 files are created for the x, y, z acceleration and x, y, z gyroscope outputs. Three threads are added the first two threads connect to the logging scripts for the seperate imus and the third thread runs an initial debugging code to remove any prior data or settings from the imus. 
  
logOrigS1.py  /  logOrigS2.py
  These scripts have the same setup and are threaded into the main script. First raspberrypi pin 14 is set to low and a constant loop runs to determine if the pin has changed its state. When the pin changes from low to high the imus will start logging and when the pin changes from high to low the imus will stop logging. This is called in the function main() as an event e1 for starting logging and e2 for stopping logging. Once the imu has stopped logging data will be uploaded to the raspberrypi over a period of ~5min.
  
restart.py
  This script is threaded at the beginning of the Main.py script to clear and debug the imus. 
  
pin.py
  Script used to determine the state of the pin being used to see if the pin is able to read change in TDT.
  
readTDT.py 
  Skeleton code implemented into the logOrigS1.py/logOrigS2.py code to read the pin in the background while data logging occurs. 
