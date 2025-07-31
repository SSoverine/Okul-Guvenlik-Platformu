import cv2
import multiprocessing
import face_recognition
import numpy as np
import os
import csv
import time
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
from plyer import notification
from ultralytics.engine.results import Results

# Önceden tanımlamalar

base_folder = "Veriler"  # Tüm veri dosyalarının saklanacağı ana klasör
place_folder = "Veriler\\Mekanlar"
student_folder = "Veriler\\Öğrenciler"
os.makedirs(base_folder, exist_ok=True)
os.makedirs(place_folder, exist_ok=True)
os.makedirs(student_folder, exist_ok=True)
detected = []  # Bu listeyi global olarak tutacağız

# Kişilerin son kaydedilme zamanını takip etmek için bir sözlük
last_recorded_time = {}

# YOLO modelini yükle
model = YOLO("model.pt")

# Yüz verilerini kaydedilen klasörden al
known_face_encodings = []
known_face_names = []
known_face_classes = []
known_face_numbers = []

output_folder = "data/yuzler"
face_files = os.listdir(output_folder)
def face_files_info():
    for file in face_files:
        if file.endswith(".jpg"):
            # Dosya adı formatından öğrenci bilgilerini al
            file_info = file.split('_')
            name = file_info[0]
            student_class = file_info[1]
            student_number = file_info[2].split(".")[0]  # ".jpg" uzantısını çıkar

            # Yüz resmi yükle
            image_path = os.path.join(output_folder, file)
            image = cv2.imread(image_path)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_encodings = face_recognition.face_encodings(rgb_image)

            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(name)
                known_face_classes.append(student_class)
                known_face_numbers.append(student_number)
            else:
                print(f"Yüz bulunamadı: {file}")


# run_task fonksiyonu, kameradaki kareyi alıp queue üzerinden geri gönderiyor.
def run_task(frame_queue, current_location, cam_index, notify):
    # Potansiyel İhlal Unsurları klasör ve dosya işlemleri
    def init_violation_files():
        today = datetime.now().strftime("%Y-%m-%d")
        violations_folder = os.path.join(base_folder, "Potansiyel_Ihlal_Unsurlari", today)
        os.makedirs(violations_folder, exist_ok=True)

        violation_file = os.path.join(violations_folder, "ihlal_unsurlari.csv")
        if not os.path.isfile(violation_file):
            with open(violation_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Tarih", "Unsurlar", "Mekan", "Zaman"])

        return violation_file


    # İhlal unsurlarını kaydetme fonksiyonu
    def log_violation_item(item, location, timestamp):
        violation_file = init_violation_files()

        with open(violation_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            time_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
            writer.writerow([date, item, location, time_str])


    # Zaman kontrol fonksiyonu
    def can_record_person(name):
        current_time = time.time()
        if name in last_recorded_time:
            elapsed_time = current_time - last_recorded_time[name]
            if elapsed_time < 60:  # 60 saniye (1 dakika) geçmemişse kaydetme
                return False
        # Kayıt yapılabilir, zaman güncellenir
        last_recorded_time[name] = current_time
        return True


    # Kişi klasörlerini ve dosyalarını oluşturma
    def init_person_files(person_name):
        today = datetime.now().strftime("%Y-%m-%d")  # Bugünün tarihi
        person_folder = os.path.join(student_folder, person_name, today)
        os.makedirs(person_folder, exist_ok=True)
        
        # Mekan dosyası
        location_file = os.path.join(person_folder, "mekan.csv")
        if not os.path.isfile(location_file):
            with open(location_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Mekan", "Sınıfı", "Numarası", "Süre (dk)"])

        # Çevre dosyası
        environment_file = os.path.join(person_folder, "cevre.csv")
        if not os.path.isfile(environment_file):
            with open(environment_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Öğrenci", "Sınıfı", "Numarası", "Süre (dk)"])

        # Hareket dosyası
        movement_file = os.path.join(person_folder, "hareket.csv")
        if not os.path.isfile(movement_file):
            with open(movement_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Mekan", "Sınıfı", "Numarası", "Zaman"])

        return location_file, environment_file, movement_file


    # Mekan klasörlerini ve günlük dosyalarını oluşturma
    def init_location_files(location_name):
        today = datetime.now().strftime("%Y-%m-%d")  # Bugünün tarihi
        location_folder = os.path.join(place_folder, location_name, today)
        os.makedirs(location_folder, exist_ok=True)
        
        # Mekan öğrenci dosyası
        student_file = os.path.join(location_folder, "ogrenci.csv")
        if not os.path.isfile(student_file):
            with open(student_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Öğrenci", "Sınıfı", "Numarası", "Süre (dk)"])

        # Mekan hareket dosyası
        movement_file = os.path.join(location_folder, "hareket.csv")
        if not os.path.isfile(movement_file):
            with open(movement_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Öğrenci", "Sınıfı", "Numarası", "Zaman"])
        
        return student_file, movement_file

    # Veriyi dosyalara yazma
    def update_person_files(name, current_location, timestamp, detected_people):
        person_files = init_person_files(name)
        location_file, environment_file, movement_file = person_files

        index = known_face_names.index(name)
        student_class = known_face_classes[index]
        student_number = known_face_numbers[index]

        # Mekan dosyası güncelleme
        with open(location_file, "r+", newline="", encoding="utf-8") as f:
            data = list(csv.reader(f))
            for row in data:
                if row[0] == current_location and row[1] == student_class and row[2] == student_number:
                    row[3] = str(int(row[3]) + 1)
                    break
            else:
                data.append([current_location, student_class, student_number, "1"])
            f.seek(0)
            f.truncate()
            writer = csv.writer(f)
            writer.writerows(data)

        # Çevre dosyası güncelleme
        with open(environment_file, "r+", newline="", encoding="utf-8") as f:
            data = list(csv.reader(f))
            for person in detected_people:
                p_index = known_face_names.index(person)
                p_class = known_face_classes[p_index]
                p_number = known_face_numbers[p_index]
                for row in data:
                    if row[0] == person and row[1] == p_class and row[2] == p_number:
                        row[3] = str(int(row[3]) + 1)
                        break
                else:
                    data.append([person, p_class, p_number, "1"])
            f.seek(0)
            f.truncate()
            writer = csv.writer(f)
            writer.writerows(data)

        # Hareket dosyası güncelleme
        with open(movement_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([current_location, student_class, student_number, datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")])

    def update_location_files(current_location, name, timestamp):
        location_files = init_location_files(current_location)
        student_file, movement_file = location_files
        if name != "Bilinmeyen":
            index = known_face_names.index(name)
            student_class = known_face_classes[index]
            student_number = known_face_numbers[index]
        else:
            student_class = ""
            student_number = ""

        # Mekan öğrenci dosyası güncelleme
        with open(student_file, "r+", newline="", encoding="utf-8") as f:
            data = list(csv.reader(f))
            for row in data:
                if row[0] == name and row[1] == student_class and row[2] == student_number:
                    row[3] = str(int(row[3]) + 1)
                    break
            else:
                data.append([name, student_class, student_number, "1"])
            f.seek(0)
            f.truncate()
            writer = csv.writer(f)
            writer.writerows(data)

        # Mekan hareket dosyası güncelleme
        with open(movement_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, student_class, student_number, datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")])

    video = cv2.VideoCapture(cam_index)
    face_files_info()
    while True:
        ret, frame = video.read()
        if not ret:
            print("Kameradan görüntü alınamadı.")
            break

        # Model sonuçlarını alıyoruz
        results = model.predict(source=frame, conf=0.5)


        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])

        # Yüzleri tanıma
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        detected_people = []  # Bu döngüde algılanan kişiler

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Bilinmeyen"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            # Yüz üzerinde isim göster
            cv2.putText(frame, name, (left, top - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.rectangle(frame, (left, top), (right, bottom), (50, 50, 255), 2)

            # Kişi algılandıysa ve kayıt zamanı uygunsa bilgileri güncelle
            if name != "Bilinmeyen" and can_record_person(name):
                timestamp = time.time()
                detected_people.append(name)

                # Kişiyi güncelle
                if notify:
                    notification.notify(
                        title="Öğrenci Tespiti",
                        message=f'{name} isimli öğrenci, {current_location} bölgesinde tespit edilmiştir.\n{datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")}',
                        timeout=10  # Bildirimin kaç saniye gösterileceğini belirtir
                    )
                update_person_files(name, current_location, timestamp, detected_people)
                update_location_files(current_location, name, timestamp)

            # Burada önemli olan, her yeni kareyi frame_queue'ya gönderiyoruz
            frame_queue.put(frame)

        # Sonuçları modelle işledikten sonra videoyu kaydediyoruz
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Kutuların koordinatları
                conf = box.conf[0]  # Güven skoru
                cls = int(box.cls[0])  # Sınıf kimliği
                if model.names[cls] == "Telefon" and conf >0.5:
                    # Telefon algılandı, ekrana çerçeve çiz ve dosyaya kaydet
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Telefon", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Tespit edilen telefonun bilgilerini kaydet
                    timestamp = time.time()
                    log_violation_item("Telefon", current_location, timestamp)
                elif model.names[cls] == "Sigara" and conf>0.6:  # Sigara sınıf adını kontrol edin
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Kırmızı çerçeve
                    cv2.putText(frame, "Sigara", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    # Tespit edilen sigaranın bilgilerini kaydet
                    timestamp = time.time()
                    log_violation_item("Sigara", current_location, timestamp)
                elif model.names[cls] == "Bıçak":  # sınıf adını kontrol edin
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Kırmızı çerçeve
                    cv2.putText(frame, "Bıçak", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    # Tespit edilen sigaranın bilgilerini kaydet
                    timestamp = time.time()
                    log_violation_item("Bıçak", current_location, timestamp)
        frame_queue.put(frame)
        #cv2.imshow("Yüz Tanıma ve Telefon Tespiti", frame)

        #if cv2.waitKey(1) & 0xFF == ord("q"):
        #    break

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Parametreleri tanımlayın
    frame_queue = multiprocessing.Queue()  # Frame kuyruk oluşturma
    current_location = "Kantin"  # Örnek bir mekan adı
    cam_index = 0  # Kameranın index'i
    notify = False  # Bildirim açma
    known_face_encodings = []  # Yüz tanımlamaları için örnek liste
    known_face_names = []  # Tanımlı yüzlerin isimleri
    known_face_classes = []  # Öğrencilerin sınıf bilgisi
    known_face_numbers = []  # Öğrencilerin numaraları

    # Process başlatma
    thread = multiprocessing.Process(target=run_task, args=(frame_queue, current_location, cam_index, notify))
    thread.start()
