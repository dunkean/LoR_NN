from tesserocr import PyTessBaseAPI, PSM, OEM
from string import digits, ascii_letters
from PIL import Image, ImageOps

import logging
import os

class OCR():
    ocr_api = None

    def __init__(self):
        self.reset()

    def __del__(self):
        del self.ocr_api
    
    def reset(self):
        self.ocr_api = PyTessBaseAPI(oem = OEM.TESSERACT_ONLY)

        
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

    def filter_img(self, im):
        if im == None:
            return im
        # im = ImageOps.grayscale(im)
        # im = im.filter(ImageFilter.GaussianBlur(4))
        # im = ImageOps.invert(im)
        return im

    def ocr_txt(self, img):
        im = self.ocr_filter_img(img)
        self.ocr_api.SetPageSegMode(PSM.SINGLE_BLOCK)
        self.ocr_api.SetVariable('tessedit_char_whitelist', ascii_letters)
        self.ocr_api.SetVariable('tessedit_char_blacklist', digits)
        self.ocr_api.SetImage(im)
        text = self.ocr_api.GetUTF8Text().strip('\n')
        # logging.info("Btn text detected as %s", text)
        return text.lower()


    def ocr_number(self,img):
        im = self.ocr_filter_img(img)
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

