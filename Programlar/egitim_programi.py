import cv2
import face_recognition
import os
from PIL import Image
import numpy as np
import time

def train_face(name, Class, number, cam):
    # Video ayarları
    video = cv2.VideoCapture(cam)

    # Yüz verilerini kaydetmek için bir klasör oluştur
    output_folder = "data/yuzler"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"{output_folder} klasörü oluşturuldu.")

    # Eğitim verisi için yüz kaydetme
    i = 0
    start_time = time.time()  # Zamanı başlat
    countdown_start_time = None  # Geri sayımı başlatan zaman

    while True:
        ret, frame = video.read()
        height, width, _ = frame.shape

        # Ekranın sağ üst köşesi için konum hesapla
        x = width - 50  # Sağdan 50 piksel
        y = 50  # Üstten 50 piksel
        if not ret:
            print("Kameradan görüntü alınamadı.")
            break

        # Görüntüyü RGB'ye çevir
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Yüz algılama
        face_locations = face_recognition.face_locations(rgb_frame)

        # Yüz algılandığında, etrafına çerçeve koy
        if face_locations:
            for (top, right, bottom, left) in face_locations:
                # Çerçeve çizme
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Yuz algilandi!", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Fotoğraf çekme işlemi
        elapsed_time = time.time() - start_time
        if elapsed_time >= 3 and i < 5:
            # 3 saniye geçtiğinde fotoğraf çek
            print("Bir sonraki fotoğraf için:")
            if countdown_start_time is None:
                countdown_start_time = time.time()  # Geri sayımı başlat

            remaining_time = 3 - (time.time() - countdown_start_time)
            remaining_time_text = f"{int(remaining_time)}"

            # Geri sayım metnini sağ üst köşeye yerleştir
            cv2.putText(frame, remaining_time_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # Fotoğraf çekme
            if remaining_time <= 0:
                # Dosya adı formatı: "ad_sınıf_numara_index.jpg"
                filename = f"{name}_{Class}_{number}_{i}.jpg"
                file_path = os.path.join(output_folder, filename)

                try:
                    # OpenCV ile BGR'yi RGB'ye çevir
                    pil_image = Image.fromarray(rgb_frame)  # numpy array'ini Pillow görüntüsüne çevir
                    pil_image.save(file_path)  # Fotoğrafı Pillow ile kaydet
                    print(f"Yüz kaydedildi: {file_path}")
                except Exception as e:
                    print(f"Fotoğraf kaydedilemedi: {e}")

                i += 1
                start_time = time.time()  # Zamanı tekrar başlat
                countdown_start_time = None  # Geri sayımı sıfırla

        # Görüntüyü ekranında gösterme
        cv2.imshow("Yüz Ekleme Sistemi", frame)

        # 5 fotoğraf kaydedildiğinde sonlandır
        if i >= 5:
            print("Eğitim verileri kaydedildi.")
            break

        k = cv2.waitKey(1)
        if k == ord("q"):
            break

    # Video kaydını sonlandır
    video.release()
    cv2.destroyAllWindows()

# Eğer bu dosya doğrudan çalıştırılırsa, kullanıcıdan bilgi al
if __name__ == "__main__":
    name = input("Kişinin ismini ve soyismini giriniz: ")
    Class = input("Kişinin sınıfını giriniz: ")
    number = input("Kişinin numarasını giriniz: ")
    train_face(name, Class, number)
