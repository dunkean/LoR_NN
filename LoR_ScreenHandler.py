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

from LoR_Datamodels import CardDesc, Card, Stage, State, CardType, TokenType

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
            print("CAPTURE ERROR")
            print(win32gui.error())
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

    desktop_hwnd = None
    desktop_dc = None
    desktop_img_dc = None
    mem_dc = None

    shot_count = 0

    OCR = None
    matcher = None

    def __init__(self, LoR_hwnd):
        try:
            self.LoR_hwnd = LoR_hwnd
            ## create device context for desktop and client
            self.desktop_hwnd = win32gui.GetDesktopWindow()
            self.desktop_dc = win32gui.GetWindowDC(self.desktop_hwnd)
            self.desktop_img_dc = win32ui.CreateDCFromHandle(self.desktop_dc)
            self.mem_dc = self.desktop_img_dc.CreateCompatibleDC()
            ## default system decorations
            self.sys_wdn_offset = ( win32api.GetSystemMetrics(win32con.SM_CXFRAME) + win32api.GetSystemMetrics(92), #SM_CXPADDEDBORDER
                                    win32api.GetSystemMetrics(win32con.SM_CYFRAME) + win32api.GetSystemMetrics(92) + win32api.GetSystemMetrics(win32con.SM_CYCAPTION))
            self.Lor_app = Region("LoR", self.desktop_img_dc)
            self.update_geometry()
            self.OCR = LoR_OCR.OCR()
            self.matcher = LoR_PatternMatcher.Matcher(self.v_scale)
            pyautogui.FAILSAFE = False
        except win32gui.error:
            print("GUI error in init")
            print(win32gui.error())
            self.mem_dc.DeleteDC()
            self.desktop_img_dc.DeleteDC()
            win32gui.ReleaseDC(self.desktop_hwnd, self.desktop_dc)
        
    def __del__(self):
        self.mem_dc.DeleteDC()
        self.desktop_img_dc.DeleteDC()
        win32gui.ReleaseDC(self.desktop_hwnd, self.desktop_dc)


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
            # logging.info("Waiting for button to be usable for play")
            ocr = self.btn_txt().lower()
            if ocr == None:
                continue
            for v in btn_values:
                if v in ocr:
                    return v
            # time.sleep(self.duration(1))
        return None

    def get_btn(self):
        ocr = "######"
        btn_values = ["round","pass","skip","select","attack","block","turn","summon","ok"]
        ocr = self.btn_txt().lower()
        if ocr == None:
            return None
        for v in btn_values:
            if v in ocr:
                return v
            # time.sleep(self.duration(1))
        return None

    def wait_for_next_state(self):
        pyautogui.moveTo(self.posToGlobal((0,0)))
        self.update_geometry()
        state = State()
        btn = self.get_btn()
        if btn == None:
            state.stage = Stage.Wait
            # logging.info("Waiting")
            time.sleep(0.5)
            return state

        # time.sleep(1)
        ### Status ###
        self.update_status(state)
        logging.info("OCR status: %s", state.to_str())
        ### Cards ###
        self.get_board_cards(state)
        logging.info("Player Army: %s", state.player.army.to_str())
        logging.info("Opponent Army: %s", state.opponent.army.to_str())

        ### Stage ###
        if btn == "round" or btn == "pass":
            state.stage = Stage.Play
        elif btn == "skip" or btn == "block":
            state.stage = Stage.Block
        elif btn == "ok":
            # if self.last_card(spell_arena).owned: ## @TODO determine the cast or counter or validate state from cards
            state.stage = Stage.Cast
            state.stage = Stage.Counter
        else:
            state.stage = Stage.Wait

        # print("State available", state.to_str())
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
        # if not os.path.isfile("capture/" + name + str(number) + ".png"):
        #     src.save("capture/" + name + str(number) + ".png")
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
        # if not os.path.isfile("capture/" + region_name + str(number) + ".png"):
        #     src.save("capture/" + region_name + str(number) + ".png")
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

    def pattern_card_skills(self, card, name, pos):
        rect = LoR_Constants.card_prop_rect(card, "skills", pos, self.Lor_app.width, self.Lor_app.height)
        rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
        region = Region(name, self.desktop_img_dc, rect)
        region.capture(self.mem_dc)
        if region.img == None:
            return -1

        return self.matcher.pattern_detect_skills(region.img)
        
    def pattern_card_number(self, card, name, pos):
        rect = LoR_Constants.card_prop_rect(card, name, pos, self.Lor_app.width, self.Lor_app.height)
        rect = (rect[0] + self.Lor_app.left, rect[1] + self.Lor_app.top, rect[2], rect[3])
        region = Region(name, self.desktop_img_dc, rect)
        region.capture(self.mem_dc)
        if region.img == None:
            return -1

        if name == "cost":
            return self.matcher.pattern_detect_number(region.img, "cost")
        else:
            return self.matcher.pattern_detect_number(region.img, "unit", True)


    def update_card_cor(self, card):
        logging.info("Update card position")
        playable_cards = queries.get_playable_cards()   
        for json_card in playable_cards:
            if card.id == json_card["CardID"]:
                y = self.Lor_app.height - json_card["TopLeftY"]
                x = json_card["TopLeftX"]
                h = json_card["Height"]
                w = json_card["Width"]
                card.rect = (x,y,x+w,y+h)
                card.size = (w,h)
                card.center = (x+int(w/2), y+int(h/2))
                return

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
            elif y < step: 
                state.opponent.army.deployed.append(card)
                card._hp = self.pattern_card_number(card, "hp", "bot")
                card._atk = self.pattern_card_number(card, "atk", "bot")
                # card.detected_skills
            elif y < 2*step: 
                state.opponent.army.pit.append(card)
                card._hp = self.pattern_card_number(card, "hp", "bot")
                card._atk = self.pattern_card_number(card, "atk", "bot")
                # card.detected_skills
            elif y < 3*step: 
                state.spell_arena.append(card)
            elif y < 4*step: 
                state.player.army.pit.append(card)
                if card.type == CardType.Unit:
                    card._hp = self.pattern_card_number(card, "hp", "top")
                    card._atk = self.pattern_card_number(card, "atk", "top")
                    # card.detected_skills
            elif y < 5*step: 
                state.player.army.deployed.append(card)
                card._hp = self.pattern_card_number(card, "hp", "top")
                card._atk = self.pattern_card_number(card, "atk", "top")
                # card.detected_skills
            else: 
                state.player.army.hand.append(card)
                card._cost = self.pattern_card_number(card, "cost", "top")
        
        ## Set challenge and forced oppositions
        for player_card in state.player.army.pit:
            for opp_card in state.opponent.army.pit:
                if player_card.rect[0] == opp_card.rect[0]:
                    player_card.opp = opp_card
                    opp_card.opp = player_card


    def update_status(self, state):
        state.player.mana = self.pattern_pos_number("mana", False)
        state.opponent.mana = self.pattern_pos_number("mana", True)
        state.player.smana = self.pattern_pos_number("smana", False)
        state.opponent.smana = self.pattern_pos_number("smana", True)
        state.player.hp = self.pattern_pos_number("hp", False, True)
        state.opponent.hp = self.pattern_pos_number("hp", True, True)

        if self.detect("token_attack", LoR_Constants.atk_token_rect(self.face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            state.player.token = TokenType.Attack
        elif self.detect("token_scout", LoR_Constants.scout_token_rect(self.face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            state.player.token = TokenType.Scout
        elif self.detect("token_round", LoR_Constants.atk_token_rect(self.face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            state.player.token = TokenType.Round
        else:
            state.player.token = TokenType.Stateless

        if self.detect("token_opp_attack", LoR_Constants.opp_atk_token_rect(self.opp_face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            state.opponent.token = TokenType.Attack
        elif self.detect("token_opp_scout", LoR_Constants.opp_scout_token_rect(self.opp_face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            state.opponent.token = TokenType.Scout
        elif self.detect("token_opp_round", LoR_Constants.opp_atk_token_rect(self.opp_face_card_rect
                                            , self.Lor_app.width, self.Lor_app.height)) != None:
            state.opponent.token = TokenType.Round
        else:
            state.opponent.token = TokenType.Stateless
        
        


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
            self.wait_for_btn()


    def duration(self, sec):
        return  (random.random()-0.5) * sec + sec

    def posToGlobal(self, pos):
        return pos[0] + self.Lor_app.left, pos[1] + self.Lor_app.top

    def invert_Y(self, pos):
        return pos[0], self.Lor_app.height - pos[1]



    # def card_replace_pos(self, card): ###@TODO to put in LOR Constant
    #     pos = queries.get_card_pos(card)
    #     x = self.Lor_app.left + int(pos[0] + card.width/5)
    #     y = self.Lor_app.top + self.Lor_app.height - int(pos[1] - card.height/6)
    #     return x, y


    def click(self, pos = None):
        if pos != None:
            global_pos = self.posToGlobal(pos)
            logging.info("click %i:%i", global_pos[0], global_pos[1])
            pyautogui.moveTo(global_pos[0], global_pos[1], self.duration(0.5), pyautogui.easeInQuad)
        pyautogui.click()
        time.sleep(0.05)



    def mulligan_cards(self, cards):
        for card in cards:
            pos = LoR_Constants.mulligan_button_pos(card, self.Lor_app.height)
            global_pos = self.posToGlobal(pos)
            logging.info("click mulligan %s %i:%i", card.name, global_pos[0], global_pos[1])
            pyautogui.moveTo(global_pos[0], global_pos[1], self.duration(0.5), pyautogui.easeInQuad)
            pyautogui.click()


    def click_next(self):
        pos = LoR_Constants.game_button_pos(self.face_card_rect, self.Lor_app.width, self.Lor_app.height)
        global_pos = self.posToGlobal(pos)
        logging.info("click next %i:%i", global_pos[0], global_pos[1])
        pyautogui.moveTo(global_pos[0], global_pos[1], 0.1, pyautogui.easeInQuad)
        pyautogui.click()
        time.sleep(0.05)
        pyautogui.moveTo(self.posToGlobal((0,0)))

    def card_handle_pos(self, card):
        # print(card)
        x,y = LoR_Constants.card_hdl_pos(card, self.Lor_app.height)
        # print(x,y)
        return self.posToGlobal((x,y))

    
    def click_card(self, card):
        self.click(self.card_handle_pos(card))
        time.sleep(0.05)
    
    def drag_to_center(self, card):
        logging.info("Drag %s to center", card.name)
        self.update_card_cor(card)
        x, y = self.card_handle_pos(card)
        # print("card handle",x,y)
        center_x, center_y = self.Lor_app.center()
        pyautogui.moveTo(x, y, 0.2, pyautogui.easeInQuad)
        pyautogui.dragTo(center_x, center_y, 0.3)
        time.sleep(0.9)

    def drag_to_card(self, card, target):
        logging.info("Drag %s to %s", card.name, target.name)
        self.update_card_cor(card)
        self.update_card_cor(target)
        x, y = self.card_handle_pos(card)
        destx, desty = self.card_handle_pos(target)
        center_x, center_y = self.Lor_app.center()
        pyautogui.moveTo(center_x, center_y, 0.2, pyautogui.easeInQuad)
        pyautogui.moveTo(x, y, 0.3, pyautogui.easeInQuad)
        pyautogui.dragTo(destx, desty, 0.3)
        time.sleep(1.3)

    # def drag_to_block(self, block):
    #     logging.info("Drag %s to %s", block[0]["name"], block[1]["name"])
    #     x, y = self.card_handle_pos(block[0])
    #     destx, desty = self.card_handle_pos(block[1])
    #     center_x, center_y = self.Lor_app.center()
    #     pyautogui.moveTo(center_x, center_y, 0.2, pyautogui.easeInQuad)
    #     pyautogui.moveTo(x, y, 0.3, pyautogui.easeInQuad)
    #     pyautogui.dragTo(destx, desty, 0.2)


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
        # if name == "Mulligan":
        #     source.img.show()
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
            pass
            # print(name, "not detected")
            logging.info("%s not detected", name)
        return pos




    def wait_n_click_img(self, btn_names, click = True, sleep_duration = 3):
        logging.info("Waiting images %s" + "for click" if click else "", " - ".join(btn_names))
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
                            # logging.info("reseting index of detection")
                            # index = max(0, index-1)
                            # logging.info("clicking last detected position")
                            print("clicking last detected position")
                            self.click(last_detected_pos)
                else:
                    logging.info("Clicking %s", name)
                    # print("Clicking %s", name)
                    btn_names.pop(0)
                    last_detected_pos = detected_pos
                    self.click(detected_pos)
                    time.sleep(0.5)

            time.sleep(1)
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

