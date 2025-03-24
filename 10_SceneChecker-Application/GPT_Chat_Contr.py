#!/usr/bin/python3
################################################################
# class GPT_Chat_Contr
# This file implements the access to the OpenAI GPT Model via
# the GPT chat completions API. The API-Key is read from file.
# A prompt consits of a user prompt and a system prompt
# (also named developer prompt).
#
# File: GPT_Chat_Contr.py
# Author: Detlef Heinze 
# Version: 1.0    Date: 16.03.2025 
################################################################

#Imports for access to OpenAI GPT 
from openai import OpenAI

# Class GPT_Chat_Contr realizes the connection and access to the
# OpenAI GPT Chat Completions API.
# An internet connection must be present and a file with the API-Key also. 
class GPT_Chat_Contr:
    def __init__(self, api_key_file_path, temperature=0.0):
        print("\nInitializing OpenAI GPT_Chat_Contr")
        # Path with filename to the OpenAI API-Key
        self._api_key_file_path= api_key_file_path  

        #Model to be used
        self._model= "gpt-4o"                      
        
        # What sampling temperature to use, between 0 and 2. Higher values
        # like 0.8 will make the output more random, while lower values
        # like 0.2 will make it more focused and deterministic. 
        self._temperature= temperature 

        # Text for the developer_message which specifies the rules for
        # every prompt. For older models this is called system message
        # or system prompt.              
        self._developer_messageText= ''                     
    
    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, aNumber): 
        if not (0.0 <= aNumber <= 2.0): 
            raise ValueError("Temperature must be between 0.0 and 2.0") 
        self._temperature = aNumber

    @property
    def developer_prompt(self):
        return self._developer_messageText

    # Connect to OpenAI Chat Completions API with API_KEY from a file
    # Return True, if connection is established
    def connect_ChatGPT(self):
        result= False
        print("Connecting to OpenAI Chat Completions API...")
        try:
            with open(self._api_key_file_path, 'r', encoding='utf-8') as file:
                self._api_key = file.read()
                print("API-key for GPT successfully read.")
        except: 
            print('ERROR: API-key file for OpenAI GPT not found. Put it in the root folder of the application. File name shall be openAIKey.txt')
        else:
            try:
                self.client= OpenAI(api_key= self._api_key)
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
            else:
                print('OpenAI API successfully connected.')
                result= True
        return result

    #Read the developer prompt from local text file
    def read_developer_prompt(self, developer_message_file_path):
        print("Reading system-prompt from file...", developer_message_file_path)
        try:
            with open(developer_message_file_path, 'r', encoding='utf-8') as file:
                self._developer_messageText = file.read()
        except: 
            print('ERROR: System-promt file for OpenAI GPT not found. Put it in the root folder of the application. File name shall be system_prompt.txt')
        else:
            print("System-prompt was successfully read.\n")
            
    def write_developer_prompt(self, aText, developer_message_file_path):
        print('Saving system-prompt to file:', developer_message_file_path)
        try:
            with open(developer_message_file_path, 'w', encoding='utf-8') as file:
                self._developer_messageText = aText
                file.write(aText)
        except: 
            print('ERROR: System-promt file could not be written.')
        else:
            print("System-prompt file was successfully written.\n")
    
    # Run a stateless chat including the user prompt and the developer prompt.
    # Use the value of the temperature property 
    # Return a chat completion object as result. 
    def run_prompt(self, user_prompt=''):

        print('User_prompt:\n', user_prompt)
        completion = self.client.chat.completions.create(
            model= self._model,
            messages=[
                {
                    "role": "developer", "content": self.developer_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature= self.temperature
        )
        return completion
    
    # Access the message result of a completion object 
    def get_message_result(self, aCompletion):
         
        if aCompletion.object == "chat.completion":
            return aCompletion.choices[0].message.content
        else:
            return ""

    
    
