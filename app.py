from flask import Flask, request, redirect, jsonify, url_for, send_from_directory
from flask_cors import CORS 
from ktpocr import KTPOCR  # Import kode KTPOCR yang telah Anda sebutkan
from kkOcr import KKOCR  # Import kode KTPOCR yang telah Anda sebutkan
import uuid
import os
app = Flask(__name__)
CORS(app)  # Aktifkan CORS untuk aplikasi Flask Anda


app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Definisikan fungsi-fungsi seperti allowed_file, save_ocr_result_to_file, clean_ocr_text, index, dan upload_file sebagaimana Anda lakukan sebelumnya.
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_ocr_result_to_file(text, filename="output.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

def clean_ocr_text(text):
    cleaned_text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
    return cleaned_text

@app.route('/')
def index():
    return 'Scan OCR with Python Flask! by devnolife'

# Tambahkan fungsi untuk melakukan ekstraksi NIK menggunakan KTPOCR
@app.route('/ktp/upload', methods=['POST'])
def extract_nik():
    if 'file' not in request.files:
        return jsonify({'message': 'File tidak ditemukan dalam permintaan!'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Nama file kosong!'}), 400
    if file and allowed_file(file.filename):
        unique_filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filename)

        # Gunakan KTPOCR untuk ekstraksi NIK
        ocr = KTPOCR(filename)
        if ocr.result.nik == None : 
            return jsonify({"message" : "NIK Tidak Ditemukan"}), 400
        extracted_nik = ocr.result.nik

        response_data = {
            'message': 'Ekstraksi NIK berhasil!',
            'filename': unique_filename,
            'nik': extracted_nik,
            'data_tambahan' : {
                "nama" : ocr.result.nama,
                "kelurahan" : ocr.result.kelurahan,
                "kecamatan" : ocr.result.kecamatan
            }
        }

        try :
            os.remove(filename)
        except : 
            print("Cant Remove File")

        return jsonify(response_data), 200
    else:
        return jsonify({'message': 'File yang diupload tidak valid!'}), 400

@app.route('/kk/upload', methods=['POST'])
def extract_kk():
    if 'file' not in request.files:
        return jsonify({'message': 'File tidak ditemukan dalam permintaan!'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Nama file kosong!'}), 400
    if file and allowed_file(file.filename):
        unique_filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filename = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filename)

        # Gunakan KTPOCR untuk ekstraksi NIK
        ocr = KKOCR(filename)
        if ocr.result == "" : 
            return jsonify({"message" : "KK Tidak Ditemukan"}), 400
        extract_kk = ocr.result

        response_data = {
            'message': 'Ekstraksi NIK berhasil!',
            'filename': unique_filename,
            'kk': extract_kk
        }
        try :
            os.remove(filename)
        except : 
            print("Cant Remove File")

        return jsonify(response_data), 200
        
        
    return jsonify({'message': 'File yang diupload tidak valid!'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
