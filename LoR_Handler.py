import win32gui, win32ui, win32con, win32api
import LoR_Queries as queries
import subprocess
import time
from PIL import Image, ImageOps
import numpy as np
import cv2
import pyautogui
from ctypes import windll

class Region:

    name = ""
    left = 0
    top = 0
    width = 0
    height = 0
    bitmap = None
    img = None
    desktop_img_dc = None

    def __init__(self, name, desktop_img_dc, left = 0, top = 0, width = 0, height = 0):
        self.name = name
        self.desktop_img_dc = desktop_img_dc
        self.bitmap = win32ui.CreateBitmap()
        self.update_geometry((left, top, width, height))
        
    def rect(self):
        return (self.left, self.top, self.width, self.height)
    
    def update_geometry(self, rect):
        print("Region", self.name, "update geometry")
        print(self.width, self.height, rect[2], rect[3])
        if self.width != rect[2] or self.height != rect[3]:
            print("update geometry to", rect)
            self.bitmap.CreateCompatibleBitmap(self.desktop_img_dc, rect[2], rect[3])

        self.left = rect[0]
        self.top = rect[1]
        self.width = rect[2]
        self.height = rect[3]

    def equals(self, rect):
        if  self.left == rect[0] and self.top == rect[1] and self.width == rect[2] and self.height == rect[3]:
            return True
        return False

    def capture(self, mem_dc):
        print("shooting", self.name)
        # print(self.bitmap.GetInfo())
        mem_dc.SelectObject(self.bitmap) 
        mem_dc.BitBlt(  (0, 0),  (self.width, self.height), 
                        self.desktop_img_dc, (self.left, self.top), 
                        win32con.SRCCOPY)
        
        self.img =  Image.frombuffer(
                    'RGB', (self.width, self.height),
                    self.bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
        
        return 


class LoR_Handler:
    Lor_app = None
    LoR_hwnd = None
    LoR_offset = (0,0)
    regions = {}
    patterns = {}
    sys_wdn_offset = (0,0)
    v_scale = 1

    desktop_hwnd = None
    desktop_dc = None
    desktop_img_dc = None
    mem_dc = None
    screenshot = None

    def __init__(self, LoR_hwnd):
        self.LoR_hwnd = LoR_hwnd
        ## create device context for desktop and client
        desktop_hwnd = win32gui.GetDesktopWindow()
        desktop_dc = win32gui.GetWindowDC(desktop_hwnd)
        self.desktop_img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        self.mem_dc = self.desktop_img_dc.CreateCompatibleDC()
        ## default system decorations
        self.sys_wdn_offset = ( win32api.GetSystemMetrics(win32con.SM_CXFRAME) + win32api.GetSystemMetrics(92), #SM_CXPADDEDBORDER
                                win32api.GetSystemMetrics(win32con.SM_CYFRAME) + win32api.GetSystemMetrics(92) + win32api.GetSystemMetrics(win32con.SM_CYCAPTION))
        self.Lor_app = Region("LoR", self.desktop_img_dc)

    def update_geometry(self):
        wl, wt, _, wb = win32gui.GetWindowRect(self.LoR_hwnd)
        cl, ct, cr, cb = win32gui.GetClientRect(self.LoR_hwnd)
        if wt != ct or wb != cb: #Not FullScreen
            self.LoR_offset = self.sys_wdn_offset
        else:
            self.LoR_offset = (0, 0)

        current_LoR_rect = (wl + self.LoR_offset[0], wt + self.LoR_offset[1], cr - cl, cb - ct)
        print("LOR_rect", current_LoR_rect)
        if self.Lor_app.equals(current_LoR_rect) == False: #geometry changed
            self.patterns = {}
            self.regions = {}
            self.v_scale = current_LoR_rect[3] / 1080
            self.Lor_app.update_geometry(current_LoR_rect)

        ## MANAGE RECTS FOR OCR

    def wait_for_selection_menu(self, nb_try = 5, sleep_duration = 1): ## generic query
        counter = 0
        while(queries.cards()["GameState"] != "Menus"):
            time.sleep(sleep_duration)
            counter = counter + 1
            if(counter > nb_try):
                return False
        return True

    def detect_pattern(self, region, pattern_cv_img):
        print("Detection in", region.name)
        self.update_geometry()
        region.capture(self.mem_dc)
        # region.img.show()
        im = ImageOps.grayscale(region.img)
        im = ImageOps.invert(im)
        # im.show()
        im.save("test.png")
        cv_im = np.array(im.convert('L'))
        res = cv2.matchTemplate(cv_im, pattern_cv_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        rects = []
        if (max_val > 0.8):
            loc = np.where( res >= 0.8)
            for pt in zip(*loc[::-1]):
                rects.append((pt[0], pt[1], pt[0] + pattern_cv_img.shape[1], pt[1] + pattern_cv_img.shape[0]))
            print("Detected at", rects)
            return True, rects[0]
        return False, None

    def get_pattern(self, name):
        pattern_cv_img = None
        if name in self.patterns:
            pattern_cv_img = self.patterns[name]
        else:
            pattern_img = Image.open(name + ".png")
            pattern_cv_img = np.array(pattern_img.convert('L'))
            width = int(pattern_cv_img.shape[1] * self.v_scale)
            height = int(pattern_cv_img.shape[0] * self.v_scale)
            print("Pattern size", width, height)
            pattern_scaled = cv2.resize(pattern_cv_img, (width, height))
            self.patterns[name] = pattern_scaled
        return pattern_scaled

    def wait4pattern(self, name, nb_try = 5, sleep_duration = 1):
        print("wait4", name)
        pattern_cv_img = self.get_pattern(name)
        source = None
        if name in self.regions:
            source = self.regions[name]
        else:
            source = self.Lor_app

        print("using", source.name)
        counter = 0
        detected_rect = (0,0,0,0)
        detected = False
        while detected == False:
            detected, detected_rect = self.detect_pattern(source, pattern_cv_img)
            self.Lor_app.img.save("tmp.png")
            counter = counter + 1
            if counter > nb_try or detected == True:
                break
            time.sleep(sleep_duration)
        
        if detected == True and name not in self.regions: ## register new region
            print(name, "detected", detected_rect, self.Lor_app.left)
            pattern_rect = (self.Lor_app.left + detected_rect[0], self.Lor_app.top + detected_rect[1], 
                            detected_rect[2]-detected_rect[0], detected_rect[3]-detected_rect[1])
            pattern_region = Region(name, self.desktop_img_dc, pattern_rect)

        detected_rect = (detected_rect[0], detected_rect[1], detected_rect[2]-detected_rect[0], detected_rect[3]-detected_rect[1])
        print("DETECTED:", detected_rect)
        return detected, detected_rect

    def click(self, rect):
        print("Going to click>", rect)
        rect2click = (self.Lor_app.left + rect[0] + int(rect[2]/2), self.Lor_app.top + rect[1] + int(rect[3]/2))
        print(self.Lor_app.top)
        pyautogui.moveTo(self.Lor_app.left + rect[0] + int(rect[2]/2), self.Lor_app.top + rect[1] + int(rect[3]/2), 0.5, pyautogui.easeInQuad)
        time.sleep(0.05)
        # pyautogui.mouseDown()
        time.sleep(0.05)
        # pyautogui.mouseUp()

    def wait4pattern_n_click(self, name, nb_try = 5, sleep_duration = 1):
        print("wait4nclick", name)
        detected, rect = self.wait4pattern(name, nb_try, sleep_duration)
        if detected == True:
            print("Going to click rect", rect)
            self.click(rect)
            return True
        return False
    
    def wait_and_click(self, btn_names, nb_try = 5, sleep_duration = 1):
        index = 0
        tries = []
        print("Ready to click", btn_names)
        while(index < len(btn_names) and index >= 0):
            print("Searching index", index, ">", btn_names[index])
            if index >= len(tries): 
                tries.append(0)
            clicked = self.wait4pattern_n_click(btn_names[index], 2, 1)
            if clicked == False:
                if tries[index] >= nb_try: ## button waited too many times
                    return False
                else:
                    tries[index] = tries[index] + 1 ## button waited too many times retry previous button
                    index = index - 1

        if index < 0: ## first button not found
            pyautogui.mouseDown()
            time.sleep(0.05)
            pyautogui.mouseUp()
            return False

        return True

    def exit(self):
        win32gui.PostMessage(LoR_h.LoR_hwnd,win32con.WM_CLOSE,0,0)
        while win32gui.FindWindow(None, 'Legends of Runeterra') != 0:
            print("waiting for LoR to be down...")
            time.sleep(0.5)

        time.sleep(5)
    

def launch():
    if win32gui.FindWindow(None, 'Legends of Runeterra') == 0:
        print("Launching LoR...")
        subprocess.Popen('"D:\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live', shell=True) 
    
    while queries.cards() == None:
        print("Waiting LoR to be up...")
        time.sleep(5)

    LoR = LoR_Handler(win32gui.FindWindow(None, 'Legends of Runeterra'))
    if win32gui.IsIconic(LoR.LoR_hwnd):
        win32gui.ShowWindow(LoR.LoR_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(LoR.LoR_hwnd)

    return LoR


LoR_h = launch()
