import tkinter as tk
from tkinter import simpledialog
from egitim_programi import train_face  # egitim_programi.py'dan fonksiyonu import et
import cv2

# Ana pencereyi oluştur
window = tk.Tk()
window.title("Yüz Ekleme Sistemi")
window.geometry("300x300")  # Pencere boyutu
#window.iconbitmap("logo.ico") 

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = (screen_width - 300) // 2
y = (screen_height - 300) // 2
window.geometry(f"300x300+{x}+{y}")

# Kullanıcıdan bilgi almak için etiketler ve giriş kutuları oluştur
label_name = tk.Label(window, text="İsim Soyisim:", bg='#87cfdb', font="Bahnschrift", fg="#2f2f2f")
label_name.pack(pady=5)
entry_name = tk.Entry(window, bg="#7375be")
entry_name.pack(pady=5)

label_class = tk.Label(window, text="Sınıf/Görev:", font="Bahnschrift", bg='#87cfdb', fg="#2f2f2f")
label_class.pack(pady=5)
entry_class = tk.Entry(window, bg="#7375be")
entry_class.pack(pady=5)

label_number = tk.Label(window, text="Numara:", font="Bahnschrift", bg='#87cfdb', fg="#2f2f2f")
label_number.pack(pady=5)
entry_number = tk.Entry(window, bg="#7375be")
entry_number.pack(pady=5)

# Kamera seçim fonksiyonu
def select_camera():
    available_cameras = get_available_cameras()

    # Kamera seçim ekranı
    camera_index = simpledialog.askinteger(
        "Kamera Seç",
        "Bir kamera seçin:\n" + "\n".join([f"{i + 1}: Kamera {i + 1}" for i in available_cameras]),
        parent=window
    )
    
    if camera_index is not None and 1 <= camera_index <= len(available_cameras):
        return available_cameras[camera_index - 1]
    else:
        return None

def get_available_cameras():
    available_cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
        cap.release()
    return available_cameras

window.configure(bg='#87cfdb')

def start_training():
    # Kullanıcıdan alınan bilgileri al
    name = entry_name.get()
    class_info = entry_class.get()
    number = entry_number.get()

    # Kamera seçimi
    camera_index = select_camera()

    if camera_index is None:
        print("Geçerli bir kamera seçilmedi.")
        return

    # Yüz tanıma eğitimini başlat
    train_face(name, class_info, number, camera_index)

# Buton oluştur
button_start = tk.Button(window, text="Yüz Ekle", command=start_training)
button_start.pack(pady=20)

# Ana döngüyü başlat
window.mainloop()
