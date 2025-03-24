#!/usr/bin/python3
############################################################
# Class SC_Contr
# This class realizes the application control code for
# using a camera and the object detection. Also default
# values are handled here.
#
# File: SC_Contr.py
# Author: Detlef Heinze 
# Version: 1.0    Date: 16.03.2025   
###########################################################

from picamera2 import Picamera2
import json #Access to json files

import time
import numpy as np
from PIL import ImageDraw as D

#Imports for the mediapipe object-detection task
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

#Checking the version of a package
from importlib.metadata import version

#The controller class for the SceneChecker
class SC_Contr(object):
    
    # Constructor which defines default values for settings
    def __init__(self,
                 aView,
                 minObjectScore= 0.15,
                 threshold= 10):  #detect up to 10 objects
        
        self.myView= aView
        
        #Initialization for object detection
        self.default_model ='efficientdet_lite0.tflite'
        self.default_labels = 'labelmap.txt'
        self.default_threshold= minObjectScore
        self.default_top_k= threshold    # max count of detected objects
        self.category_allowList= ["fork", "knife", "cup", "spoon","bowl"]
        print('Initializing Mediapipe Object Detector')
        print("MediaPipe Version:",version('mediapipe'))
        print('Loading {} with {} labels.'.format(self.default_model, self.default_labels))
        
        #Overwrite some default values with user's configuration
        self.import_configApp_file()
        
        print('A maximum of {} objects are detected with a score greater than {}.'.format(self.default_top_k, self.default_threshold))
        print('Category allowList: ', self.category_allowList)
        
        #Initialize MediaPipe object detction task
        BaseOptions = mp.tasks.BaseOptions
        ObjectDetector = mp.tasks.vision.ObjectDetector
        ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path= self.default_model),
            max_results=self.default_top_k,
            score_threshold= self.default_threshold,
            running_mode=VisionRunningMode.IMAGE,
            category_allowlist= self.category_allowList)
        self.detector= ObjectDetector.create_from_options(options)
        
        self.labels = self.read_label_file(self.default_labels)      
        self.inference_size = (320,320)
        print('Inference size: ', self.inference_size )
        
        #Image counter for canvas
        self.imageObj=0
    
    #Import user's configuration and update default values
    def import_configApp_file(self):
        input_file= "configApp.json"
        self.developer_prompt_path= 'system_prompt.txt'
        print('Importing: ', input_file)
        try:
            with open(input_file) as json_file:
                data = json.load(json_file)
        except:
            print('Error: Could not import', input_file)
            print('Continue with default values')
        else:
            self.default_threshold= float(data["threshold"])
            self.default_top_k= int(data["top_k"])
            self.category_allowList= data["category_allowList"]
            self.developer_prompt_path= data["default_system_prompt_path"]
        
    #Read the label file and create a dictionary
    #with key = linenumber and value= text of line
    def read_label_file(self,aFilename):
        with open(aFilename, 'r') as file:
            lines = file.readlines()
        return {i: line.strip() for i, line in enumerate(lines, 1)}
    
    
    # Configure PiCam
    # Return parameter: created PiCam
    def configurePiCam(self):
        print("Configuring Picamera2:", self.inference_size)
        self.cam = Picamera2()
        config = self.cam.create_still_configuration(
                        main={"size": self.inference_size})
        self.cam.configure(config)
        self.cam.start()
        time.sleep(2)
        return self.cam
    
    #Take a photo and return a PIL image
    def takePhoto(self):
        
        return self.cam.capture_image("main")
    
    #Predict the picture using the detector and return a list of detections.
    def predict_image(self, pil_image):
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB, data=np.asarray(pil_image))
        return self.detector.detect(mp_image)
        
    #Get and process the results of inference. Update image with objects found.
    def process_inference_results(self, image, detection_result):
        
        return self.append_objs_to_img(image, detection_result.detections, self.labels)
    
    #Add a rectangle, score and object class name to each object found on image.
    def append_objs_to_img(self, image, detections, labels):
        draw= D.Draw(image)
        for detection in detections:
            #print(detection)
            bbox = detection.bounding_box
            x0, y0 = bbox.origin_x, bbox.origin_y
            x1, y1 = x0 + bbox.width, y0+ bbox.height

            classname= detection.categories[0].category_name
            percent= detection.categories[0].score*100
            label = '{:2.0f}% {}'.format(percent,classname )
            draw.rectangle([(x0, y0), (x1, y1)],outline= 'white', width=2)
            draw.text((x0+5, y0+4),label)
                
        return image
    
    #Create and return user-prompt from detections
    def create_user_prompt(self, detections):
        self.detectedObjectString= 'Liste 1:\n'
        self.ObjectsCountString= 'Liste 2:\n'
        self.objCountDict= {}
        for aClassname in self.category_allowList:
            self.objCountDict[aClassname]= 0
        # Create "Liste1" containing each Object found with rectangle data
        # and orientation
        for detection in detections:
            classname= detection.categories[0].category_name
            bbox = detection.bounding_box
            x0, y0 = bbox.origin_x, bbox.origin_y
            x1, y1 = x0 + bbox.width, y0+ bbox.height
            self.detectedObjectString= self.detectedObjectString + \
                                       classname + ', (' + \
                                       str(x0)+ ',' + str(y0)+ ',' + \
                                       str(x1)+ ',' + str(y1) + '), ' 
            #Orientation 
            orientationCoef = bbox.width / bbox.height
            if orientationCoef < 0.8:
                orientationStr = 'senkrecht.'
            elif orientationCoef > 1.25:
                orientationStr = 'waagerecht.'
            else:
                orientationStr = 'neutral.'
            self.detectedObjectString= self.detectedObjectString +  \
                                       orientationStr + '\n'
            #Count objects
            if classname in self.objCountDict:
                self.objCountDict[classname]= self.objCountDict[classname]+1
            else:
                self.objCountDict[classname]= 1
        
        # Create "Liste 2" with object counters
        for classname, count in self.objCountDict.items():
            self.ObjectsCountString = self.ObjectsCountString + \
                                      classname + ': ' + str(count) + '.\n'   
        return self.detectedObjectString + '\n' + self.ObjectsCountString    
    
        
        
            
        
    
        
        
