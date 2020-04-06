# import json

# import win32gui, win32ui, win32con, win32api
# from ctypes import windll
# import requests
# from PIL import Image, ImageOps, ImageEnhance
# import tesserocr
# from tesserocr import PyTessBaseAPI, PSM, OEM
# import pytesseract
# import cv2
# import io
# import numpy as np
# import pyautogui
# import time
# import os
# import subprocess
# import sys
# from string import digits, ascii_letters
# from dataclasses import dataclass


# @dataclass
# class Region:
#     local_left: int
#     local_right: int
#     local_top: int
#     local_bot: int
#     left: int
#     right: int
#     top: int
#     bot: int
#     width: int
#     height: int
    

# class LoR:
#     cards_dict = {}
#     hwnd = None
#     screen: Region
#     client_rect = (0,0,0,0)
#     client_size = (0,0)
#     client_offset = (0,0)
#     board_data = None
#     face_card = None
#     opp_face_card = None
#     atk_token_img = None
#     opp_atk_token_img = None
#     last_capture = None
#     ocr_api = None
#     original_capture = None

#     def __init__(self):
#         self.load_db()
#         self.hwnd = win32gui.FindWindow(None, 'Legends of Runeterra')
#         if self.hwnd == 0:
#             return
#         self.update_geometry()
#         self.atk_token_img = np.array(Image.open("atk.png").convert('L'))
#         self.opp_atk_token_img = np.array(Image.open("opp_atk.png").convert('L'))
#         self.ocr_api = PyTessBaseAPI(oem = OEM.TESSERACT_ONLY)
    
#     def clean(self):
#         self.board_data = None
#         self.face_card = None
#         self.opp_face_card = None
#         self.last_capture = None


#     def load_db(self):
#         with open('set1-en_us.json', encoding="utf8") as json_file:
#             for p in  json.load(json_file):
#                 self.cards_dict[p["cardCode"]] = p
    
#     def update_geometry(self):
#         hdesktop = win32gui.GetDesktopWindow()
#         _, dt, _, db = win32gui.GetClientRect(hdesktop)
#         wl, wt, wr, wb = win32gui.GetWindowRect(self.hwnd)
#         cl, ct, cr, cb = win32gui.GetClientRect(self.hwnd)
#         w_head = (win32api.GetSystemMetrics(win32con.SM_CYFRAME) + win32api.GetSystemMetrics(win32con.SM_CYCAPTION) + win32api.GetSystemMetrics(92))
#         w_bord = win32api.GetSystemMetrics(win32con.SM_CXSIZEFRAME)
#         dh = dt - db
#         ch = ct - cb
#         if dh == ch:
#             w_head = 0
#             w_bord = 0
#         self.client_offset = (w_bord, w_head)
#         self.client_rect = (wl + w_bord, wt + w_head, wr - w_bord, wb - w_bord)
#         self.client_size = (cr - cl, cb - ct)
    
#     def capture(self, rect = None, save_name = None): ##TODO capture only required rect
#         self.update_geometry()
#         # hwndDC = win32gui.GetWindowDC(self.hwnd)
#         # mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
#         # saveDC = mfcDC.CreateCompatibleDC()
#         # saveBitMap = win32ui.CreateBitmap()
#         # if rect != None:
#         #     saveBitMap.CreateCompatibleBitmap(mfcDC, rect[2] - rect[0], rect[3] - rect[1])
#         #     saveDC.SelectObject(saveBitMap)
#         #     saveDC.BitBlt((0,0), (rect[2] - rect[0], rect[3] - rect[1]), mfcDC, (rect[0] + self.client_offset[0], rect[1] + self.client_offset[1]), win32con.SRCCOPY)
#         # else:
#         #     saveBitMap.CreateCompatibleBitmap(mfcDC, self.client_size[0], self.client_size[1])
#         #     saveDC.SelectObject(saveBitMap)
#         #     saveDC.BitBlt((0,0), (self.client_size[0], self.client_size[1]), mfcDC, (self.client_offset[0], self.client_offset[1]), win32con.SRCCOPY)

#         # bmpinfo = saveBitMap.GetInfo()
#         # bmpstr = saveBitMap.GetBitmapBits(True)
#         # im = Image.frombuffer(
#         #     'RGB',
#         #     (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
#         #     bmpstr, 'raw', 'BGRX', 0, 1)
#         im = pyautogui.screenshot()
#         self.original_capture = pyautogui.screenshot()
#         im = ImageOps.grayscale(im)
#         im = ImageOps.invert(im)
#         # im.show()
#         if save_name != None:
#             im.save(save_name + ".png")
#         self.last_capture = im


#     def is_detected(self, pattern, rect = None):
#         perfect_scale = self.client_size[1] / 1080  #token shot at 1920*1080
#         im = None
#         if rect != None:
#             im = self.last_capture.crop(rect)
#         cv_im = np.array(im.convert('L'))
#         centers = []
#         rects =[]
#         detected = False
#         for i in range(-5, 5, 1):
#             scale = i/100 + perfect_scale
#             width = int(pattern.shape[1] * scale)
#             height = int(pattern.shape[0] * scale)
#             pattern_scaled = cv2.resize(pattern, (width, height))
#             res = cv2.matchTemplate(cv_im, pattern_scaled, cv2.TM_CCOEFF_NORMED)
#             _, max_val, _, _ = cv2.minMaxLoc(res)
#             if (max_val > 0.8):
#                 detected = True
#                 loc = np.where( res >= 0.8)
#                 for pt in zip(*loc[::-1]):
#                     centers.append((pt[0] + int(width/2), pt[1] + int(height/2)))
#                     rects.append((pt[0], pt[1], pt[0] + width, pt[1] + height))
#                 break
#         return detected, rects, centers

#     def get_positional_rectangles(self):
#         url = "http://127.0.0.1:21337/positional-rectangles"
#         r = requests.get(url = url) 
#         self.board_data = r.json()
#         for card in self.board_data["Rectangles"]:
#             code = card["CardCode"]
#             if code == "face":
#                 if card["LocalPlayer"] == True:
#                    self.face_card = card
#                 else:
#                     self.opp_face_card = card
    
#     def atk_token_rect(self, face_card, opp = False):
#         if(opp == True):
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.8*face_card["Width"]), 
#                     self.client_size[1]/2 - 2*face_card["Height"],
#                     self.client_size[0] - face_card["TopLeftX"],
#                     self.client_size[1]/2 - face_card["Height"] )
#         else:
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.8*face_card["Width"]), 
#                     self.client_size[1]/2 + face_card["Height"],
#                     self.client_size[0] - face_card["TopLeftX"],
#                     self.client_size[1]/2 + 2.5*face_card["Height"])

#     def hp_rect(self, face_card):
#         return (face_card["TopLeftX"]+ 0.90*face_card["Width"], 
#             self.client_size[1]-face_card["TopLeftY"]+0.2*face_card["Height"], 
#             face_card["TopLeftX"] + 1.4*face_card["Width"],
#             self.client_size[1]-face_card["TopLeftY"]+face_card["Height"])

#     def mana_rect(self, face_card, opp = False):
#         if(opp == True):
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.3*face_card["Width"]), 
#                     self.client_size[1]/2 - 1.25*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.98*face_card["Width"]),
#                     self.client_size[1]/2 - 0.85*face_card["Height"] )
#         else:
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.30*face_card["Width"]), 
#                     self.client_size[1]/2 + 0.80*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.98*face_card["Width"]),
#                     self.client_size[1]/2 + 1.2*face_card["Height"])

#     def smana_rect(self, face_card, opp = False):
#         if(opp == True):
#             return (self.client_size[0] - (face_card["TopLeftX"]+0.88*face_card["Width"]), 
#                     self.client_size[1]/2 - 1.50*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.63*face_card["Width"]),
#                     self.client_size[1]/2 - 1.25*face_card["Height"] )
#         else:
#             return (self.client_size[0] - (face_card["TopLeftX"]+0.88*face_card["Width"]), 
#                     self.client_size[1]/2 + 1.25*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.63*face_card["Width"]),
#                     self.client_size[1]/2 + 1.50*face_card["Height"])


    

#     def card_cor(self, card):
#         local_x = int(card["TopLeftX"] + card["Width"]/2)
#         local_y = self.client_size[1] - card["TopLeftY"] + 20
#         return local_x + self.client_rect[0], local_y + self.client_rect[1]
    
#     def card_rect(self, card):
#         local_x = card["TopLeftX"]
#         local_y = self.client_size[1] - card["TopLeftY"]
#         h =  card["Height"]
#         w = card["Width"]
#         return local_x + self.client_rect[0], local_y + self.client_rect[1], local_x + self.client_rect[0] + w, local_y + self.client_rect[1] + h, w, h

#     def local_card_rect(self, card):
#         local_x = card["TopLeftX"]
#         local_y = self.client_size[1] - card["TopLeftY"]
#         h =  card["Height"]
#         w = card["Width"]
#         return local_x, local_y, local_x + w, local_y + h, w, h

#     def rect_cor(self, rect):
#         local_x = int((rect[0]+rect[2]) / 2)
#         local_y = int((rect[1]+rect[3]) / 2)
#         return local_x + self.client_rect[0], local_y + self.client_rect[1]

#     def center(self):
#         return int((self.client_rect[2]+self.client_rect[0])/2), int((self.client_rect[1]+self.client_rect[3])/2)

#     #   0 = Orientation and script detection (OSD) only.
#     #   1 = Automatic page segmentation with OSD.
#     #   2 = Automatic page segmentation, but no OSD, or OCR
#     #   3 = Fully automatic page segmentation, but no OSD. (Default)
#     #   4 = Assume a single column of text of variable sizes.
#     #   5 = Assume a single uniform block of vertically aligned text.
#     #   6 = Assume a single uniform block of text.
#     #   7 = Treat the image as a single text line.
#     #   8 = Treat the image as a single word.
#     #   9 = Treat the image as a single word in a circle.
#     #   10 = Treat the image as a single character.
#     def ocr(self, rect, option, intensity, show = False):
#         im = self.last_capture.crop(rect)
#         enhancer = ImageEnhance.Brightness(im)
#         im = enhancer.enhance(intensity)
#         if show == True:
#             im.show()
#         # text = pytesseract.image_to_string(im, config="--psm " + str(option) + " -c tessedit_char_whitelist=0123456789")
#         self.ocr_api.SetVariable('tessedit_char_whitelist', digits)
#         self.ocr_api.SetVariable('tessedit_char_blacklist', ascii_letters)
#         self.ocr_api.SetPageSegMode(PSM.SINGLE_WORD)
#         self.ocr_api.SetImage(im)
#         text = self.ocr_api.GetUTF8Text().strip('\n')
#         return text

#     def ocr_txt(self, rect, option, intensity, show = False):
#         im = self.last_capture.crop(rect)
#         enhancer = ImageEnhance.Brightness(im)
#         im = enhancer.enhance(intensity)
#         if show == True:
#             im.show()
#         # text = pytesseract.image_to_string(im, config="--psm " + str(option))
#         self.ocr_api.SetPageSegMode(PSM.SINGLE_BLOCK)
#         self.ocr_api.SetVariable('tessedit_char_whitelist', ascii_letters)
#         self.ocr_api.SetVariable('tessedit_char_blacklist', digits)
#         self.ocr_api.SetImage(im)
#         text = self.ocr_api.GetUTF8Text().strip('\n')
#         return text

#     def get_numerical_values(self):
#         hp = self.ocr(self.hp_rect(self.face_card), 8, 6)
#         opp_hp = self.ocr(self.hp_rect(self.opp_face_card), 8, 6)
#         mana = self.ocr(self.mana_rect(self.face_card), 8, 3)
#         opp_mana = self.ocr(self.mana_rect(self.opp_face_card, True), 8, 3)
#         smana = self.ocr(self.smana_rect(self.face_card), 10, 4)
#         opp_smana = self.ocr(self.smana_rect(self.opp_face_card, True), 10, 4)
#         btn = self.ocr_txt(self.btn_rect(self.face_card), 6, 2)
#         # #print(hp, mana, smana, "---", opp_hp, opp_mana, opp_smana)
#         return hp, mana, smana, opp_hp, opp_mana, opp_smana, btn

#     def get_cards_state(self):
#         hand = []
#         opp_hand = []
#         board = []
#         pit = []
#         cast = []
#         opp_pit = []
#         opp_board = []
#         mulligan = []
#         step = self.client_size[1] / 6

#         for card in self.board_data["Rectangles"]:
#             if card["CardCode"] == "face":
#                 continue
#             card.update(self.cards_dict[card["CardCode"]])
#             # #print(self.cards_dict[card["CardCode"]]["name"], card["TopLeftY"])
#             y = self.client_size[1] - card["TopLeftY"]
#             if y < 0: opp_hand.append(card)
#             elif y < step: opp_board.append(card)
#             elif y < 2*step: 
#                 if(card["LocalPlayer"] == True):
#                     mulligan.append(card)
#                 else:
#                     opp_pit.append(card)
#             elif y <  self.client_size[1] - self.opp_face_card["TopLeftY"]:
#                 if(card["LocalPlayer"] == True):
#                     mulligan.append(card)
#             elif y < 3*step: 
#                 cast.append(card)
#                 # #print(y)
#             elif y < 4*step: pit.append(card)
#             elif y < 5*step: board.append(card)
#             else: hand.append(card)

#         hand = sorted(hand, key=lambda x: x["TopLeftX"])
#         opp_hand = sorted(opp_hand, key=lambda x: x["TopLeftX"])
#         board = sorted(board, key=lambda x: x["TopLeftX"])
#         opp_board = sorted(opp_board, key=lambda x: x["TopLeftX"])
#         pit = sorted(pit, key=lambda x: x["TopLeftX"])
#         opp_pit = sorted(opp_pit, key=lambda x: x["TopLeftX"])
#         cast = sorted(cast, key=lambda x: x["TopLeftX"])
#         mulligan = sorted(mulligan, key=lambda x: x["TopLeftX"])
#         return hand, opp_hand, board, opp_board, pit, opp_pit, cast, mulligan

    
#     def get_stage(self, btn, cast, mulligan):
#         a = btn.lower()
#         if "round" in a or "pass" in a: #"END_ROUND" #PASS
#             return "PLAYTIME"

#         if "skip" in a: # SKIP BLOCK
#             return "BLOCKTIME"

#         if "select" in a:
#             return "CHOOSE_WISELY"

#         if "attack" in a or "block" in a: ## should not happens coz its a validation #BLOCK #ATTACK
#             return "PUSH_NEXT"
     
#         if "ok" in a and len(cast) > 0 and cast[0]["LocalPlayer"] == True: ## own cast validation Should not happen
#             return "PUSH_NEXT"

#         if "ok" in a and (len(cast) == 0 or cast[0]["LocalPlayer"] == True):
#             return "REACT"
        
#         if "turn" in a or "onent" in a:
#             return "OPPONENT_PLAYING"
        
#         return "UNKNOWN_STATE"

#     def get_atk_tokens(self):
#         me, _, _ = self.is_detected(self.atk_token_img, self.atk_token_rect(self.face_card, False) )
#         opp, _, _ = self.is_detected(self.opp_atk_token_img, self.atk_token_rect(self.face_card, True) )
#         return me, opp

#     def update_attack_life(self, line, top = False):
#         for card in line:
#             im = self.original_capture
#             r,g,b = im.split()
#             self.last_capture = ImageOps.invert(r)

#             l, t, _, b, w, h = self.local_card_rect(card)
#             lrect = (0,0,0,0)
#             rrect = (0,0,0,0)
#             if top == False:
#                 lrect = (l+int(w/2-h/4) , b-int(h/4) , l+int(w/2-h/20) , b-int(h/30))
#                 rrect = (l+int(w/2+h/20) , b-int(h/4) , l+int(w/2+h/20+h/4) , b-int(h/30))
#             else:
#                 lrect = (l+int(w/2-h/4) , t+int(h/20) , l+int(w/2-int(h/20)) , t+int(h/20+h/5))
#                 rrect = (l+int(w/2+h/20) ,  t+int(h/20) , l+int(w/2+h/20+h/4) , t+int(h/20+h/5))
#             atk = self.ocr(lrect, 10, 4)
#             hp = self.ocr(rrect, 10, 2)
#             # if hp == "":
#             #     im = self.original_capture
#             #     r,g,b = im.split()
#             #     # r.show()
#             #     # g.show()
#             #     # b.show()
#             #     im = ImageOps.invert(im)
#             #     enhancer = ImageEnhance.Brightness(im)
#             #     im = enhancer.enhance(4)
#             #     im = ImageOps.grayscale(im)
#             #     enhancer = ImageEnhance.Brightness(im)
#             #     im = enhancer.enhance(1)
#             #     im = ImageOps.posterize(im, 3)
#             #     self.last_capture = ImageOps.invert(r)
#             #     t = im.crop(rrect)
#             #     im.show()
#             #     #print("Retry:", self.ocr(rrect, 10, 2))
#             #     # im.show()
#             #print(card["name"], hp)
#             card["atk"] = atk
#             card["hp"] = hp
#             # #print(card["name"],atk, hp, l, t, w, h)

#     def get_state(self):
#         self.update_geometry()
#         #print("before capture")
#         self.capture()
#         #print("before http query")
#         self.get_positional_rectangles()
#         if(len(self.board_data["Rectangles"]) == 0):
#             return None
#         if(self.face_card == None or self.opp_face_card == None):
#             return None
#         # #print(self.board_data)
#         #print("before tokens match")
#         atk_token, opp_atk_token = self.get_atk_tokens()
#         #print("before numericals ocr")
#         hp, mana, smana, opp_hp, opp_mana, opp_smana, btn = self.get_numerical_values()
#         #print("before cards positioning")
#         hand, opp_hand, board, opp_board, pit, opp_pit, cast, mulligan = self.get_cards_state()
#         #print("before cards update ocr") 
#         self.update_attack_life(opp_board, False)
#         self.update_attack_life(opp_pit, False)
#         self.update_attack_life(pit, True)
#         self.update_attack_life(board, True)

#         stage = self.get_stage(btn, cast, mulligan)# + "-" + btn
#         #print("END")
#         return {"hand":hand,
#                 "opp_hand":opp_hand,
#                 "board":board,
#                 "opp_board":opp_board,
#                 "pit":pit,
#                 "opp_pit":opp_pit,
#                 "cast":cast,
#                 "hp":hp,
#                 "mana":mana,
#                 "smana":smana,
#                 "opp_hp":opp_hp,
#                 "opp_mana":opp_mana,
#                 "opp_smana":opp_smana,
#                 "mulligan":mulligan,
#                 "stage":stage,
#                 "atk_token": atk_token,
#                 "opp_atk_token": opp_atk_token,
#                 "btn": btn
#                 }



#     def next(self):
#         x, y = self.rect_cor(self.btn_rect(self.face_card))
#         pyautogui.moveTo(x, y, 0.1, pyautogui.easeInQuad)
#         pyautogui.click()
#         # self.get_out()

#     def get_out(self):
#         pyautogui.move(self.client_rect[0], self.client_rect[1])
    
#     def cast(self, card, target1=None, target2=None):
#         # #print("CASTING", card["name"])
#         x, y = self.card_cor(card)
#         destx, desty = self.center()
#         pyautogui.moveTo(x, y, 0.1, pyautogui.easeInQuad)
#         pyautogui.dragTo(destx, desty, 0.3)
#         # self.get_out()

#     def attack(self, card, blocker=None):
#         x, y = self.card_cor(card)
#         destx, desty = self.center()
#         pyautogui.moveTo(x, y, 0.1, pyautogui.easeInQuad)
#         pyautogui.dragTo(destx, desty, 0.3)
#         # self.get_out()

#     def block(self, blocker, attacker):
#         x, y = self.card_cor(blocker)
#         destx, desty = self.card_cor(attacker)
#         pyautogui.moveTo(x, y, 0.5, pyautogui.easeInQuad)
#         pyautogui.dragTo(destx, desty, 0.3)
#         # self.get_out()

#     def click(self, cor):
#         pyautogui.moveTo(cor[0] + self.client_rect[0], cor[1] + self.client_rect[1], 0.5, pyautogui.easeInQuad)
#         # pyautogui.click()
#         time.sleep(0.05)
#         pyautogui.mouseDown()
#         time.sleep(0.05)
#         pyautogui.mouseUp()

#     def is_deck_selection(self):
#         self.get_positional_rectangles()
#         if self.board_data["GameState"] == "Menus":
#             return True
#         return False

#     def get_last_game(self):
#         url = "http://127.0.0.1:21337/game-result"
#         r = requests.get(url = url) 
#         data = r.json()
#         return data["GameID"], data["LocalPlayerWon"]

#     def wait_for_btn(self, button_state, tries = 30):
#         detected = False
#         counter = 0
#         # while detected == False:
#         #     rect = 
#         btn = self.ocr_txt(self.btn_rect(self.face_card), 6, 2)

#         btn_im = Image.open(btn_name + ".png")
#         pattern = np.array(btn_im.convert('L'))
#         self.update_geometry()
#         self.capture()
#         detected, _, _ = self.is_detected(pattern)
#         counter = 0
        
#             # if(counter > tries):
#             #     return False
#             # time.sleep(0.5)
#             # self.update_geometry()
#             # self.capture()
#             # detected, _, _ = self.is_detected(pattern)
#             # counter = counter + 1
#         return True

#     def wait_and_click(self, btn_names, tries = 5):
#         for i in range(len(btn_names)):
#             btn_name = btn_names[i]
#             btn_im = Image.open(btn_name + ".png")
#             pattern = np.array(btn_im.convert('L'))
#             self.update_geometry()
#             self.capture()
#             detected, _, centers = self.is_detected(pattern)
#             counter = 0
#             not_found = False
#             while detected == False:
#                 if(counter > tries):
#                     if i > 0:
#                         self.wait_and_click([btn_names[i-1]])
#                     else:
#                         pyautogui.mouseDown()
#                         time.sleep(0.05)
#                         pyautogui.mouseUp()
#                     counter = 0
#                 time.sleep(0.5)
#                 # #print("Searching for", btn_name)
#                 self.update_geometry()
#                 self.capture()
#                 detected, _, centers = self.is_detected(pattern)
#                 counter = counter + 1

#             if not_found == False:
#                 # #print("Clicking", btn_name)
#                 self.click(centers[0])
#             time.sleep(0.2)
#             ## wait to disappear (useless and buggy)
#             # detected, rect, center = self.is_detected(pattern, rect)
#             # while detected == True:
#             #     time.sleep(0.5)
#             #     detected, rect, center = self.is_detected(pattern, rect)



# ########### OUT OF GAME #####################
# def is_game_running():
#     url = "http://127.0.0.1:21337/positional-rectangles"
#     try:
#         requests.get(url = url)
#         return True
#     except:
#         return False
#     return False

# def launch_game():
#     #print("Launching")
#     hwnd = win32gui.FindWindow(None, 'Legends of Runeterra')
#     if hwnd == 0:
#         subprocess.Popen('"C:\\Riot Games\\Riot Client\\RiotClientServices.exe" --launch-product=bacon --launch-patchline=live', shell=True) 
#     #print("App launched")