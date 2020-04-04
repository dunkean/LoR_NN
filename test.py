
import win32gui, win32ui, win32con, win32api
from ctypes import windll
from PIL import Image, ImageOps, ImageEnhance
import cv2
import pyautogui
import mss
import time

# import d3dshot
    # d.capture()
    # im = d.get_latest_frame()
# from python_imagesearch.imagesearch import imagesearch, region_grabber

def low_level_winshot(rect = None):
    hdesktop = win32gui.GetDesktopWindow() 
    dl, dt, dr, db = win32gui.GetClientRect(hdesktop)
    top = dt
    left = dl
    width = dr - dl
    height = db - dt
    srcdc = windll.user32.GetWindowDC(0)
    memdc = windll.gdi32.CreateCompatibleDC(srcdc)
    bmp = windll.gdi32.CreateCompatibleBitmap(srcdc, width, height)
    windll.gdi32.SelectObject(memdc, bmp)
    windll.gdi32.BitBlt(memdc, 0, 0, width, height, srcdc, left, top, SRCCOPY)        
    bmp_header = pack('LHHHH', calcsize('LHHHH'), width, height, 1, 24)
    c_bmp_header = c_buffer(bmp_header) 
    c_bits = c_buffer(' ' * (height * ((width * 3 + 3) & -4)))
    got_bits = ctypes.windll.gdi32.GetDIBits(memdc, bmp, 0, height,
                        c_bits, c_bmp_header, DIB_RGB_COLORS)
def win_shot(rect = None):
    # hwnd = win32gui.FindWindow(None, 'Legends of Runeterra')
    # hdesktop = win32gui.GetDesktopWindow()
    # dl, dt, dr, db = win32gui.GetClientRect(hdesktop)
    # wl, wt, wr, wb = win32gui.GetWindowRect(hwnd)
    # cl, ct, cr, cb = win32gui.GetClientRect(hwnd)
    # w_head = (win32api.GetSystemMetrics(win32con.SM_CYFRAME) + win32api.GetSystemMetrics(win32con.SM_CYCAPTION) + win32api.GetSystemMetrics(92))
    # w_bord = win32api.GetSystemMetrics(win32con.SM_CXSIZEFRAME)
    # dh = dt - db
    # dw = dr - dl
    # ch = ct - cb
    # if dh == ch:
    #     w_head = 0
    #     w_bord = 0
    # client_offset = (w_bord, w_head)
    # client_rect = (wl + w_bord, wt + w_head, wr - w_bord, wb - w_bord)
    # client_size = (cr - cl, cb - ct)
        
    # hwndDC = win32gui.GetWindowDC(hwnd)
    # desktop_dc = win32gui.GetWindowDC(hdesktop)
    # mfcDC  = win32ui.CreateDCFromHandle(desktop_dc)
    # saveDC = mfcDC.CreateCompatibleDC()
    # saveBitMap = win32ui.CreateBitmap()
    # if rect != None:
    #     saveBitMap.CreateCompatibleBitmap(mfcDC, rect[2] - rect[0], rect[3] - rect[1])
    #     saveDC.SelectObject(saveBitMap)
    #     saveDC.BitBlt((rect[0],rect[1]), (rect[2] - rect[0], rect[3] - rect[1]), mfcDC, (0,0), win32con.SRCCOPY)
    # else:
    #     saveBitMap.CreateCompatibleBitmap(mfcDC, dw, dh)
    #     saveDC.SelectObject(saveBitMap)
    #     saveDC.BitBlt((0,0), (dw, dh), mfcDC, (0,0), win32con.SRCCOPY)
    
    # hdesktop = win32gui.FindWindow(None, 'Legends of Runeterra')
    # while win32gui.GetAncestor(hdesktop) != win32gui.GetDesktopWindow():
    #     hdesktop = win32gui.GetParent(hdesktop)
        
    #     print(win32gui.GetWindowText(hdesktop))
    # width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    # height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    # left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    # top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN) 

    hdesktop = win32gui.GetDesktopWindow() 
    dl, dt, dr, db = win32gui.GetClientRect(hdesktop)
    top = dt
    left = dl
    width = dr - dl
    height = db - dt
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC() 
    screenshot = win32ui.CreateBitmap()
    if rect == None:
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot) 
        mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top),win32con.SRCCOPY) 
    else:
        screenshot.CreateCompatibleBitmap(img_dc, rect[2] - rect[0], rect[3] - rect[1])
        mem_dc.SelectObject(screenshot) 
        mem_dc.BitBlt((0, 0),  (rect[2] - rect[0], rect[3] - rect[1]), img_dc, (rect[0],rect[1]), win32con.SRCCOPY) 
    
    bmpinfo = screenshot.GetInfo()
    bmpstr = screenshot.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    return im

def mss_shot(rect = None):
    monitor_number = 1
    monitor = sct.monitors[1]
    screenshot = None
    if rect != None:
        monitor = {
            "top": rect[1],  # 100px from the top
            "left": rect[0],  # 100px from the left
            "width": rect[2]-rect[0],
            "height": rect[3]-rect[1],
            "mon": monitor_number,
        }
    
    screenshot = sct.grab(monitor)
    im = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    return im

def pyauto_shot(rect = None):
    if rect == None:
        return pyautogui.screenshot()
    else:
        return pyautogui.screenshot(region = rect)


# d = d3dshot.create()
im = None
sct = mss.mss()
start = time.time()
rect = (100,100,500,500)

for i in range(100):
    # im = win_shot(rect)
    im = pyauto_shot(rect)
    # im = mss_shot(rect)
end = time.time()
print(end - start)

im.show()

## full desktop
# win 4-7 sec ok
# pyauto 4-7 sec ok
# mss 4-7 sec ok

## full rect
# 

## full windows ??