import win32gui, win32con
import subprocess
import logging
import time
import sys

import LoR_ServerHandler as server

def launch_application():
    if win32gui.FindWindow(None, 'Legends of Runeterra') == 0:
        logging.info("Lauching LoR subprocess...")
        subprocess.Popen('"' + sys.argv[2] + ':\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live', shell=True) 
    
    while server.board() == None:
        logging.info("Waiting for service positional-rectangles to be up")
        time.sleep(5)

    LoR_hwnd = win32gui.FindWindow(None, 'Legends of Runeterra')
    if win32gui.IsIconic(LoR_hwnd):
        win32gui.ShowWindow(LoR_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(LoR_hwnd)

    return LoR_hwnd