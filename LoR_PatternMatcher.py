import logging
import numpy as np
from PIL import Image, ImageOps
import cv2
import imutils

### barrier pixel leftx/centery = 255 242 90

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
            # logging.info("Adding pattern %s in sources", name)
            image = cv2.imread("assets/" + name + ".png")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.source_patterns[name] = gray

        if name not in self.scaled_patterns:
            # logging.info("Adding pattern %s in patterns", name)
            pattern_cv_img = self.source_patterns[name]
            width = int(pattern_cv_img.shape[1] * self.v_scale)
            height = int(pattern_cv_img.shape[0] * self.v_scale)
            pattern_cv_img = cv2.resize(pattern_cv_img, (width, height))
            # if canny:
            #     pattern_cv_img = cv2.Canny(pattern_cv_img, 20, 150)
            self.scaled_patterns[name] = pattern_cv_img

    def register_img_patterns(self):
        list_btn = ["Play", "vsAI", "Friends", "Spare", "Challenge", "Accept", "Play", "vsAI", "Versus", "Replay", "Continue", "Ready", "Mulligan"]
        for btn in list_btn:
            self.register_pattern(btn)

        list_objects = ["token_attack", "token_opp_attack", "token_scout", "token_opp_scout", "token_round", "token_opp_round"]
        for obj in list_objects:
            self.register_pattern(obj)
    
    def register_number_patterns(self):
        for i in range(0,10):
            self.register_pattern("hp" + str(i), True)
        self.register_pattern("hp2b", True)
        
        for i in range(0,11):
            self.register_pattern("mana" + str(i), True)

        for i in range(0,10):
            self.register_pattern("unit" + str(i), True)
        
        for i in range(0,4):
            self.register_pattern("smana" + str(i), True)

        for i in range(0,13):
            self.register_pattern("cost" + str(i), True)

   
    def ocr_filter_img(self, im):
        if im == None:
            return im
        dat = im.getdata()
        f = []
        for d in dat:
            if d[0] >= 254 and d[1] >= 254 and d[2] >= 254: #chp catk
                f.append((255,255,255))
            elif d[0] <= 28 and d[1] == 255 and d[2] <= 80: #chp catk boost
                f.append((255,255,255))
            elif d[0] == 255 and d[1] <=2 and d[2] <=2: #chp catk malus
                f.append((255,255,255))
            # elif d[0] <= 179 and d[0] >= 164 and d[1] <= 230 and d[1] >= 211 and d[2] >= 233: #smana
            #     f.append((255,255,255))
            # elif d[0] <= 205 and d[0] >= 175 and d[1] <= 220 and d[1] >= 190 and d[2] <= 235 and d[2] >= 215: #mana
            #     f.append((255,255,255))
            # elif d[0] == 245 and d[1] == 245 and d[2] == 250: #hp
            #     f.append((255,255,255))
            # elif d[0] == 246 and d[1] == 227 and d[2] == 227: #card cost
            #     f.append((255,255,255))
            else:
                f.append(d)
        im.putdata(f)
        # im = ImageOps.grayscale(im)
        # im = im.filter(ImageFilter.GaussianBlur(4))
        # im = ImageOps.invert(im)
        return im

    def pattern_detect_number(self, img, name, double_digit = False):
        interval = None
        precision = 0.7
        display = False
        if "hp" in name:
            interval = range(9,-1,-1)
            precision = 0.85
        elif "unit" in name:
            interval = range(9,-1,-1)
            precision = 0.7
            # display = True
        elif "smana" in name:
            interval = range(0,4)
            precision = 0.85
        elif "mana" in name:
            interval = range(10,-1,-1)
            precision = 0.85
        elif "cost" in name:
            interval = range(12,-1,-1)
            precision = 0.85

        img = self.ocr_filter_img(img)
        img = np.array(img.convert('L'))
        # scale = 1/self.v_scale
        # img = imutils.resize(img, width = int(img.shape[1] * scale))
        # edged = cv2.Canny(img, 20, 150)
        # cv2.imshow("Visualize", img)
        # cv2.waitKey(0)
        edged = img
        result = []
        for number in interval:
            found, locs = self.match_number(edged, self.scaled_patterns[name + str(number)], precision, display)
            if found:
                if double_digit:
                    for loc in locs:
                        result.append((loc[0], loc[1], number))
                else:
                    return number

            ################################     HACK     ######################################
            ## hp decimal "2" and numeral "2" are different @TODO remove this hack by finding homogeneous "2"
            if number == 2 and name == "hp":            
                found, locs = self.match_number(edged, self.scaled_patterns[name + str(number) + "b"], precision)
                if found:
                    if double_digit:
                        for loc in locs:
                            result.append((loc[0], loc[1], number))
                    else:
                        return number
            ####################################################################################

        if double_digit and len(result) > 0:
            result.sort()
            ### remove close x different values
            final_nb = []
            last_d = (999999, 0, -1)
            for d in result:
                if abs(last_d[0] - d[0]) > 8:
                    if not last_d[0] == 999999:
                        final_nb.append(last_d[2])
                    last_d = d
                elif d[1] > last_d[1]:
                    last_d = d

            if not last_d[0] == 9999999:
                final_nb.append(last_d[2])
            str_number = ''.join([str(c) for c in final_nb])
            return int(str_number)
        return -1


    def match_number(self, edged, template, precision, display = False):
        result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, max_loc) = cv2.minMaxLoc(result)
        match_locations = np.where(result>precision)
        
        detected = []
        for i in range(len(match_locations[0])):
            x = match_locations[0][i]
            y = match_locations[1][i]
            score = result[x][y]
            detected.append((x,y,score))
        
        ### remove close x values
        detected.sort()
        fxs = []
        last_x = 9999999
        for d in detected:
            x = d[1]
            score = d[2]
            if abs(last_x - x) > 8:
                if not last_x == 9999999:
                    fxs.append((last_x,score))
                last_x = x
        if not last_x == 9999999:
            fxs.append((last_x,score))
       
        if maxVal > precision :
            return True, fxs

        # for scale in np.linspace(1.1, 0.9, 10)[::-1]:
        #     edged = imutils.resize(edged, width = int(edged.shape[1] * scale))
        #     if edged.shape[0] <= template.shape[0] or edged.shape[1] <= template.shape[1]:
        #         break

        #     result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF_NORMED)
        #     (_, maxVal, _, max_loc) = cv2.minMaxLoc(result)
        #     match_locations = np.where(result>precision)

        #     if maxVal > precision :
        #         return True, xs

        return False, (-1,-1)

    
    def pattern_detect_skills(self, im):
        # img = self.ocr_filter_img(img)
        # img = np.array(img.convert('L'))
        return []


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
        # if "token_round" in name:
        #     im.save("Capture.png")
        cv_im = np.array(im.convert('L'))
        pattern_cv_img = self.scaled_patterns[name]
        width = pattern_cv_img.shape[1]
        height = pattern_cv_img.shape[0]
        res = cv2.matchTemplate(cv_im, pattern_cv_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        if (max_val > 0.85):
            # logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
            return (max_loc[0], max_loc[1], width, height)

        pattern_cv_img = self.source_patterns[name]
        # logging.info("Attempting scaling for detection")
        for i in range(-5, 5, 1):
            scale = i/100 + self.v_scale
            width = int(pattern_cv_img.shape[1] * scale)
            height = int(pattern_cv_img.shape[0] * scale)
            pattern_scaled = cv2.resize(pattern_cv_img, (width, height))
            res = cv2.matchTemplate(cv_im, pattern_scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if (max_val > 0.85):
                # logging.info("Pattern %s detected at %i, %i, %i, %i", name, max_loc[0], max_loc[1], width, height)
                return (max_loc[0], max_loc[1], width, height)
        return None

    
        


