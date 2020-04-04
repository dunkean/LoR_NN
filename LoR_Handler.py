import win32gui, win32ui, win32con
import LoR_Queries as queries
import subprocess
import time

class Region:
    name = ""
    left = 0
    top = 0
    width = 0
    height = 0
    bitmap = None

    def __init__(self, name, left, top, width, height):
        

class LoR_Handler:
    screen = None

    def __init__(self):
        self.screen = None


def launch_LoR():
    if win32gui.FindWindow(None, 'Legends of Runeterra') == 0:
        subprocess.Popen('"C:\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live', shell=True) 
    
    while queries.is_available() == False:
        print("Waiting LoR to be up...")
        time.sleep(5)

    return LoR_Handler()
