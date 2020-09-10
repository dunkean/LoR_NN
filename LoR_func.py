import win32gui, win32con, win32process, win32api
import subprocess
import logging
import time
import sys

import LoR_ServerHandler as server
LoR_hwnd = None
def launch_application():
    if win32gui.FindWindow(None, 'Legends of Runeterra') == 0:
        logging.info("Lauching LoR subprocess...")
        subprocess.Popen('"' + sys.argv[2] + ':\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live', shell=True) 
    
    while server.board() == None:
        logging.info("Waiting for service positional-rectangles to be up")
        time.sleep(5)




    # def callback(handle, ctx):
    #     try:
    #         global LoR_hwnd
    #         name = win32gui.GetWindowText(handle)
    #         pid = win32process.GetWindowThreadProcessId(handle)
    #         proc_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid[1])
    #         proc_name = win32process.GetModuleFileNameEx(proc_handle, 0)
    #         # print(handle, name, proc_name, pid[1])
    #         if "LoR" in proc_name:
    #             # print("Found", handle)
    #             LoR_hwnd = handle
    #     except:
    #         pass

    # win32gui.EnumWindows(callback, None)
    # print("Handle", LoR_hwnd)
    
    # sys.exit(1)
    LoR_hwnd = win32gui.FindWindow(None, 'Legends of Runeterra')
    if win32gui.IsIconic(LoR_hwnd):
        win32gui.ShowWindow(LoR_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(LoR_hwnd)

    return LoR_hwnd