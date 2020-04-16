import win32gui, win32ui, win32con, win32api
import LoR_Queries as queries
import subprocess
import time
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import cv2
import pyautogui
from ctypes import windll
import random
import LoR_Constants
from tesserocr import PyTessBaseAPI, PSM, OEM
from string import digits, ascii_letters
import LoR_Brain
import logging
import sys
import os

brain = LoR_Brain.Brain()

class Region:
    name = ""
    left = 0
    top = 0
    width = 0
    height = 0
    bitmap = None
    img = None
    desktop_img_dc = None

    def __init__(self, name, desktop_img_dc, rect = (0,0,0,0)):
        self.name = name
        self.desktop_img_dc = desktop_img_dc
        self.bitmap = win32ui.CreateBitmap()
        self.update_geometry(rect)
        
    def rect(self):
        return (self.left, self.top, self.width, self.height)
    
    def center(self):
        return (self.left + int(self.width/2), self.top + int(self.height/2))
    
    def update_geometry(self, rect):
        if rect[2] <= 0 or rect[3] <= 0:
            logging.error("Unable to create region %s with non positive size: %i-%i", self.name, rect[2], rect[3])
        if self.width != rect[2] or self.height != rect[3]:
            try:
                self.bitmap.CreateCompatibleBitmap(self.desktop_img_dc, rect[2], rect[3])
                pass
            except:
                logging.error("Unable to create region %s compatible bitmap", self.name)
                pass

        self.left = rect[0]
        self.top = rect[1]
        self.width = rect[2]
        self.height = rect[3]

    def equals(self, rect):
        if  self.left == rect[0] and self.top == rect[1] and self.width == rect[2] and self.height == rect[3]:
            return True
        return False

    def capture(self, mem_dc):
        if self.width <= 0 or self.height <= 0 or self.bitmap == None:
            print("PROBLEM WITH REGION", self.name)
            return
        try:
            mem_dc.SelectObject(self.bitmap) 
            mem_dc.BitBlt(  (0, 0),  (self.width, self.height), 
                            self.desktop_img_dc, (self.left, self.top), 
                            win32con.SRCCOPY)
            
            self.img =  Image.frombuffer(
                        'RGB', (self.width, self.height),
                        self.bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
            pass
        except:
            logging.error("Unable to select or copy region", self.name)
            self.img = None
            pass

        return 



class Cards:
    hand = None
    opp_hand = None
    board = None
    pit = None
    cast = None
    opp_pit = None
    opp_board = None
    
    def __init__(self):
        self.hand = []
        self.opp_hand = []
        self.board = []
        self.pit = []
        self.cast = []
        self.opp_pit = []
        self.opp_board = []

    def card_to_string(self, c):
        s = ""
        if "cost" in c: s = s + "(" + str(c["cost"]) + ")"
        s = s + c["name"] + ":"
        if "real_atk" in c: s = s + str(c["real_atk"]) 
        if "real_hp" in c: s = s + "|" + str(c["real_hp"])
        if "attack" in c: s = s + "(" + str(c["attack"]) + "|"
        if "health" in c: s = s + str(c["health"]) + ")"
        return s

    def to_string(self):
        str = ""
        if len(self.hand) > 0:
            str += "HAND> " + " - ".join(( self.card_to_string(c)  for c in self.hand)) + "\n"
        if len(self.board) > 0:
            str += "BOARD> " + " - ".join((self.card_to_string(c) for c in self.board)) + "\n"
        if len(self.pit) > 0:
            str += "PIT> " + " - ".join((self.card_to_string(c) for c in self.pit)) + "\n"
        if len(self.cast) > 0:
            str += "CAST> " + " - ".join((self.card_to_string(c) for c in self.cast)) + "\n"
        if len(self.opp_pit) > 0:
            str += "OPP_PIT> " + " - ".join((self.card_to_string(c) for c in self.opp_pit)) + "\n"
        if len(self.opp_board) > 0:
            str += "OPP_BOARD> " + " - ".join((self.card_to_string(c) for c in self.opp_board)) + "\n"
        return str

class Status:
    hp = 0
    mana = 0
    smana = 0
    opp_hp = 0
    opp_mana = 0
    opp_smana = 0
    atk_token = False
    opp_atk_token = False

    def __init__(self):
        self.hp = -1
        self.mana = -1
        self.smana = -1
        self.opp_hp = -1
        self.opp_mana = -1
        self.opp_smana = -1
        self.atk_token = False
        self.opp_atk_token = False
        
    def to_string(self):
        return "hp:%s, mana:%s, smama:%s, token:%s | hp:%s, mana:%s, smana:%s, token:%s" %\
                (self.hp, self.mana, self.smana, "X" if self.atk_token == True else "-", \
                self.opp_hp, self.opp_mana, self.opp_smana, "X" if self.opp_atk_token == True else "-")

class LoR_Handler:
    Lor_app = None
    LoR_hwnd = None
    LoR_offset = (0,0)
    regions = {}
    patterns = {}
    source_patterns = {}
    sys_wdn_offset = (0,0)
    v_scale = 1

    face_card_rect = None
    opp_face_card_rect = None

    desktop_img_dc = None
    mem_dc = None
    ocr_api = None

    shot_count = 0

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
        self.ocr_api = PyTessBaseAPI(oem = OEM.TESSERACT_ONLY)
        self.update_geometry()
        self.register_number_patterns()

    def reset_devices(self):
        # self.LoR_hwnd = win32gui.FindWindow(None, 'Legends of Runeterra')
        #   ## create device context for desktop and client
        # desktop_hwnd = win32gui.GetDesktopWindow()
        # desktop_dc = win32gui.GetWindowDC(desktop_hwnd)
        # self.desktop_img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        # self.mem_dc = self.desktop_img_dc.CreateCompatibleDC()
        # ## default system decorations
        # self.sys_wdn_offset = ( win32api.GetSystemMetrics(win32con.SM_CXFRAME) + win32api.GetSystemMetrics(92), #SM_CXPADDEDBORDER
        #                         win32api.GetSystemMetrics(win32con.SM_CYFRAME) + win32api.GetSystemMetrics(92) + win32api.GetSystemMetrics(win32con.SM_CYCAPTION))
        # self.Lor_app = Region("LoR", self.desktop_img_dc)
        self.ocr_api = PyTessBaseAPI(oem = OEM.TESSERACT_ONLY)


    def update_geometry(self):
        wl, wt, _, wb = win32gui.GetWindowRect(self.LoR_hwnd)
        cl, ct, cr, cb = win32gui.GetClientRect(self.LoR_hwnd)
        if wt != ct or wb != cb: #Not FullScreen
            self.LoR_offset = self.sys_wdn_offset
        else:
            self.LoR_offset = (0, 0)

        current_LoR_rect = (wl + self.LoR_offset[0], wt + self.LoR_offset[1], cr - cl, cb - ct)
        if self.Lor_app.equals(current_LoR_rect) == False: #geometry changed
            logging.info("Geometry changed")
            self.patterns = {}
            self.regions = {}
            self.v_scale = current_LoR_rect[3] / 1080
            self.Lor_app.update_geometry(current_LoR_rect)
            self.set_face_cards()
        
        if self.face_card_rect == None or self.opp_face_card_rect == None:
            self.set_face_cards()


    def set_face_cards(self, cards = None):
        logging.info("updating face cards")
        if cards == None:
            logging.info("no cards provided")
            cards = queries.cards()

        if cards == None:
            self.face_card_rect = None
            self.opp_face_card_rect = None
            return

        for card in cards:
            if card["CardCode"] == "face":
                rect = (card["TopLeftX"], self.Lor_app.height - card["TopLeftY"], card["Width"], card["Height"])
                if card["LocalPlayer"] == True:
                    self.face_card_rect = rect
                else:
                    self.opp_face_card_rect = rect
    
    def get_status(self):
        self.update_geometry()
        self.register_number_patterns()
        status = Status()
        status.hp = self.pattern_detect_number("hp")
        status.opp_hp = self.pattern_detect_number("opp_hp")
        status.mana = self.pattern_detect_number("mana")
        status.opp_mana = self.pattern_detect_number("opp_mana")
        status.smana = self.pattern_detect_number("smana")
        status.opp_smana = self.pattern_detect_number("opp_smana")
        # time.sleep(2)
        # status.hp = self.ocr_number("hp")
        # status.opp_hp = self.ocr_number("opp_hp")
        # status.mana = self.ocr_number("mana")
        # status.opp_mana = self.ocr_number("opp_mana")
        # status.smana = self.ocr_number("smana")
        # status.opp_smana = self.ocr_number("opp_smana")
        if self.detect("atk_token", LoR_Constants.atk_token_rect(self.face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            status.atk_token = True
        else:
            status.atk_token = False

        if self.detect("opp_atk_token", LoR_Constants.opp_atk_token_rect(self.opp_face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            status.opp_atk_token = True
        else:
            status.opp_atk_token = False
        
        logging.info("OCR status: %s", status.to_string())

        return status


    def get_board_cards(self):
        logging.info("Computing card repartition on board")
        self.update_geometry()
        playable_cards = queries.get_playable_cards()
        brain.complete(playable_cards)
        allcards = Cards()
        step = self.Lor_app.height / 6

        for card in playable_cards:
            y = self.Lor_app.height - card["TopLeftY"]
            if y < 0: 
                allcards.opp_hand.append(card)
                # card["real_cost"] = self.ocr_number(card, "cost", "top")
            elif y < step: 
                allcards.opp_board.append(card)
                card["real_hp"] = self.ocr_number(card, "hp", "bot")
                card["real_atk"] = self.ocr_number(card, "atk", "bot")
            elif y < 2*step: 
                allcards.opp_pit.append(card)
                card["real_hp"] = self.ocr_number(card, "hp", "bot")
                card["real_atk"] = self.ocr_number(card, "atk", "bot")
            elif y < 3*step: 
                allcards.cast.append(card)
            elif y < 4*step: 
                allcards.pit.append(card)
                if card["type"] == "Unit":
                    card["real_hp"] = self.ocr_number(card, "hp", "top")
                    card["real_atk"] = self.ocr_number(card, "atk", "top")
            elif y < 5*step: 
                allcards.board.append(card)
                card["real_hp"] = self.ocr_number(card, "hp", "top")
                card["real_atk"] = self.ocr_number(card, "atk", "top")
            else: 
                allcards.hand.append(card)
        
        logging.info(allcards.to_string())
        # print(allcards.to_string())
        return allcards

    def wait_for_selection_menu(self, sleep_duration = 1): ## generic query
        logging.info("Wait for deck selection menu.")
        while(queries.board()["GameState"] != "Menus"):
            time.sleep(self.duration(sleep_duration))

    def wait_for_game_to_start(self, sleep_duration = 1): ## generic query
        logging.info("Waiting for game to start...")
        cards = []
        while( cards == None or len(cards) == 0 ):
            cards = queries.cards()
            time.sleep(self.duration(sleep_duration))
        self.set_face_cards(cards)
        if self.face_card_rect == None:
            self.wait_for_game_to_start()
        else:
            self.wait_for_btn_ingame()


    def duration(self, sec):
        return  (random.random()-0.5) * sec + sec

    def posToGlobal(self, pos):
        return pos[0] + self.Lor_app.left, pos[1] + self.Lor_app.top

    def invert_Y(self, pos):
        return pos[0], self.Lor_app.height - pos[1]

    def card_handle_pos(self, card):
        pos = queries.get_card_pos(card)
        x = self.Lor_app.left + int(pos[0] + card["Width"]/5)
        y = self.Lor_app.top + self.Lor_app.height - int(pos[1] - card["Height"]/6)
        return x, y

    def click_next(self):
        pos = LoR_Constants.game_button_pos(self.face_card_rect, self.Lor_app.width, self.Lor_app.height)
        global_pos = self.posToGlobal(pos)
        logging.info("click next %i:%i", global_pos[0], global_pos[1])
        pyautogui.moveTo(global_pos[0], global_pos[1], 0.1, pyautogui.easeInQuad)
        pyautogui.click()

    def click(self, pos = None):
        if pos != None:
            global_pos = self.posToGlobal(pos)
            logging.info("click %i:%i", global_pos[0], global_pos[1])
            pyautogui.moveTo(global_pos[0], global_pos[1], self.duration(0.5), pyautogui.easeInQuad)
        pyautogui.click()

    def click_card(self, card):
        self.click(self.card_handle_pos(card))

    def click_mulligan(self, cards):
        for card in cards:
            pos = LoR_Constants.mulligan_button_pos(card, self.Lor_app.height)
            global_pos = self.posToGlobal(pos)
            logging.info("click mulligan %s %i:%i", card["name"], global_pos[0], global_pos[1])
            pyautogui.moveTo(global_pos[0], global_pos[1], self.duration(0.5), pyautogui.easeInQuad)
            pyautogui.click()

    def drag_to_center(self, card):
        logging.info("Drag %s to center", card["name"])
        x, y = self.card_handle_pos(card)
        center_x, center_y = self.Lor_app.center()
        pyautogui.moveTo(x, y, 0.6, pyautogui.easeInQuad)
        pyautogui.dragTo(center_x, center_y, 0.2)
    
    def drag_to_block(self, block):
        logging.info("Drag %s to %s", block[0]["name"], block[1]["name"])
        x, y = self.card_handle_pos(block[0])
        destx, desty = self.card_handle_pos(block[1])
        center_x, center_y = self.Lor_app.center()
        pyautogui.moveTo(center_x, center_y, 0.2, pyautogui.easeInQuad)
        pyautogui.moveTo(x, y, 0.3, pyautogui.easeInQuad)
        pyautogui.dragTo(destx, desty, 0.2)



    def match_pattern_number(self, im, name):
        # im.save("Capture.png")
        cv_im = np.array(im.convert('L'))
        pattern_cv_img = self.patterns[name]
        width = pattern_cv_img.shape[1]
        height = pattern_cv_img.shape[0]
        res = cv2.matchTemplate(cv_im, pattern_cv_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if (max_val > 0.8):
            logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
            return (max_loc[0], max_loc[1], width, height)

        pattern_cv_img = self.source_patterns[name]
        logging.info("Attempting scaling for detection")
        for i in range(-5, 5, 1):
            scale = i/100 + self.v_scale
            width = int(pattern_cv_img.shape[1] * scale)
            height = int(pattern_cv_img.shape[0] * scale)
            pattern_scaled = cv2.resize(pattern_cv_img, (width, height))
            res = cv2.matchTemplate(cv_im, pattern_scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if (max_val > 0.9):
                logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
                return (max_loc[0], max_loc[1], width, height)
        return None

    def match_pattern(self, region, name, filter = False):
        region.capture(self.mem_dc)
        if region.img == None:
            return None
        im = ImageOps.grayscale(region.img)
        im = ImageOps.invert(im)
        # im.save("Capture.png")
        cv_im = np.array(im.convert('L'))
        pattern_cv_img = self.patterns[name]
        width = pattern_cv_img.shape[1]
        height = pattern_cv_img.shape[0]
        res = cv2.matchTemplate(cv_im, pattern_cv_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if (max_val > 0.8):
            logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
            return (max_loc[0], max_loc[1], width, height)

        pattern_cv_img = self.source_patterns[name]
        logging.info("Attempting scaling for detection")
        for i in range(-5, 5, 1):
            scale = i/100 + self.v_scale
            width = int(pattern_cv_img.shape[1] * scale)
            height = int(pattern_cv_img.shape[0] * scale)
            pattern_scaled = cv2.resize(pattern_cv_img, (width, height))
            res = cv2.matchTemplate(cv_im, pattern_scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if (max_val > 0.8):
                print("detected at another scale")
                logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
                return (max_loc[0], max_loc[1], width, height)
        return None

    def register_pattern(self, name):
        if name not in self.source_patterns:
            logging.info("Adding pattern %s in sources", name)
            pattern_img = Image.open("assets/" + name + ".png")
            pattern_cv_img = np.array(pattern_img.convert('L'))
            self.source_patterns[name] = pattern_cv_img

        if name not in self.patterns:
            logging.info("Adding pattern %s in patterns", name)
            pattern_cv_img = self.source_patterns[name]
            width = int(pattern_cv_img.shape[1] * self.v_scale)
            height = int(pattern_cv_img.shape[0] * self.v_scale)
            pattern_cv_img = cv2.resize(pattern_cv_img, (width, height))
            self.patterns[name] = pattern_cv_img

    def register_number_patterns(self):
        for i in range(1,21):
            self.register_pattern("hp" + str(i))
            self.register_pattern("opp_hp" + str(i))
        
        for i in range(0,11):
            self.register_pattern("mana" + str(i))
            self.register_pattern("opp_mana" + str(i))
        
        for i in range(0,4):
            self.register_pattern("smana" + str(i))
            self.register_pattern("opp_smana" + str(i))
        

    def pattern_detect_number(self, name):
        self.update_geometry()
        region = None
        if name not in self.regions and name != "":
            rect = LoR_Constants.status_number_rect(name, self.face_card_rect, self.opp_face_card_rect, self.Lor_app.width, self.Lor_app.height)
            rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
            self.regions[name] = Region(name, self.desktop_img_dc, rect)
            region = self.regions[name]
        else:
            region = self.regions[name]

        region.capture(self.mem_dc)
        # if "opp_smana" in name:
        #     region.img.show()
        if region.img == None:
            return -1

        interval = None
        if "hp" in name:
            interval = range(20,0,-1)
        elif "smana" in name:
            interval = range(0,4)
        elif "mana" in name:
            interval = range(10,-1,-1)

        im = self.ocr_filter_img(region.img)
        # im.show()
        for number in interval:
            # try:
            rect = self.match_pattern_number(im, name + str(number))
            if rect != None:
                logging.info("Pattern number %s: %i >", name, number)
                return number
            else:
                logging.info("Pattern number %s not detected", name)
            # except:
            #     print("Exception at", name + str(number))
            #     sys.exit()
        return -1


    def ocr_filter_img(self, im):
        if im == None:
            return im
        dat = im.getdata()
        f = []
        for d in dat:
            if d[0] >= 254 and d[1] >= 254 and d[2] >= 254: #chp catk
                f.append((0,0,0))
            elif d[0] <= 28 and d[1] == 255 and d[2] <= 80: #chp catk boost
                f.append((0,0,0))
            elif d[0] == 255 and d[1] <=2 and d[2] <=2: #chp catk malus
                f.append((0,0,0))
            elif d[0] <= 179 and d[0] >= 164 and d[1] <= 230 and d[1] >= 211 and d[2] >= 233: #smana
                f.append((0,0,0))
            elif d[0] <= 205 and d[0] >= 175 and d[1] <= 220 and d[1] >= 190 and d[2] <= 235 and d[2] >= 215: #mana
                f.append((0,0,0))
            elif d[0] == 245 and d[1] == 245 and d[2] == 250: #hp
                f.append((0,0,0))
            elif d[0] == 246 and d[1] == 227 and d[2] == 227: #card cost
                f.append((0,0,0))
            else:
                f.append((255,255,255))
        im.putdata(f)
        im = ImageOps.grayscale(im)
        # im = im.filter(ImageFilter.GaussianBlur(4))
        # im = ImageOps.invert(im)
        return im

    def ocr_number(self, name, prop = "", pos = ""):       
        region = None
        if prop != "":
            rect = LoR_Constants.card_prop_rect(name, prop, pos, self.Lor_app.width, self.Lor_app.height)
            rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
            region = Region(name, self.desktop_img_dc, rect)
        elif name not in self.regions and name != "":
            rect = LoR_Constants.status_number_rect(name, self.face_card_rect, self.opp_face_card_rect, self.Lor_app.width, self.Lor_app.height)
            rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
            self.regions[name] = Region(name, self.desktop_img_dc, rect)
            region = self.regions[name]
        else:
            region = self.regions[name]

        region.capture(self.mem_dc)

        if region.img == None:
            return -1
        im = self.ocr_filter_img(region.img)
        
        self.ocr_api.SetVariable('tessedit_char_whitelist', digits)
        self.ocr_api.SetVariable('tessedit_char_blacklist', ascii_letters)
        self.ocr_api.SetPageSegMode(PSM.SINGLE_WORD)
        self.ocr_api.SetImage(im)
       
        number = self.ocr_api.GetUTF8Text().strip('\n')
        try:
            number = int(number)
            
            # if not os.path.isfile("assets/" + name + str(number) + ".png"):
            #     region.img.save("assets/" + name + str(number) + ".png")
                # region.img.show()
        except:
            # print(name)
            # im.show()
            number = -1
        
        # if number <= 20:
        #     im.save("samples/im ("+str(number)+")/" + str(self.shot_count) + ".png")
        # else:
        #     im.save("samples/im (--)/" + name + '_' + str(self.shot_count) + ".png")

        self.shot_count += 1
        logging.info("OCR number %i >", number)
        return int(number)

    def ocr_btn_txt(self):
        self.update_geometry()
        if "game_buton" not in self.regions:
            logging.info("Creating region for button text")
            btn_rect = LoR_Constants.game_button_rect(self.face_card_rect, self.Lor_app.width, self.Lor_app.height)
            btn_rect = (btn_rect[0] + self.Lor_app.left, btn_rect[1] + self.Lor_app.top, btn_rect[2], btn_rect[3])
            self.regions["game_buton"] = Region("game_buton", self.desktop_img_dc, btn_rect)

        region = self.regions["game_buton"]
        region.capture(self.mem_dc)
        # region.img.show()
        if region.img == "ERROR":
            return None
        im = self.ocr_filter_img(region.img)
        self.ocr_api.SetPageSegMode(PSM.SINGLE_BLOCK)
        self.ocr_api.SetVariable('tessedit_char_whitelist', ascii_letters)
        self.ocr_api.SetVariable('tessedit_char_blacklist', digits)
        self.ocr_api.SetImage(im)
        text = self.ocr_api.GetUTF8Text().strip('\n')
        logging.info("Btn text detected as %s", text)
        return text.lower()

    def detect(self, name, src_rect = None):
        self.update_geometry()
        self.register_pattern(name)
        source = None
        if name in self.regions:
            source = self.regions[name]
        else:
            if src_rect == None:
                source = self.Lor_app
            else:
                src_rect = (src_rect[0] + self.Lor_app.left, src_rect[1] + self.Lor_app.top, src_rect[2], src_rect[3])
                self.regions[name] = Region(name, self.desktop_img_dc, src_rect)
                source = self.regions[name]

        rect = self.match_pattern(source, name)
        if rect == None and name in self.regions and src_rect == None:
            rect = self.match_pattern(self.Lor_app, name)
        if rect != None and name not in self.regions:
            self.regions[name] = Region(name, self.desktop_img_dc, rect)

        pos = None
        if rect != None:
            pos = (rect[0] + int(rect[2]/2), rect[1] + int(rect[3]/2))
            # print("Detection of %s > %i:%i", name, pos[0], pos[1])
            logging.info("Detection of %s > %i:%i", name, pos[0], pos[1])
        else:
            # print(name, "not detected")
            logging.info("%s not detected", name)
        return pos

    def wait_for_btn_ingame(self, sleep_duration = 1):
        self.update_geometry()
        btn_values = ["round","pass","skip","select","attack","block","turn","summon","ok"]
        detected = False
        while detected == False:
            logging.info("Wainting for button to be usable for play")
            ocr = self.ocr_btn_txt()
            # print(ocr)
            for v in btn_values:
                if v in ocr:
                    return
            time.sleep(self.duration(sleep_duration))


    def wait_for_image(self, btn_names, click = True, sleep_duration = 3):
        logging.info("Waiting images %s" + "for click" if click else "", "-".join(btn_names))
        # print("Waiting images %s" + "for click" if click else "", "-".join(btn_names))
        index = 0
        last_detected_pos = None
        tries = 0
        while index < len(btn_names):
            name = btn_names[0]
            logging.info("Searching for %s", name)
            # print("Searching for %s", name)
            detected_pos = self.detect(name)

            if click == True:
                if detected_pos == None:
                    tries += 1
                    # print("Not detected for %s times", tries)
                    if tries > 3:
                        tries == 0
                        logging.info("%s not detected", name)
                        # print("%s not detected", name)
                        if last_detected_pos == None:
                            logging.info("clicking screen dumbly")
                            # print("clicking screen dumbly")
                            self.click()
                        else:
                            logging.info("clicking last detected position")
                            # print("clicking last detected position")
                            self.click(last_detected_pos)
                else:
                    logging.info("Clicking %s", name)
                    # print("Clicking %s", name)
                    btn_names.pop(0)
                    last_detected_pos = detected_pos
                    self.click(detected_pos)

            time.sleep(self.duration(sleep_duration))
        return True

    def exit(self):
        logging.info("Closing LoR Window...")
        win32gui.PostMessage(LoR_h.LoR_hwnd,win32con.WM_CLOSE,0,0)

        while win32gui.FindWindow(None, 'Legends of Runeterra') != 0:
            logging.info("Waiting for LoR window handler == None")
            #print("waiting for LoR to be down...")
            time.sleep(0.5)

        time.sleep(5)

def raw_capture():
    LoR = launch()
    LoR.update_geometry()
    LoR.Lor_app.capture(LoR.mem_dc)
    # im = ImageOps.grayscale(LoR.Lor_app.img)
    # im = ImageOps.invert(im)
    im = LoR.ocr_filter_img(LoR.Lor_app.img)
    im.save("capture.png")

def launch():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log")
        ]
    )

    if win32gui.FindWindow(None, 'Legends of Runeterra') == 0:
        logging.info("Lauching LoR subprocess...")
        subprocess.Popen('"' + sys.argv[2] + ':\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live', shell=True) 
    
    while queries.board() == None:
        logging.info("Waiting for service positional-rectangles to be up")
        time.sleep(5)

    LoR = LoR_Handler(win32gui.FindWindow(None, 'Legends of Runeterra'))
    if win32gui.IsIconic(LoR.LoR_hwnd):
        win32gui.ShowWindow(LoR.LoR_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(LoR.LoR_hwnd)

    return LoR


# logger = logging.getLogger('server_logger')
# logger.setLevel(logging.INFO)
# # create file handler which logs even debug messages
# fh = logging.FileHandler('server.log')
# fh.setLevel(logging.INFO)
# # create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# # create formatter and add it to the handlers
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# ch.setFormatter(formatter)
# fh.setFormatter(formatter)
# # add the handlers to logger
# logger.addHandler(ch)
# logger.addHandler(fh)
# logging.getLogger().disabled = False
# # LoR_h = launch()