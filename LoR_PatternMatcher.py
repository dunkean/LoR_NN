import logging
import numpy as np
from PIL import Image, ImageOps
import cv2


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
            pattern_cv_img = cv2.resize(pattern_cv_img, (width, height))
            if canny:
                pattern_cv_img = cv2.Canny(pattern_cv_img, 50, 200)
            self.scaled_patterns[name] = pattern_cv_img

    def register_img_patterns(self):
        list_btn = ["Play", "vsAI", "Friends", "Spare", "Challenge", "Accept", "Play", "vsAI", "Continue", "Ready", "Mulligan"]
        for btn in list_btn:
            self.register_pattern(btn)
    
    def register_number_patterns(self):
        # for i in range(1,21):
        #     self.register_pattern("hp" + str(i))
        
        for i in range(0,11):
            self.register_pattern("mana" + str(i), True)
        
        # for i in range(0,4):
        #     self.register_pattern("smana" + str(i))

   
    def pattern_detect_number(self, img, name):
        interval = None
        if "hp" in name:
            interval = range(20,0,-1)
        elif "smana" in name:
            interval = range(0,4)
        elif "mana" in name:
            interval = range(10,-1,-1)

        for number in interval:
            found = self.match_number(img, self.scaled_patterns[name + str(number)])
            if found:
                print("Found", number)
                return number
            else:
                logging.info("Pattern number %s not detected", name)
        return -1


    def match_number(self, gray, template):
        edged = cv2.Canny(np.array(gray.convert('L')), 50, 200)
        result = cv2.matchTemplate(edged, template, cv2.TM_SQDIFF_NORMED)
        (_, maxVal, _, _) = cv2.minMaxLoc(result)
        match_locations = np.where(result<=0.9)
        if len(match_locations) > 0 :
            # cv2.imshow("Visualize", edged)
            # cv2.imshow("Visualize", template)
            # cv2.waitKey(0)
            return True
        return False



    

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

    
        


