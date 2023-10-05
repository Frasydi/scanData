import cv2
import json
import re
import pytesseract
from ktp import KTPInformation
import numpy as np
from spellchecker import SpellChecker

config = r'--oem 3 --psm 6'

kernel = np.ones((5,5),np.uint8)

class KTPOCR(object):
    def __init__(self, image):
        # image =cv2.dilate(image, kernel, iterations = 1)
        # image = cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)
        # image = cv2.GaussianBlur(image, (1, 1), 0)
        self.image = cv2.imread(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255,
	        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        median = cv2.medianBlur(thresh, 3)
        final = median

        
        cv2.imwrite("edit.jpg", final)

        self.result = KTPInformation()
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
                self.result.nik = result
                continue
            else:
                pass
            caseUp = word.upper()
            
            if index == 1:
                try :
                    word = word.split(r'[-.:-]')
                    print(word[0])
                    self.result.nama = word[0]
                    continue
                except : 
                    pass
            if index == 6:
                try :
                    word = word.split(r'[-.:-]')
                    print(word[0])
                    self.result.kelurahan = word[0]
                    continue
                except : 
                    pass
            if index == 7:
                try :
                    word = word.split(r'[-.:-]')
                    print(word[0])
                    self.result.kecamatan = word[0]
                    continue
                except : 
                    pass
            


            # if "Tempat" in word:
            #     word = word.split(':')
            #     date_match = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", word[-1])
            #     if date_match:
            #         self.result.tanggal_lahir = date_match.group(0)
            #         self.result.tempat_lahir = word[-1].replace(self.result.tanggal_lahir, '')
            #     continue

            # if 'Darah' in word:
            #     blood_match = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)
            #     if blood_match:
            #         self.result.jenis_kelamin = blood_match.group(0)

            # if 'Alamat' in word:
            #     self.result.alamat = self.word_to_number_converter(word).replace("Alamat ","")
            # if 'NO.' in word:
            #     self.result.alamat = self.result.alamat + ' '+word
            # if "Kecamatan" in word:
            #     word_split = word.split(':')
            #     if len(word_split) > 1:
            #         self.result.kecamatan = word_split[1].strip()

            # if "Desa" in word:
            #     wrd = word.split()
            #     desa = []
            #     for wr in wrd:
            #         if not 'desa' in wr.lower():
            #             desa.append(wr)
            #     self.result.kelurahan_atau_desa = ''.join(wr)
            # if 'Kewarganegaraan' in word:
            #     word_split = word.split(':')
            #     if len(word_split) > 1:
            #         self.result.kewarganegaraan = word_split[1].strip()

            # if 'Pekerjaan' in word:
            #     wrod = word.split()
            #     pekerjaan = []
            #     for wr in wrod:
            #         if not '-' in wr:
            #             pekerjaan.append(wr)
            #     self.result.pekerjaan = ' '.join(pekerjaan).replace('Pekerjaan', '').strip()
            # if 'Agama' in word:
            #     self.result.agama = word.replace('Agama',"").strip()
            # if 'Perkawinan' in word:
            #     word_split = word.split(':')
            #     if len(word_split) > 1:
            #         self.result.status_perkawinan = word_split[1].strip()

            # if "RTRW" in word:
            #     word = word.replace("RTRW",'')
            #     self.result.rt = word.split('/')[0].strip()
            #     self.result.rw = word.split('/')[1].strip()

    def master_process(self):
        raw_text = self.process(self.image)
        self.extract(raw_text)

    def to_json(self):
        return json.dumps(self.result.__dict__, indent=4)


