Installation der SceneChecker-Applikation (see English Version below)
===================================================================
Voraussetzung: Raspberry Pi 4B (oder höher) mit 
  - PiOS Bookworm 64bit mit Python 3.11 
  - Raspberry Pi Camera Model 3 Wide (Camera V2 geht auch)

Empfohlen: Update von PiOS Bookworm 64bit
- sudo apt update
- sudo apt full-upgrade

Die Installation der SceneChecker-Applikation besteht aus:

1) Anschluss der Raspberry Pi Camera Model 3 Wide
   https://www.youtube.com/watch?v=r3tpas_fvRc

2) RaspberryPi starten und anmelden 
 
3) Einrichtung eines Python Environments im home-Verzeichnis.
   Vorschlag Benennung: appDevEnv
   Bei der Anlage des Environments müssen die System-Pakete mit übernommen werden:
   cd ~
   python -m venv appDevEnv --system-site-packages
   
4) Aktivierung des Python-Environments
   Für die nachfolgenden Installationen muss das Python-Environment
   aktiviert sein. Aktivierung mit: 
   source appDevEnv/bin/activate

5) Download des GitHub-Repository 
   auf dem Raspberry Pi unter dem user "pi":
   https://github.com/robodhhb/SceneChecker
   mit dem grünen Knopf "code" und dann "Download zip". 

6) LXTerminal öffnen und zip-Datei mit unzip in einem Ordner Ihrer Wahl entpacken.

7) Installation für die Objekterkennung (MediaPipe-API):
   Siehe:https:ai.google.dev/edge/mediapipe/solutions/setup_python?hl=de

8) Beschreibung für die Nutzung des  OpenAI Chat Completions API:
   https://platform.openai.com/docs/libraries?language=python

   Registrieren Sie sich bei OpenAI und melden sich dort an. 
   Über den Link https://platform.openai.com/api-keys  
   beschaffen Sie sich ein API-key (ein langer String) und speichern Ihn
   in die vorhandene Datei openAIKey.txt im Projektordner. Nur dieser String
   darf in der Datei sein.  

9) Installation des OpenAI Chat Completion API:
   pip install openai 

10) Programme starten:  
   - Python Environment aktivieren: "source appDevEnv/bin/activate" 
   - Starten im LXTerminal mit "python3 SC_Main.py" aus dem Unterordner
     ../10_SceneChecker-Application
    
------------------    
Bekannte Probleme:
a)  Falls das Paket "ImageTk" nicht gefunden wird, muss es noch
    installiert werden mit:
    sudo apt install python3-pil.imagetk
b)  Die Fehlermeldung beim Start in der Konsole kann ignoriert werden:
    Error in cpuinfo: prctl(PR_SVE_GET_VL) failed

Hinweise, Fragen, Anregungen und Ideen an:
smrc_alert@gmx.de
    
========================English Version====================================
Installation of the application "SceneChecker"
--------------------------------------------
Prerequisite: Raspberry Pi 4B (oder higher)
  - PiOS Bookworm 64bit with Python 3.11 
  - Raspberry Pi Camera Model 3 Wide (Camera V2 also possible)
   
Recommended: Update PiOS Bookworm 64bit
- sudo apt update
- sudo apt full-upgrade

Installation steps:

1) Connect Raspberry Pi Camera Model 3 Wide
   https://www.youtube.com/watch?v=r3tpas_fvRc
   
2) Start Raspberry Pi and login
 
2) Setup  Raspberry Pi Camera V2:
   https://projects-raspberry.com/getting-started-with-raspberry-pi-camera/

3) Create a python environment in user's home directory.
   Name it: appDevEnv

   When you create the environment the system-packages must be included:
   cd ~
   python -m venv appDevEnv --system-site-packages

4) Activate the python environment for the following installations:
   source appDevEnv/bin/activate

5) Download the GitHub-Repository: https://github.com/robodhhb/SceneChecker
   Press the green button "code" and select in the menu "Download zip". 

6) Open LXTerminal and unzip the downloaded zip file.

7) Install the MediaPipe-API for object-detection:
   See:https:ai.google.dev/edge/mediapipe/solutions/setup_python?hl=de

8) Manual for the use of the OpenAI Chat Completions API:
   https://platform.openai.com/docs/libraries?language=python
  
   Register at OpenAI and login.
   Use the link https://platform.openai.com/api-keys  
   to get an API-Key (a long string) and save it to the existing
   file openAIKey.txt in the project folder. Only this string
   must be present in the file. 

9) Install the OpenAI Chat Completion API:
   pip install openai 

10) Start of the application  
   - Activate the Python Environment: "source appDevEnv/bin/activate" 
   - Run "python3 SC_Main.py" with LXTerminal in the subfolder:
     ../10_SceneChecker-Application

--------------       
Known issues:
a)  If the paket "ImageTk" cannot be found, it has to be installed with:
    sudo apt install python3-pil.imagetk
    
b)  The following error message after having startet the application can be ignored:
    Error in cpuinfo: prctl(PR_SVE_GET_VL) failed

      
   

