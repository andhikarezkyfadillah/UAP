from flask import Flask, request, render_template, jsonify
from keras.models import load_model
import numpy as np
import os
from PIL import Image
from tensorflow.keras.preprocessing import image as tf_image
from datetime import datetime


app = Flask(__name__) #membuat objek flask dengan nama modul name.
UPLOAD_FOLDER = 'static/uploads/' #direktori tempat file yang diunggah 

model = load_model('model.h5') # load model dari file model h5
@app.after_request # fungsi yang dijalankan permintaan HTTP selesai diproses oleh flask
def add_header(r): #memperesentasikan respon HTTP
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" #instruksi kepada browser u/ tidak menyimpan cache, permanen, dan validasi setiap menggunakan cache
    r.headers["Pragma"] = "no-cache" #hmemberikan instruksi serupa terait cache
    r.headers["Expires"] = "0" # menunjukkan konten tidak valid setelah saat ini
    r.headers['Cache-Control'] = 'public, max-age=0' # konten dapat di cache untuk publik, tetapu umur cache pendek
    return r

@app.route('/') #akses halaman utama
def home():
    return render_template('index.html') 

@app.route('/predict', methods=['POST']) #menanggapi permintaan prediksi melalui HTTP POST
def predict():
    if request.method == 'POST':
        # Ambil waktu awal prediksi
        start_time = datetime.now()

        # Ambil file gambar dari permintaan POST
        file = request.files['file']
        file.save(os.path.join('static', 'temp.jpg')) #menyimpan file yang dunggah

        # Lakukan preprocessing pada gambar
        img = Image.open(file).convert('RGB').resize((150, 150)) #membuka gambar dengan RGB dan ukuran 150x150
        img_array = tf_image.img_to_array(img) / 255.0 #Menghasilkan array NumPy yang mewakili gambar dan melakukan normalisasi nilai pikselnya.
        img_array = np.expand_dims(img_array, axis=0) # Mengubah bentuk array untuk memasukkannya ke dalam model sebagai input.

        # Lakukan prediksi dengan model
        pred = model.predict(img_array)[0] #menampilkan hasil prediksi di halaman web.

        # Ambil waktu akhir prediksi
        end_time = datetime.now()

        # Hitung lama waktu prediksi
        prediction_time = end_time - start_time

        # Ambil label yang diprediksi
        predicted_label = str(np.argmax(pred)) #Hasil indeks ini dikonversi menjadi string dan disimpan dalam variabel predicted_label.
        labels = ['paper', 'rock', 'scissors'] #menentukan kelas
        actual_label = labels[int(predicted_label)] #Hasilnya disimpan dalam variabel actual_label, yang sekarang berisi label kelas yang diprediksi oleh model.

        # Ambil nama file gambar yang diprediksi
        image_name = 'temp.jpg'

        # Hitung akurasi prediksi
        respon_model = [round(elem * 100, 2) for elem in pred] #digunakan untuk mengonversi probabilitas prediksi dari model menjadi persentase yang dibulatkan.

        return predict_result(model, actual_label, image_name, prediction_time, respon_model)
      
    
    
def predict_result(model,  actual_label, image_name, prediction_time, respon_model):
    class_list = {'paper': 0, 'rock': 1, 'scissors': 2} #Sebuah kamus yang menetapkan indeks numerik untuk setiap kelas ('paper', 'rock', 'scissors').
    idx_pred = respon_model.index(max(respon_model)) #Indeks prediksi yang memiliki probabilitas tertinggi.
    labels = list(class_list.keys()) #List yang berisi label kelas ('paper', 'rock', 'scissors')
    return render_template('/result_select.html', labels=labels,
                            probs=respon_model, model=model, pred=idx_pred,
                            run_time=prediction_time, img=image_name)


if __name__ == '__main__':
    app.run(debug=True)
