import cv2
import json
import re
import pytesseract
from ktp import KTPInformation
import numpy as np
from spellchecker import SpellChecker

config = r'--oem 3 --psm 6'

kernel = np.ones((5,5),np.uint8)

class KKOCR(object):
    def __init__(self, image):
        # image =cv2.dilate(image, kernel, iterations = 1)
        # image = cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)
        # image = cv2.GaussianBlur(image, (1, 1), 0)
        self.image = cv2.imread(image)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.resultImage = cv2.erode(self.image, kernel, iterations = 1)
        # self.resultImage = cv2.dilate(self.image, kernel, iterations = 1)
        
        cv2.imwrite("edit.jpg", self.resultImage)

        self.result = ""
        self.master_process()


    def process(self, image):
        raw_extracted_text = pytesseract.image_to_string((self.resultImage), lang="ind", config=config)
        return raw_extracted_text

    def word_to_number_converter(self, word):
        word_dict = {
            '|' : "1"
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res


    def nik_extract(self, word):
        word_dict = {
            'b' : "6",
            'e' : "2",
            'o' : '0',
            'O' : "0",
            "S" : "5",
            "s" : "5",
            "?" : "7",
            ")" : "1",
            'Y' : "4"
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res
    
    def extract(self, extracted_result):
        cleanedResult = extracted_result.replace(r'[\s\t\n]+', '')
        print(cleanedResult)
        for index, word in enumerate(cleanedResult.split("\n")):
            nik = re.findall(r'\b\d+\b', word)

            if index == 0:
                result = ''.join(nik)
                self.result = result
                continue
            else:
                pass
            

    def master_process(self):
        raw_text = self.process(self.image)
        self.extract(raw_text)

    def to_json(self):
        return json.dumps(self.result.__dict__, indent=4)


