import win32gui, win32ui, win32con, win32api
import subprocess
import time
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import cv2
import pyautogui
from ctypes import windll
import random
import LoR_Constants

import logging
import sys
import os
import LoR_Datamodels

from LoR_Datamodels import CardDesc, Card, Stage, State, CardType

import LoR_Brain
import LoR_ServerHandler as queries
import LoR_OCR, LoR_PatternMatcher


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

class LoR_Handler:
    Lor_app = None
    LoR_hwnd = None
    LoR_offset = (0,0)
    regions = {}
    sys_wdn_offset = (0,0)
    v_scale = 1

    face_card_rect = None
    opp_face_card_rect = None

    desktop_img_dc = None
    mem_dc = None

    shot_count = 0

    OCR = None
    matcher = None

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
        self.update_geometry()
        self.OCR = LoR_OCR.OCR()
        self.matcher = LoR_PatternMatcher.Matcher(self.v_scale)

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
    
    def btn_txt(self):
        self.update_geometry()
        if "game_buton" not in self.regions:
            logging.info("Creating region for button text")
            btn_rect = LoR_Constants.game_button_rect(self.face_card_rect, self.Lor_app.width, self.Lor_app.height)
            btn_rect = (btn_rect[0] + self.Lor_app.left, btn_rect[1] + self.Lor_app.top, btn_rect[2], btn_rect[3])
            self.regions["game_buton"] = Region("game_buton", self.desktop_img_dc, btn_rect)

        region = self.regions["game_buton"]
        region.capture(self.mem_dc)
        if region.img == "ERROR":
            return None
        else:
            return self.OCR.ocr_txt(region.img)

    def wait_for_btn(self):
        ocr = "######"
        btn_values = ["round","pass","skip","select","attack","block","turn","summon","ok"]
        detected = False
        while detected == False:
            logging.info("Wainting for button to be usable for play")
            ocr = self.btn_txt()
            if ocr == None:
                continue
            for v in btn_values:
                if v in ocr:
                    return v
            time.sleep(self.duration(1))
        return None

    def wait_for_next_state(self):
        self.update_geometry()
        state = State()
        btn = self.wait_for_btn()
        time.sleep(0.5)
        ### Status ###
        self.update_status(state)
        ### Cards ###
        self.get_board_cards(state)

        ### Stage ###
        if btn == "round" or btn == "pass":
            state.stage = Stage.Play
        elif btn == "skip":
            state.stage = Stage.Block
        elif btn == "ok":
            # if self.last_card(spell_arena).owned: ## @TODO determine the cast or counter or validate state from cards
            state.stage = Stage.Cast
            state.stage = Stage.Counter
        else:
            state.stage = Stage.Wait

        return state

    def ocr_card_number(self, card, name, pos):
        rect = LoR_Constants.card_prop_rect(card, name, pos, self.Lor_app.width, self.Lor_app.height)
        rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
        region = Region(name, self.desktop_img_dc, rect)
        region.capture(self.mem_dc)
        if region.img == None:
            return -1

        src = region.img.copy()
        number = self.OCR.ocr_number(region.img)
        if not os.path.isfile("capture/" + name + str(number) + ".png"):
            src.save("capture/" + name + str(number) + ".png")
        return number

    def ocr_pos_number(self, name, opp):
        region = None
        region_name = ("opp_" if opp else "") + name
        if region_name not in self.regions and region_name != "":
            rect = LoR_Constants.status_number_rect(name, opp, self.face_card_rect, self.opp_face_card_rect, self.Lor_app.width, self.Lor_app.height)
            rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
            self.regions[region_name] = Region(region_name, self.desktop_img_dc, rect)
            region = self.regions[region_name]
        else:
            region = self.regions[region_name]

        region.capture(self.mem_dc)
        if region.img == None:
            return -1


        src = region.img.copy()
        number = self.OCR.ocr_number(region.img)
        if not os.path.isfile("capture/" + region_name + str(number) + ".png"):
            src.save("capture/" + region_name + str(number) + ".png")
        return number
    
    def pattern_pos_number(self, name, opp, double_digit = False):
        region = None
        region_name = ("opp_" if opp else "") + name
        if region_name not in self.regions and region_name != "":
            rect = LoR_Constants.status_number_rect(name, opp, self.face_card_rect, self.opp_face_card_rect, self.Lor_app.width, self.Lor_app.height)
            rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
            self.regions[region_name] = Region(region_name, self.desktop_img_dc, rect)
            region = self.regions[region_name]
        else:
            region = self.regions[region_name]

        region.capture(self.mem_dc)
        if region.img == None:
            return -1

        return self.matcher.pattern_detect_number(region.img, name, double_digit)


    def get_board_cards(self, state):
        logging.info("Computing card repartition on board")
        playable_cards = queries.get_playable_cards()
        # brain.complete(playable_cards) #### @TODO
        
        step = self.Lor_app.height / 6
        for json_card in playable_cards:
            card = Card()
            y = self.Lor_app.height - json_card["TopLeftY"]
            x = json_card["TopLeftX"]
            h = json_card["Height"]
            w = json_card["Width"]
            card.from_json(json_card, (x,y,x+w,y+h), (w,h), (x+int(w/2), y+int(h/2)))

            if y < 0: 
                state.opponent.army.hand.append(card)
                # card["real_cost"] = self.ocr_number(card, "cost", "top") ##@TODO if card readable update cost
            elif y < step: 
                state.opponent.army.deployed.append(card)
                card.hp = self.ocr_card_number(card, "hp", "bot")
                card.atk = self.ocr_card_number(card, "atk", "bot")
            elif y < 2*step: 
                state.opponent.army.pit.append(card)
                card.hp = self.ocr_card_number(card, "hp", "bot")
                card.atk = self.ocr_card_number(card, "atk", "bot")
            elif y < 3*step: 
                state.spell_arena.append(card)
            elif y < 4*step: 
                state.player.army.pit.append(card)
                if card.type == CardType.Unit:
                    card.hp = self.ocr_card_number(card, "hp", "top")
                    card.atk = self.ocr_card_number(card, "atk", "top")
            elif y < 5*step: 
                state.player.army.deployed.append(card)
                card.hp = self.ocr_card_number(card, "hp", "top")
                card.atk = self.ocr_card_number(card, "atk", "top")
            else: 
                state.player.army.hand.append(card)

    def update_status(self, state):
        state.player.mana = self.pattern_pos_number("mana", False)
        state.opponent.mana = self.pattern_pos_number("mana", True)
        state.player.smana = self.pattern_pos_number("smana", False)
        state.opponent.smana = self.pattern_pos_number("smana", True)
        state.player.hp = self.pattern_pos_number("hp", False, True)
        state.opponent.hp = self.pattern_pos_number("hp", True, True)
        # status.hp = self.pattern_detect_number("hp")
        # status.opp_hp = self.pattern_detect_number("opp_hp")

        # status.smana = self.pattern_detect_number("smana")
        # status.opp_smana = self.pattern_detect_number("opp_smana")
        # time.sleep(2)
        # state.player.hp = self.ocr_pos_number("hp", False)
        # state.opponent.hp = self.ocr_pos_number("hp", True)
        # state.player.mana = self.ocr_pos_number("mana", False)
        # state.opponent.mana = self.ocr_pos_number("mana", True)
        # state.player.smana = self.ocr_pos_number("smana", False)
        # state.opponent.smana = self.ocr_pos_number("smana", True)

        # if self.detect("atk_token", LoR_Constants.atk_token_rect(self.face_card_rect
        #                                     , self.Lor_app.width, self.Lor_app.height)) != None:
        #     status.atk_token = True
        # else:
        #     status.atk_token = False

        # if self.detect("opp_atk_token", LoR_Constants.opp_atk_token_rect(self.opp_face_card_rect
        #                                     , self.Lor_app.width, self.Lor_app.height)) != None:
        #     status.opp_atk_token = True
        # else:
        #     status.opp_atk_token = False
        
        # logging.info("OCR status: %s", status.to_string())

        # return status



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

    def mulligan_cards(self, cards):
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



    def detect(self, name, src_rect = None):
        self.update_geometry()
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


        source.capture(self.mem_dc)
        if source.img == None:
            return None
        rect = self.matcher.match_pattern(source.img, name)

        if rect == None and name in self.regions and src_rect == None:
            self.Lor_app.capture(self.mem_dc)
            if self.Lor_app.img == None:
                return None
            rect = self.matcher.match_pattern(self.Lor_app.img, name)
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




    def wait_n_click_img(self, btn_names, click = True, sleep_duration = 3):
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