#!/usr/bin/python3
################################################################
# class SC_View
# This file implements a view for the SceneChecker
# on a Raspberry Pi. 
#
# File: SC_View.py
# Author: Detlef Heinze 
# Version: 1.1   Date: 24.03.2025   
################################################################

#Imports for user interface
import tkinter as tk
from tkinter import ttk
import enum
import time

#Imports for image preparation and display
from PIL import ImageTk

#Import of own modules
from GPT_Chat_Contr import GPT_Chat_Contr
from SC_Contr import SC_Contr

# Possible states of camera
class CamState(enum.Enum): 
    off = 0  # switched off no image visible
    on = 1   # switched on images visible
    halt = 2 # last image visible 
    
#The window class of the application
class SC_View(object):

    #Initialize a new SMRC_View
    def __init__(self, master):
        self.master = master
        self.master.geometry('1300x600')
        self.master.resizable(0, 0)
        master.title("  SceneChecker 1.0")
        self.cameraState=CamState.off
        self.initOK= True
        self.checkScene_now= False
        
        print('Initializing SceneChecker Controller...')
        try:
            self.scc= SC_Contr(self)
        except Exception as e:
            self.initOK= False
            print('   ERROR: SceneChecker Controller could not be initialized properly.')
            print(e)  
        else:
            self.vertRes= self.scc.inference_size[0]
            self.horzRes= self.scc.inference_size[1]
        
        self.canv = tk.Canvas(self.master, height=self.vertRes,width= self.horzRes)
        self.canv.grid(column=0, row=0, pady=10, padx= 10) 
        self.canv.create_rectangle(4,4,self.horzRes-1, self.vertRes-1 )

        self.canv.create_text(self.vertRes/2, self.horzRes/2, text='Camera OFF', anchor='center', \
                            font=('TkMenuFont', '20', 'bold'), fill='blue')
        
        self.checkFrame= tk.Frame(self.master)
        self.checkFrame.grid(column=0,row=1)
        
        self.btnStartStop= tk.Button(self.checkFrame, text="Kamera starten", \
                                  command=self.btnStartStop_clicked)
        self.btnStartStop.pack(pady=12)
        self.btnCheckScene= tk.Button(self.checkFrame, text="Szene checken", \
                                  command=self.btnCheckScene_clicked)
        self.btnCheckScene.config(state=tk.DISABLED)
        self.btnCheckScene.pack(pady=12)
        
        print('\nInitializing video capture...')
        self.scc.configurePiCam()
        
        # Initializing OpenAI GPT chat interface.
        self.gpt_chat_contr= GPT_Chat_Contr('openAIKey.txt')
        self.gpt_chat_contr.read_developer_prompt(self.scc.developer_prompt_path)
        self.gpt_chat_contr.temperature= 0.0 #Answer with no creativity
        if not self.gpt_chat_contr.connect_ChatGPT():
            self.initOK = False
        else:
            # Insert notebook widget with system-prompt and chat in/output with GPT
            self.insert_GPT_notebook()
            print('Opening window')
    
    # Insert notebook widget with system-prompt and chat in/out tab for GPT
    def insert_GPT_notebook(self):
        self.gpt_notebook = ttk.Notebook(self.master)
        self.systemPrompt_Tab = ttk.Frame(self.gpt_notebook)
        self.chatInOut_Tab = ttk.Frame(self.gpt_notebook)
        self.gpt_notebook.add(self.systemPrompt_Tab, text='System-Prompt')
        self.gpt_notebook.add(self.chatInOut_Tab, text='Letzter Check')
        self.gpt_notebook.place(x=370, y=12)
        
        #Widgets for the system-prompt tab
        
        self.system_textWidget= tk.Text(self.systemPrompt_Tab, \
                                        width=112, height= 30)
        self.yScrollbar1= ttk.Scrollbar(self.systemPrompt_Tab, orient = 'vertical', \
                                        command = self.system_textWidget.yview)
        self.system_textWidget.grid(column=0,row=0, pady=5)
        self.system_textWidget.see('1.0') #See text from the beginning
        self.yScrollbar1.grid(column = 1, row = 0)
        self.save_sys_prompt_needed=False 
        self.system_textWidget.insert('1.0', self.gpt_chat_contr.developer_prompt)
        self.system_textWidget['state'] = 'normal'
        self.system_textWidget.bind("<<Modified>>", self.on_modified_textWidget)
        # Initialize a flag to track modifications
        self.modifyingText = False
        
        self.fileName_label = tk.Label(self.systemPrompt_Tab, text='Datei: '+ \
                                       self.scc.developer_prompt_path)
        self.fileName_label.grid(column=0, row=1, pady=5)
        
        #Widgets for the chatInOut tab
        self.chatInOut_textWidget= tk.Text(self.chatInOut_Tab, width=112, height= 30)
        self.chatInOut_textWidget.grid(column=0,row=0, pady=5)
        self.chatInOut_textWidget.insert(tk.END,'')
        self.chatInOut_textWidget['state']= 'disabled'
        self.token_label = tk.Label(self.chatInOut_Tab, text='')
        self.token_label.grid(column= 0, row=1, pady=5)
        
    
    # Event Handler
    # Event handler for switching camera on and off
    def btnStartStop_clicked(self):
        match self.cameraState:
            case CamState.off:
                self.cameraState= CamState.on
                self.imageCount=0
                self.startTime= time.time()
                self.btnStartStop['text']= 'Kamera stoppen'
                self.btnCheckScene.config(state=tk.NORMAL)
                self.runCamera()
            case CamState.on:
                self.cameraState= CamState.off
                print('Stopping camera')
                self.btnStartStop['text']= 'Kamera starten'
                self.btnCheckScene.config(state=tk.DISABLED)
                self.duration= time.time()-self.startTime
                if self.scc.imageObj > 0:
                    self.scc.imageObj= 0
                print('\nImages taken:', self.imageCount)
                print('Images taken per second: ', self.imageCount/self.duration)
                print('Duration: ', self.duration, 's')
                print()
            case CamState.halt:
                print('CamState is halted  setting on')
                self.cameraState= CamState.on
                self.imageCount=0
                self.startTime= time.time()
                self.btnStartStop['text']= 'Kamera stoppen'
                self.btnCheckScene.config(state=tk.NORMAL)
                self.runCamera()

    #Button CheckScene is clicked
    def btnCheckScene_clicked(self):
        self.checkScene_now= True
        self.btnCheckScene.config(state=tk.DISABLED)
        self.btnStartStop.config(state=tk.DISABLED)
        if self.save_sys_prompt_needed:
            self.save_system_prompt()
            self.save_sys_prompt_needed= False
    
    #Save changed system_prompt to file.
    def save_system_prompt(self):
        aText= self.system_textWidget.get("1.0", tk.END)
        self.gpt_chat_contr.write_developer_prompt(aText, self.scc.developer_prompt_path)
        
        
    #The system_prompt was changed by user
    def on_modified_textWidget(self,event):
        # Event handler method for <<Modified>> event
        # Clear the modified bit
        if not self.modifyingText:
            self.modifyingText = True  # Flag to prevent multiple triggers
            if self.cameraState != CamState.off:
                self.save_sys_prompt_needed= True
            # Reset the modified flag to False
            self.system_textWidget.edit_modified(False)

            # Reset the modifying flag after a short delay to avoid recursion
            self.master.after(0, self.reset_modifyingText_flag)

    def reset_modifyingText_flag(self):
        self.modifyingText = False
        
        
        
    #Check the actual scene with GPT
    def checkScene(self, detections):
        print('Checking szene now')
        self.token_label.config(text='')
        self.checkScene_now= False
        self.gpt_notebook.select(1)
        
        # Create and output the user_prompt from the detected objects
        # The user_promot is the scene description to be checked
        user_prompt= self.scc.create_user_prompt(detections)
        self.chatInOut_textWidget['state']= 'normal'
        self.chatInOut_textWidget.delete('1.0', tk.END)
        self.chatInOut_textWidget.insert('1.0', user_prompt + \
                                         '\nÜberprüfung läuft....\n')
        self.chatInOut_textWidget.update()
        
        # Now check the scene with OpenAI GPT using the system_prompt
        # and the user_prompt
        try:
            completion= self.gpt_chat_contr.run_prompt(user_prompt)
        except:
            self.chatInOut_textWidget.insert('end', 'ERROR: GPT ist nicht erreichbar. Es könnte ein API-Key für OpenAI fehlen.')
        else:
            check_result= completion.choices[0].message.content
            self.chatInOut_textWidget.insert('end', check_result)
            self.token_label.config(text= 'Total tokens: ' + \
                                    str(completion.usage.total_tokens))
        
        self.chatInOut_textWidget['state']= 'disabled'
        self.btnStartStop['state']= 'normal'
        self.btnStartStop['text']= 'Kamera fortsetzen'
        self.cameraState= CamState.halt  #Do not take new images
        self.master.update()           

    #Main loop for the SceneChecker
    def runCamera(self):
        print('Starting camera')
        imageObj= -1
        
        while self.cameraState == CamState.on:
            pil_image = self.scc.takePhoto()
            #Run inference on MediaPipe object detector
            detection_result= self.scc.predict_image(pil_image)
            #print(detection_result.detections)
            pil_image= self.scc.process_inference_results(pil_image, detection_result)
            
            #Save PhotoImage to member variable. This
            #prevents the image to be garbage collected
            #before it is displayed.
            self.image= ImageTk.PhotoImage(image=pil_image)
                
            #Delete last image from canvas.
            if imageObj > 0:
                self.canv.delete(imageObj)
            #Add actual image to canvas
            imageObj= self.canv.create_image(0,0,image=self.image, anchor= 'nw' )
            self.canv.update()
            self.imageCount+=1
                    
            #CheckScene if button btnCheckScene was pressed.
            if self.checkScene_now:
                self.checkScene(detection_result.detections)
            
        #Delete last image if camara was switched off to show text on canvas
        if self.cameraState == CamState.off:
            self.canv.delete(imageObj) 

    

