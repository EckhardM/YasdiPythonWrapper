#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""A simple SMA YASDI Library Python 3.x Wrapper
"""

__author__ = "Heiko Prüssing"
__license__ = "MIT License"
__version__ = "0.0.1"
__maintainer__ = "Heiko Prüssing"


# imports

import os
import time
from yasdimaster import *
from sd1channels import *

# Implementation

def pollLiveData(deviceList):
    """Polls for live data on given devices"""

    # List of all data channels I'd like to request
    channelsToRequest = [CHANNEl_NAME_PAC, CHANNEl_NAME_ETAG, CHANNEl_NAME_ETOTAL] 

    # The age of the channel value should not older than 1 second
    AGE_OF_VALUE_SECONDS = 1

    while True:
        for deviceHandle in devicesList:
            for channelName in channelsToRequest:
                channelListOfSpots = yasdiMasterLibrary.GetChannelHandlesEx(deviceHandle, SPOTCHANNELS)
                channelHandle = yasdiMasterLibrary.FindChannelName(deviceHandle, channelName)
                if INVALID_HANDLE == channelHandle:
                    print(f"Error: Channel {channelName} not found on device {yasdiMasterLibrary.GetDeviceName(deviceHandle)} ...")
                else:
                    channelValue = yasdiMasterLibrary.GetChannelValue(channelHandle, deviceHandle, AGE_OF_VALUE_SECONDS)
                    timestamp = yasdiMasterLibrary.GetChannelValueTimeStamp(channelHandle, deviceHandle)
                    channelUnit = yasdiMasterLibrary.GetChannelUnit(channelHandle)
                    print(f"{channelName};{channelUnit};{timestamp};{channelValue}")
            time.sleep(2)

if __name__ == "__main__":

    # Search for YASDI libraries also in the current directory fist
    os.environ["DYLD_LIBRARY_PATH"] = os.getcwd() # for macOS
    os.environ["LD_LIBRARY_PATH"] = os.getcwd() # for Linux/Unix

    yasdiMasterLibrary = YasdiMaster() # or  "." + os.sep + "yasdi.ini"
    yasdiLibrary = Yasdi()

    try:
        driverHandleList = yasdiLibrary.yasdiGetDrivers()
        if len(driverHandleList) == 0:
            raise Exception("Error: No configured interfaces available! Please check your YASDI configuration try again...")

        # Open all interfaces (drivers)
        for driverHandle in driverHandleList:
             print(f"Open interface driver '{yasdiLibrary.yasdiGetDriverName(driverHandle)}'. Success = {yasdiLibrary.yasdiSetDriverOnline(driverHandle)}" )

        # Search for SMA devices (inverters, etc...)
        print("Start searching SMA devices...")
        COUNT_OF_DEVICES_TO_BE_SEARCHED = 1
        if YE_OK != yasdiMasterLibrary.DoMasterCmdEx(cmd=CMD_DEVICE_DETECTION, param1=COUNT_OF_DEVICES_TO_BE_SEARCHED):
            print(f"Device detection failed for some reason. Maybe not all devices found as requested.")

        # Get the list of found SMA devices
        devicesList = yasdiMasterLibrary.GetDeviceHandles()
        for deviceHandle in devicesList:
            print(f"Found device: {yasdiMasterLibrary.GetDeviceName(deviceHandle)}")

        if len(devicesList) == 0:
            raise Exception("ERROR: No SMA inverter found! Check your hardware or yasdi configuration and try again...")
        
        # Endless poll for live data from devices:
        pollLiveData(devicesList)

    #except Exception as e:
    #    print(f"=> Exception: {e}")

    finally:
        yasdiMasterLibrary.yasdiMasterShutdown()
