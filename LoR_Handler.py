import win32gui, win32ui, win32con, win32api
import LoR_Queries as queries
import subprocess
import time
from PIL import Image, ImageOps, ImageEnhance
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
        if self.width != rect[2] or self.height != rect[3]:
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
        mem_dc.SelectObject(self.bitmap) 
        mem_dc.BitBlt(  (0, 0),  (self.width, self.height), 
                        self.desktop_img_dc, (self.left, self.top), 
                        win32con.SRCCOPY)
        
        self.img =  Image.frombuffer(
                    'RGB', (self.width, self.height),
                    self.bitmap.GetBitmapBits(True), 'raw', 'BGRX', 0, 1)
        
        return 

brain = LoR_Brain.Brain()

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

    def to_string(self):
        str = ""
        str += "HAND>" + "|".join((c["name"] for c in self.hand)) + "\\n"
        str += "BOARD>" + "|".join((c["name"] for c in self.board)) + "\\n"
        str += "PIT>" + "|".join((c["name"] for c in self.pit)) + "\\n"
        str += "CAST>" + "|".join((c["name"] for c in self.cast)) + "\\n"
        str += "OPP_PIT>" + "|".join((c["name"] for c in self.opp_pit)) + "\\n"
        str += "OPP_BOARD>" + "|".join((c["name"] for c in self.opp_board)) + "\\n"
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
        hp = -1
        mana = -1
        smana = -1
        opp_hp = -1
        opp_mana = -1
        opp_smana = -1
        atk_token = False
        opp_atk_token = False
        
    def to_string(self):
        return "hp:%s, mana:%s, smama:%s, token:%i | hp:%s, mana:%s, smana:%s, token:%i" %\
                (self.hp, self.mana, self.smana, self.atk_token, \
                self.opp_hp, self.opp_smana, self.opp_mana, self.opp_atk_token)

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

    def update_geometry(self):
        wl, wt, _, wb = win32gui.GetWindowRect(self.LoR_hwnd)
        cl, ct, cr, cb = win32gui.GetClientRect(self.LoR_hwnd)
        if wt != ct or wb != cb: #Not FullScreen
            self.LoR_offset = self.sys_wdn_offset
        else:
            self.LoR_offset = (0, 0)

        current_LoR_rect = (wl + self.LoR_offset[0], wt + self.LoR_offset[1], cr - cl, cb - ct)
        if self.Lor_app.equals(current_LoR_rect) == False: #geometry changed
            logging.info("Geometry changed > from", self.Lor_app.rect(), "to", current_LoR_rect)
            self.patterns = {}
            self.regions = {}
            self.v_scale = current_LoR_rect[3] / 1080
            self.Lor_app.update_geometry(current_LoR_rect)
            self.set_face_cards()

        ## MANAGE RECTS FOR OCR

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
        status = Status()
        status.hp = self.ocr_number("hp", 6)
        status.opp_hp = self.ocr_number("opp_hp", 6)
        status.mana = self.ocr_number("mana", 1)
        status.opp_mana = self.ocr_number("opp_mana", 1)
        status.smana = self.ocr_number("smana", 2)
        status.opp_smana = self.ocr_number("opp_smana", 2)
        if self.detect("atk_token", LoR_Constants.atk_token_rect(self.face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            status.atk_token = True
        else:
            status.atk_token = False
        status.opp_atk_token = ( self.detect("opp_atk_token"
                                , LoR_Constants.opp_atk_token_rect(self.opp_face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None)
        logging.info("OCR status: %s",)
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
            if y < 0: allcards.opp_hand.append(card)
            elif y < step: allcards.opp_board.append(card)
            elif y < 2*step: allcards.opp_pit.append(card)
            elif y < 3*step: allcards.cast.append(card)
            elif y < 4*step: allcards.pit.append(card)
            elif y < 5*step: allcards.board.append(card)
            else: allcards.hand.append(card)
        
        logging.info(allcards.to_string())
        return allcards

    def wait_for_selection_menu(self, sleep_duration = 1): ## generic query
        logging.info("Wait for deck selection menu.")
        while(queries.board()["GameState"] != "Menus"):
            time.sleep(self.duration(sleep_duration))

    def wait_for_game_to_start(self, sleep_duration = 1): ## generic query
        logging.info("Waiting for game to start...")
        cards = []
        while( len(cards) == 0):
            cards = queries.cards()
            time.sleep(self.duration(sleep_duration))
        self.set_face_cards(cards)
        self.wait_for_btn("ok")

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
        logging.info("click next", global_pos)
        global_pos = self.posToGlobal(pos)
        pyautogui.moveTo(global_pos[0], global_pos[1], 0.1, pyautogui.easeInQuad)
        pyautogui.click()

    def click(self, pos = None):
        if pos != None:
            global_pos = self.posToGlobal(pos)
            logging.info("click", global_pos)
            # center_x, center_y = self.Lor_app.center()
            # pyautogui.moveTo(center_x, center_y, 1, pyautogui.easeInQuad)
            pyautogui.moveTo(global_pos[0], global_pos[1], self.duration(0.5), pyautogui.easeInQuad)
        pyautogui.click()

    def click_mulligan(self, cards):
        for card in cards:
            pos = LoR_Constants.mulligan_button_pos(card, self.Lor_app.height)
            global_pos = self.posToGlobal(pos)
            logging.info("click mulligan", card["name"], global_pos)
            # center_x, center_y = self.Lor_app.center()
            # pyautogui.moveTo(center_x, center_y, 1, pyautogui.easeInQuad)
            pyautogui.moveTo(global_pos[0], global_pos[1], self.duration(0.5), pyautogui.easeInQuad)
            pyautogui.click()

    def drag_to_center(self, card):
        logging.info("Drag %s to center", card["name"])
        x, y = self.card_handle_pos(card)
        center_x, center_y = self.Lor_app.center()
        # pyautogui.moveTo(center_x, center_y, 0.2, pyautogui.easeInQuad)
        pyautogui.moveTo(x, y, 0.6, pyautogui.easeInQuad)
        # pyautogui.moveTo(center_x, center_x, 1, pyautogui.easeInQuad)
        pyautogui.dragTo(center_x, center_y, 0.2)
    
    def drag_to_block(self, block):
        logging.info("Drag %s to %s", block[0]["name"], block[1]["name"])
        x, y = self.card_handle_pos(block[0])
        destx, desty = self.card_handle_pos(block[1])
        center_x, center_y = self.Lor_app.center()
        pyautogui.moveTo(center_x, center_y, 0.2, pyautogui.easeInQuad)
        pyautogui.moveTo(x, y, 0.3, pyautogui.easeInQuad)
        pyautogui.dragTo(destx, desty, 0.2)

    def match_pattern(self, region, name):
        region.capture(self.mem_dc)
        # region.img.show()
        im = ImageOps.grayscale(region.img)
        im = ImageOps.invert(im)
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
                logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
                return (max_loc[0], max_loc[1], width, height)
        return None

    def register_pattern(self, name):
        if name not in self.source_patterns:
            logging.info("Adding pattern %s in sources", name)
            pattern_img = Image.open(name + ".png")
            pattern_cv_img = np.array(pattern_img.convert('L'))
            self.source_patterns[name] = pattern_cv_img

        if name not in self.patterns:
            logging.info("Adding pattern %s in patterns", name)
            pattern_cv_img = self.source_patterns[name]
            width = int(pattern_cv_img.shape[1] * self.v_scale)
            height = int(pattern_cv_img.shape[0] * self.v_scale)
            pattern_cv_img = cv2.resize(pattern_cv_img, (width, height))
            self.patterns[name] = pattern_cv_img


    def ocr_number(self, name, intensity):
        if name not in self.regions and name != "":
            rect = LoR_Constants.status_number_rect(name, self.face_card_rect, self.opp_face_card_rect, self.Lor_app.width, self.Lor_app.height)
            rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
            self.regions[name] = Region(name, self.desktop_img_dc, rect)

        region = self.regions[name]
        region.capture(self.mem_dc)
        im = ImageOps.grayscale(region.img)
        im = ImageOps.invert(im)
        enhancer = ImageEnhance.Brightness(im)
        im = enhancer.enhance(intensity)
        # if name == "mana" or name == "opp_mana" or name == "smana":
        #     im.show()
        self.ocr_api.SetVariable('tessedit_char_whitelist', digits)
        self.ocr_api.SetVariable('tessedit_char_blacklist', ascii_letters)
        self.ocr_api.SetPageSegMode(PSM.SINGLE_WORD)
        self.ocr_api.SetImage(im)
        number = self.ocr_api.GetUTF8Text().strip('\n')
        try:
            number = int(number)
        except:
            number = -1
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
        im = ImageOps.grayscale(region.img)
        im = ImageOps.invert(im)
        enhancer = ImageEnhance.Brightness(im)
        im = enhancer.enhance(2.5)
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
        
        logging.info("Detection of %s > %i:%i", name, pos[0], pos[1])
        return pos

    def wait_for_btn(self, btn_text, click = True, sleep_duration = 1):
        ocr = ""
        while ocr != btn_text:
            logging.info("Wainting for btn %s", btn_text)
            ocr = self.ocr_btn_txt()
            time.sleep(self.duration(sleep_duration))


    def wait_for_image(self, btn_names, click = True, sleep_duration = 1):
        logging.info("Waiting images %s" + "for click" if click else "", "-".join(btn_names))
        index = 0
        last_detected_pos = None
        while index < len(btn_names):
            name = btn_names[0]
            logging.info("Searching for %s", name)
            detected_pos = self.detect(name)

            if click == True:
                if detected_pos == None:
                    logging.info("%s not detected", name)
                    if last_detected_pos == None:
                        logging.info("clicking screen dumbly")
                        self.click()
                    else:
                        logging.info("clicking last detected position")
                        self.click(last_detected_pos)
                else:
                    logging.info("Clicking %s", name)
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
    

def launch():
    logging.basicConfig(filename='bot.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

    if win32gui.FindWindow(None, 'Legends of Runeterra') == 0:
        logging.info("Lauching LoR subprocess...")
        subprocess.Popen('"D:\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live', shell=True) 
    
    while queries.board() == None:
        logging.info("Waiting for service positional-rectangles to be up")
        #print("Waiting LoR to be up...")
        time.sleep(5)

    LoR = LoR_Handler(win32gui.FindWindow(None, 'Legends of Runeterra'))
    if win32gui.IsIconic(LoR.LoR_hwnd):
        win32gui.ShowWindow(LoR.LoR_hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(LoR.LoR_hwnd)

    return LoR


LoR_h = launch()









    # def wait4pattern_n_click(self, name, nb_try = 5, sleep_duration = 1):
    #     #print("wait4nclick", name)
    #     detected, rect = self.wait4pattern(name, nb_try, sleep_duration)
    #     if detected == True:
    #         #print("Going to click rect", rect)
    #         self.click(rect)
    #         return True
    #     return False
    
    
    # def wait4pattern(self, name, nb_try = 5, sleep_duration = 1):
    #     self.update_geometry()
    #     #print("wait4", name)
    #     pattern_cv_img = self.get_pattern(name)
    #     source = None
    #     if name in self.regions:
    #         source = self.regions[name]
    #     else:
    #         source = self.Lor_app

    #     #print("using", source.name)
    #     counter = 0
    #     detected_rect = (0,0,0,0)
    #     detected = False
    #     while detected == False:
    #         detected, detected_rect = self.detect_pattern(source, pattern_cv_img)
    #         # self.Lor_app.img.save("tmp.png")
    #         # counter = counter + 1
    #         # if counter > nb_try or detected == True:
    #         #     break
    #         time.sleep(sleep_duration)
        
    #     if detected == True and name not in self.regions: ## register new region
    #         #print(name, "detected", detected_rect, self.Lor_app.left)
    #         pattern_rect = (self.Lor_app.left + detected_rect[0], self.Lor_app.top + detected_rect[1], 
    #                         detected_rect[2]-detected_rect[0], detected_rect[3]-detected_rect[1])
    #         pattern_region = Region(name, self.desktop_img_dc, pattern_rect)

    #     detected_rect = (detected_rect[0], detected_rect[1], detected_rect[2]-detected_rect[0], detected_rect[3]-detected_rect[1])
    #     #print("DETECTED:", detected_rect)
    #     return detected, detected_rect
