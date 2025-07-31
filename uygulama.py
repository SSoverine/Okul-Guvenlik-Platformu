import tkinter as tk
import subprocess
import multiprocessing
from PIL import Image, ImageTk

multiprocessing.set_start_method('spawn', force=True)

window = tk.Tk()
window.title("Güvenlik Arayüzü")
window.geometry("1024x720")
#window.iconbitmap("logo.ico") 

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = (screen_width - 1024) // 2
y = (screen_height - 720) // 2
window.geometry(f"1024x720+{x}+{y}")

background_image = Image.open("Assets/arkaplan.png")
background_photo = ImageTk.PhotoImage(background_image)

background_label = tk.Label(window, image=background_photo)
background_label.place(relwidth=1, relheight=1)

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

button1 = tk.Button(window, image=button1_photo, command=button1_click, borderwidth=0, highlightthickness=0, bg='#87cfdb', activebackground='#87cfdb')
button1.place(relx=0.5, rely=0.3, anchor='center')

button2 = tk.Button(window, image=button2_photo, command=button2_click, borderwidth=0, highlightthickness=0, bg='#87cfdb', activebackground='#87cfdb')
button2.place(relx=0.5, rely=0.5, anchor='center')

button3 = tk.Button(window, image=button3_photo, command=button3_click, borderwidth=0, highlightthickness=0, bg='#87cfdb', activebackground='#87cfdb')
button3.place(relx=0.5, rely=0.7, anchor='center')

window.mainloop()
