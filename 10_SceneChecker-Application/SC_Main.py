#!/usr/bin/python3
###############################################################
# Main application file for the SceneChecker.
# It implements object detection using the Google MediaPipe
# object detection task. It uses an EfficientDet-Lite0 Model
# trained by Google AI on the COCO-Dataset.
# For checking a scene the OpenAI Chat Completions API is used.
# This file is tested on a Raspberry 4B
# running PiOS Bookworm 64bit.
#
# File: SC_Main.py
# Author: Detlef Heinze 
# Version: 1.0 Date: 16.03.2025
###########################################################

import tkinter as tk
import platform as pf
#See more imports below if it runs on Raspberry Pi

# Return "RaspberryPi" if this code is running on a Raspberry Pi
# with picamera2 installed. 
def get_platform():
    node= pf.node()
    try:
        if 'rpi' in node:
            print('Running on Raspberry  Pi:', node)
            from picamera2 import Picamera2
            print('Using Picamera2 for camera access.')
            return 'RaspberryPi'
        else:
            print('Not running on a Raspberry Pi. Aborting...')
            return'Not supported Platform'
        
    except:
        print('Running on a not supported platform or legacy PiOS like PiOS Buster or older.')
        print('Missing Picamera2 API for camera access.')
        return'Not suppoerted platform.'

# Behaviour of window close button
def on_closing():
    if mainWin.cameraState == myView.CamState.off:
        print('Stopping camera')
        mainWin.scc.cam.stop()
        mainWin.save_system_prompt()
        root.destroy()
        print("Window closed")
    else:
        print('Stop camera before closing window.')

#Create an start main application window
print("\nStarting SceneChecker 1.0\n")
runningOn= get_platform()

if runningOn == 'RaspberryPi':
    print('Initializing application window')
    #Import the needed modules
    #and create the main window.
    import SC_View as myView
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    mainWin= myView.SC_View(root)
    #Start window if initialisations are successfull
    if mainWin.initOK:
        root.mainloop()
    else:
        on_closing()
else:
    print('Abort after fatal error')
    