import logging
import numpy as np
from PIL import Image, ImageOps
import cv2
import imutils

class Matcher:
    scaled_patterns = {}
    source_patterns = {}
    v_scale = None

    def __init__(self, v_scale):
        self.v_scale = v_scale
        self.register_number_patterns()
        self.register_img_patterns()
    
    def register_pattern(self, name, canny = False):
        if name not in self.source_patterns:
            logging.info("Adding pattern %s in sources", name)
            image = cv2.imread("assets/" + name + ".png")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.source_patterns[name] = gray

        if name not in self.scaled_patterns:
            logging.info("Adding pattern %s in patterns", name)
            pattern_cv_img = self.source_patterns[name]
            width = int(pattern_cv_img.shape[1] * self.v_scale)
            height = int(pattern_cv_img.shape[0] * self.v_scale)
            # pattern_cv_img = cv2.resize(pattern_cv_img, (width, height))
            if canny:
                pattern_cv_img = cv2.Canny(pattern_cv_img, 50, 200)
            self.scaled_patterns[name] = pattern_cv_img

    def register_img_patterns(self):
        list_btn = ["Play", "vsAI", "Friends", "Spare", "Challenge", "Accept", "Play", "vsAI", "Continue", "Ready", "Mulligan"]
        for btn in list_btn:
            self.register_pattern(btn)
    
    def register_number_patterns(self):
        for i in range(0,10):
            self.register_pattern("hp" + str(i), True)
        
        for i in range(0,11):
            self.register_pattern("mana" + str(i), True)
        
        for i in range(0,4):
            self.register_pattern("smana" + str(i), True)

   
    def pattern_detect_number(self, img, name, double_digit = False):
        interval = None
        precision = 0.7
        if "hp" in name:
            interval = range(9,-1,-1)
            precision = 0.6
        elif "smana" in name:
            interval = range(0,4)
            precision = 0.8
        elif "mana" in name:
            interval = range(10,-1,-1)
            precision = 0.7

        img = np.array(img.convert('L'))
        scale = 1/self.v_scale
        img = imutils.resize(img, width = int(img.shape[1] * scale))
        edged = cv2.Canny(img, 50, 200)

        result = []
        for number in interval:
            found, locs = self.match_number(edged, self.scaled_patterns[name + str(number)], precision)
            if found:
                if double_digit:
                    for loc in locs:
                        result.append((loc, number))
                else:
                    return number

        if double_digit and len(result) > 0:
            result.sort()
            str_number = ''.join([str(c[1]) for c in result])
            return int(str_number)
        return -1

    def match_number(self, edged, template, precision):
        result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, max_loc) = cv2.minMaxLoc(result)
        match_locations = np.where(result>precision)
        xs = []
        for pt in zip(*match_locations[::-1]):
            if pt[0] not in xs:
                xs.append(pt[0])

        if maxVal > precision :
            return True, xs
        return False, (-1,-1)

    

    # def match_pattern_number(self, im, name):
    #     # im.save("Capture.png")
    #     cv_im = np.array(im.convert('L'))
    #     pattern_cv_img = self.patterns[name]
    #     width = pattern_cv_img.shape[1]
    #     height = pattern_cv_img.shape[0]
    #     res = cv2.matchTemplate(cv_im, pattern_cv_img, cv2.TM_CCOEFF_NORMED)
    #     _, max_val, _, max_loc = cv2.minMaxLoc(res)
    #     if (max_val > 0.8):
    #         logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
    #         return (max_loc[0], max_loc[1], width, height)

    #     pattern_cv_img = self.source_patterns[name]
    #     logging.info("Attempting scaling for detection")
    #     for i in range(-5, 5, 1):
    #         scale = i/100 + self.v_scale
    #         width = int(pattern_cv_img.shape[1] * scale)
    #         height = int(pattern_cv_img.shape[0] * scale)
    #         pattern_scaled = cv2.resize(pattern_cv_img, (width, height))
    #         res = cv2.matchTemplate(cv_im, pattern_scaled, cv2.TM_CCOEFF_NORMED)
    #         _, max_val, _, max_loc = cv2.minMaxLoc(res)
    #         if (max_val > 0.9):
    #             logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
    #             return (max_loc[0], max_loc[1], width, height)
    #     return None

    def match_pattern(self, img, name):
        im = ImageOps.grayscale(img)
        im = ImageOps.invert(im)
        # im.save("Capture.png")
        cv_im = np.array(im.convert('L'))
        pattern_cv_img = self.scaled_patterns[name]
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

    
        


