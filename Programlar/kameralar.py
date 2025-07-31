import cv2
import os
import sys
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
import multiprocessing
import program as program
from PIL import Image, ImageTk
import platform
import face_recognition

class CameraWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Çoklu Kamera Akışı")

        if platform.system() == "Windows":
            self.root.state("zoomed")
        else:
            self.root.attributes("-zoomed", True)  # Linux için tam ekran benzeri çözüm

        self.root.configure(bg='#87cfdb')  # Ana pencere arka plan rengi
        #self.root.iconbitmap("logo.ico") 
        
        # Kameraların verilerini saklamak için
        self.frame_queues = {}
        self.cameras = []
        self.camera_labels = []

        # Araç çubuğu
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # Kamera menüsü
        self.camera_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Kamera", menu=self.camera_menu)
        self.camera_menu.add_command(label="Kamera Ekle", command=self.add_camera)
        self.camera_menu.add_command(label="Kamera Çıkar", command=self.remove_camera)

        # Kameraları listelemek için label (ekranı böleceğiz)
        self.canvas_frame = tk.Frame(self.root, bg='#87cfdb')
        self.canvas_frame.pack(expand=True, fill=tk.BOTH)

    def add_camera(self):
        # Bilgisayara bağlı kameraları listeleme
        available_cameras = self.get_available_cameras()

        # Kamera seçim ekranı
        camera_window = tk.Toplevel(self.root)
        camera_window.title("Kamera Seç")
        camera_window.configure(bg='#87cfdb')  # Arka plan rengi

        # Pencereyi ekranın ortasında başlat
        self.center_window(camera_window, 400, 300)

        # Seçim yapılacak kameralar
        label = tk.Label(camera_window, text="Bir kamera seçin:", bg='#87cfdb')
        label.pack(pady=10)

        # Listeyi oluştur
        camera_listbox = tk.Listbox(camera_window, bg='#87cfdb', selectbackground='#add8e6', height=5)
        for i in available_cameras:
            camera_listbox.insert(tk.END, f"Kamera {i + 1}")
        camera_listbox.pack(pady=10)

        # Seçim yapıldıktan sonra işlem yapılacak buton
        def on_confirm():
            selected_index = camera_listbox.curselection()
            if selected_index:
                camera_index = selected_index[0]  # Seçilen kamerayı al
                camera_window.destroy()

                # Kamera ve bildirim seçimi için mekan adı ve bildirim ayarları
                self.show_location_and_notify_settings(camera_index)
            else:
                messagebox.showinfo("Seçim Yok", "Lütfen bir kamera seçin.")

        confirm_button = tk.Button(camera_window, text="Onayla", command=on_confirm, bg='#87cfdb', activebackground='#87cfdb')
        confirm_button.pack(pady=10)

        # Pencereyi kapatmak için bekle
        self.root.wait_window(camera_window)

    def show_location_and_notify_settings(self, camera_index):
        # Kamera ve bildirim seçimi için özel pencere
        camera_window = tk.Toplevel(self.root)
        camera_window.title("Mekan ve Bildirim Ayarları")
        camera_window.configure(bg='#87cfdb')  # Arka plan rengi

        # Pencereyi ekranın ortasında başlat
        self.center_window(camera_window, 400, 300)

        # Mekan adı sorusu
        location_label = tk.Label(camera_window, text="Kameranın kapsadığı mekanı giriniz:", bg='#87cfdb')
        location_label.pack(pady=10)
        location_entry = tk.Entry(camera_window)
        location_entry.pack(pady=5)

        # Checkbox sorusu
        notify_var = tk.BooleanVar(value=False)  # Varsayılan False
        notify_checkbox = tk.Checkbutton(
            camera_window,
            text="Bu mekanda biri tespit edildiğinde size bildirim gönderilsin mi?",
            variable=notify_var,
            bg='#87cfdb'
        )
        notify_checkbox.pack(pady=10)

        # Onay butonu
        def confirm():
            location = location_entry.get()
            notify = notify_var.get()
            camera_window.destroy()

            if location:  # Eğer mekan adı girilmişse
                # Kamera ve konum bilgisini kaydet
                self.cameras.append((camera_index, location, notify))

                # Yeni label oluştur
                label = tk.Label(self.canvas_frame, bg='#87cfdb')
                label.grid(row=len(self.cameras)//4, column=len(self.cameras)%4, padx=10, pady=10)
                self.camera_labels.append(label)

                # Yeni kuyruk oluştur ve kameraya özel başlatma süreci
                self.frame_queues[camera_index] = multiprocessing.Queue()
                camera_process = multiprocessing.Process(
                    target=program.run_task,
                    args=(self.frame_queues[camera_index], location, camera_index, notify)
                )
                camera_process.start()

                # Kamera akışını güncelleme
                self.update_frames()

        confirm_button = tk.Button(camera_window, text="Onayla", command=confirm, bg='#87cfdb', activebackground='#87cfdb')
        confirm_button.pack(pady=10)

        # Pencereyi kapatmak için bekle
        self.root.wait_window(camera_window)

    def remove_camera(self):
        if not self.cameras:
            messagebox.showinfo("Kamera Yok", "Silinecek kamera yok.")
            return

        # Kameraları listeleyip kullanıcıya seçim yaptırma
        camera_to_remove = simpledialog.askinteger(
            "Kamera Seç",
            "Silmek için bir kamera seçin:\n" +
            "\n".join([f"{i + 1}: {self.cameras[i][1]}" for i in range(len(self.cameras))]),
            parent=self.root
        )
        if camera_to_remove is not None and 1 <= camera_to_remove <= len(self.cameras):
            camera_to_remove -= 1
            self.cameras.pop(camera_to_remove)
            self.camera_labels[camera_to_remove].destroy()
            self.camera_labels.pop(camera_to_remove)
            self.update_frames()

    def update_frames(self):
        for i, (camera_index) in enumerate(self.cameras):
            try:
                frame = self.frame_queues[camera_index].get_nowait()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                self.camera_labels[i].config(image=photo)
                self.camera_labels[i].image = photo
            except:
                pass
        self.root.after(10, self.update_frames)

    def get_available_cameras(self):
        available_cameras = []
        i = 0
        while True:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
            else:
                cap.release()
                break
            cap.release()
            i += 1
        return available_cameras

    def center_window(self, window, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    window = CameraWindow(root)
    root.mainloop()
