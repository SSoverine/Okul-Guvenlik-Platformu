import tkinter as tk
import subprocess
import multiprocessing
from PIL import Image, ImageTk

# Bu satır, multiprocessing'in 'spawn' başlatma yöntemini kullanmasını sağlar
multiprocessing.set_start_method('spawn', force=True)

# Pencere oluştur
window = tk.Tk()
window.title("Güvenlik Arayüzü")
window.geometry("1024x720")  # Pencere boyutları
#window.iconbitmap("logo.ico") 

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = (screen_width - 1024) // 2
y = (screen_height - 720) // 2
window.geometry(f"1024x720+{x}+{y}")


# Arka plan resmi yükleme
background_image = Image.open("Assets/arkaplan.png")
background_photo = ImageTk.PhotoImage(background_image)

# Arka plan için bir etiket oluştur
background_label = tk.Label(window, image=background_photo)
background_label.place(relwidth=1, relheight=1)  # Arka planı tüm pencereye yay

# Butonların işlevleri
def button1_click():
    subprocess.Popen(['python', 'Programlar/kameralar.py'])

def button2_click():
    subprocess.Popen(['python', 'Programlar/yuz_ekle.py'])

def button3_click():
    subprocess.Popen(['python', 'Programlar/veriler.py'])

# Buton resimlerini yükleme
def load_image_with_transparency(image_path):
    image = Image.open(image_path).convert("RGBA")  # RGBA formatına dönüştür
    return ImageTk.PhotoImage(image)

button1_photo = load_image_with_transparency("Assets/bÇalıştır.png")
button2_photo = load_image_with_transparency("Assets/bYüzEkle.png")
button3_photo = load_image_with_transparency("Assets/bVeriler.png")

# Butonları oluştur ve ortalayın
button1 = tk.Button(window, image=button1_photo, command=button1_click, borderwidth=0, highlightthickness=0, bg='#87cfdb', activebackground='#87cfdb')
button1.place(relx=0.5, rely=0.3, anchor='center')  # Pencerenin ortasına yerleştir

button2 = tk.Button(window, image=button2_photo, command=button2_click, borderwidth=0, highlightthickness=0, bg='#87cfdb', activebackground='#87cfdb')
button2.place(relx=0.5, rely=0.5, anchor='center')  # Pencerenin ortasına yerleştir

button3 = tk.Button(window, image=button3_photo, command=button3_click, borderwidth=0, highlightthickness=0, bg='#87cfdb', activebackground='#87cfdb')
button3.place(relx=0.5, rely=0.7, anchor='center')  # Pencerenin ortasına yerleştir

# Ana döngüyü başlat
window.mainloop()
