import cv2
import json
import re
import pytesseract
from ktp import KTPInformation
import numpy as np

config = r'--oem 3 --psm 6'

kernel = np.ones((5,5),np.uint8)

class KTPOCR(object):
    def __init__(self, image):
        # image =cv2.dilate(image, kernel, iterations = 1)
        # image = cv2.normalize(image, norm_img, 0, 255, cv2.NORM_MINMAX)
        # image = cv2.GaussianBlur(image, (1, 1), 0)
        self.image = cv2.imread(image)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.threshed = cv2.erode(self.gray, kernel, iterations = 1)
        self.result = KTPInformation()
        self.master_process()

    def process(self, image):
        raw_extracted_text = pytesseract.image_to_string((self.threshed), lang="ind", config=config)
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
            ")" : "1"
        }
        res = ""
        for letter in word:
            if letter in word_dict:
                res += word_dict[letter]
            else:
                res += letter
        return res
    
    def extract(self, extracted_result):
        print(extracted_result.replace('\n', ' -- '))
        for word in extracted_result.split("\n"):
            if "NIK" in word:
                word = word.split(':')
                self.result.nik = self.nik_extract(word[-1].replace(" ", ""))
                continue

            if "Nama" in word:
                word = word.split(':')
                self.result.nama = word[-1].replace('Nama ','')
                continue

            if "Tempat" in word:
                word = word.split(':')
                date_match = re.search("([0-9]{2}\-[0-9]{2}\-[0-9]{4})", word[-1])
                if date_match:
                    self.result.tanggal_lahir = date_match.group(0)
                    self.result.tempat_lahir = word[-1].replace(self.result.tanggal_lahir, '')
                continue

            if 'Darah' in word:
                blood_match = re.search("(LAKI-LAKI|LAKI|LELAKI|PEREMPUAN)", word)
                if blood_match:
                    self.result.jenis_kelamin = blood_match.group(0)

            if 'Alamat' in word:
                self.result.alamat = self.word_to_number_converter(word).replace("Alamat ","")
            if 'NO.' in word:
                self.result.alamat = self.result.alamat + ' '+word
            if "Kecamatan" in word:
                word_split = word.split(':')
                if len(word_split) > 1:
                    self.result.kecamatan = word_split[1].strip()

            if "Desa" in word:
                wrd = word.split()
                desa = []
                for wr in wrd:
                    if not 'desa' in wr.lower():
                        desa.append(wr)
                self.result.kelurahan_atau_desa = ''.join(wr)
            if 'Kewarganegaraan' in word:
                word_split = word.split(':')
                if len(word_split) > 1:
                    self.result.kewarganegaraan = word_split[1].strip()

            if 'Pekerjaan' in word:
                wrod = word.split()
                pekerjaan = []
                for wr in wrod:
                    if not '-' in wr:
                        pekerjaan.append(wr)
                self.result.pekerjaan = ' '.join(pekerjaan).replace('Pekerjaan', '').strip()
            if 'Agama' in word:
                self.result.agama = word.replace('Agama',"").strip()
            if 'Perkawinan' in word:
                word_split = word.split(':')
                if len(word_split) > 1:
                    self.result.status_perkawinan = word_split[1].strip()

            if "RTRW" in word:
                word = word.replace("RTRW",'')
                self.result.rt = word.split('/')[0].strip()
                self.result.rw = word.split('/')[1].strip()

    def master_process(self):
        raw_text = self.process(self.image)
        self.extract(raw_text)

    def to_json(self):
        return json.dumps(self.result.__dict__, indent=4)


