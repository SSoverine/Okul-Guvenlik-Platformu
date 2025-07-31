import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pandas as pd

class ProjectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Veri Gösterici")
        self.root.geometry("600x400")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        #self.root.iconbitmap("logo.ico") 

        x = (screen_width - 1024) // 2
        y = (screen_height - 720) // 2
        self.root.geometry(f"1024x720+{x}+{y}")


        # Arka plan rengi
        background_label = ttk.Label(self.root, background="#87cfdb")
        background_label.place(relwidth=1, relheight=1)

        # Proje dosyasının bulunduğu dizinin bir üst klasörünü al
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.data_dir = os.path.join(self.project_dir, "Veriler")

        # Klasörlerin mevcut olup olmadığını kontrol et
        self.check_folders()

        # Menü
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.view_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Veri Görüntüle", menu=self.view_menu)
        self.view_menu.add_command(label="Öğrenciler", command=self.view_students)
        self.view_menu.add_command(label="Mekanlar", command=self.view_mechanics)  # Mekanlar menüsü
        self.view_menu.add_command(label="Potansiyel İhlal Unsurları", command=self.view_potential_violation_folders)  # Potansiyel İhlal Unsurları

        # Etiketler ve Listbox'lar
        self.label = tk.Label(self.root, text="Veri Görüntülemek İçin Bir Seçenek Seçin", font=("Bahnschrift", 14), background="#87cfdb")
        self.label.pack(pady=20)

        self.listbox = tk.Listbox(self.root, width=50, height=10, background="#3e6eb3", fg="white", font=("Bahnschrift", 12))
        self.listbox.pack(pady=10)

        # Liste öğelerine tıklanarak işlem yapılacak
        self.listbox.bind("<Double-1>", self.on_item_select)

        # Başlangıçta görünen klasör, henüz belirlenmedi
        self.current_folder = None

        # Arama kutusu ve butonu en alta alındı
        self.search_entry = tk.Entry(self.root, font=("Bahnschrift", 12), bg="#3e6eb3", fg="white", width=40)
        self.search_entry.pack(pady=10, padx=10)

        self.search_button = tk.Button(self.root, text="Ara", command=self.search_in_current_folder, font=("Bahnschrift", 12), background="#3e6eb3", fg="white", width=20)
        self.search_button.pack(pady=5)

    def view_potential_violation_folders(self):
        """Potansiyel İhlal Unsurları verisini göster"""
        violation_folder = os.path.join(self.data_dir, "Potansiyel_Ihlal_Unsurlari")
        self.show_violation_folders(violation_folder)

    def show_violation_folders(self, violation_folder):
        """Potansiyel İhlal Unsurları klasörünü göster"""
        self.listbox.delete(0, tk.END)

        # Alt klasörleri listele
        violations = self.list_folders(violation_folder)
        if not violations:
            messagebox.showwarning("Uyarı", "Potansiyel İhlal Unsurları klasörleri bulunamadı!")
            return

        for violation in violations:
            self.listbox.insert(tk.END, violation)

        # Listbox tıklama olayını ayarla
        self.listbox.bind("<Double-1>", lambda event: self.show_csv_files_directly(event, violation_folder))
        self.current_folder = violation_folder  # Mevcut klasörü güncelle

    def show_csv_files_directly(self, event, parent_folder_path):
        """Seçilen klasördeki direkt CSV dosyalarını göster"""
        selected_item = self.listbox.get(self.listbox.curselection())
        folder_path = os.path.join(parent_folder_path, selected_item)

        # CSV dosyalarını listele
        csv_files = self.list_csv_files(folder_path)

        if not csv_files:
            messagebox.showwarning("Uyarı", "Bu klasörde herhangi bir CSV dosyası bulunamadı!")
            return

        self.listbox.delete(0, tk.END)
        for csv_file in csv_files:
            self.listbox.insert(tk.END, csv_file)

        # CSV dosyasını açma fonksiyonunu bağla
        self.listbox.bind("<Double-1>", lambda event: self.open_csv_file(event, folder_path))

    def check_folders(self):
        """Veriler klasöründeki klasörlerin mevcut olup olmadığını kontrol et"""
        required_folders = ["Öğrenciler", "Mekanlar", "Potansiyel_Ihlal_Unsurlari"]
        for folder in required_folders:
            folder_path = os.path.join(self.data_dir, folder)
            if not os.path.exists(folder_path):
                messagebox.showerror("Hata", f"'{folder}' klasörü bulunamadı: {folder_path}")
                self.root.quit()
                return

    def view_mechanics(self):
        """Mekanlar verisini göster"""
        mechanics_folder = os.path.join(self.data_dir, "Mekanlar")
        self.show_mechanics_folders(mechanics_folder)

    def show_mechanics_folders(self, mechanics_folder):
        """Mekanlar klasörünü göster"""
        self.listbox.delete(0, tk.END)

        mechanics = self.list_folders(mechanics_folder)
        if not mechanics:
            messagebox.showwarning("Uyarı", "Mekanlar klasörleri bulunamadı!")
            return

        for mechanic in mechanics:
            self.listbox.insert(tk.END, mechanic)

        self.listbox.bind("<Double-1>", lambda event: self.show_date_folders(event, mechanics_folder))
        self.current_folder = mechanics_folder  # Mevcut klasörü güncelle

    def search_in_current_folder(self):
        """Mevcut klasörde arama yap"""
        search_term = self.search_entry.get()
        if not search_term or not self.current_folder:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir arama terimi girin ve geçerli bir klasör seçin.")
            return

        # Klasördeki klasör ve dosyaları listele
        items = self.list_folders(self.current_folder) + self.list_csv_files(self.current_folder)
        matched_items = [item for item in items if search_term.lower() in item.lower()]

        if not matched_items:
            messagebox.showinfo("Sonuç", "Arama sonucu bulunamadı.")
        else:
            self.listbox.delete(0, tk.END)
            for item in matched_items:
                self.listbox.insert(tk.END, item)

    def list_folders(self, directory):
        """Verilen dizindeki klasörleri listele"""
        try:
            return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
        except FileNotFoundError:
            messagebox.showerror("Hata", "Veri klasörü bulunamadı!")
            return []

    def list_csv_files(self, directory):
        """Verilen dizindeki CSV dosyalarını listele"""
        return [f for f in os.listdir(directory) if f.endswith('.csv')]

    def show_csv_content(self, file_path):
        """CSV dosyasını pandas ile oku ve içeriği ayrı bir pencerede tablo şeklinde göster"""
        try:
            df = pd.read_csv(file_path)
            self.show_table(df)  # CSV içeriğini tablo şeklinde göster
        except Exception as e:
            messagebox.showerror("Hata", f"CSV dosyası okunamadı: {e}")

    def show_table(self, df):
        """Veri çerçevesini (DataFrame) yeni bir pencerede tablo olarak göster"""
        table_window = tk.Toplevel(self.root)
        table_window.title("CSV İçeriği")
        table_window.geometry("600x400")

        # Treeview widget'ı oluştur
        tree = ttk.Treeview(table_window, columns=list(df.columns), show="headings")
        
        # Kolon başlıklarını ayarla
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Verileri tabloya ekle
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        tree.pack(expand=True, fill=tk.BOTH)

    def view_students(self):
        """Öğrenciler verisini göster"""
        students_folder = os.path.join(self.data_dir, "Öğrenciler")
        self.show_student_folders(students_folder)

    def show_student_folders(self, students_folder):
        """Öğrenci klasörlerini göster"""
        self.listbox.delete(0, tk.END)

        students = self.list_folders(students_folder)
        if not students:
            messagebox.showwarning("Uyarı", "Öğrenci klasörleri bulunamadı!")
            return

        for student in students:
            self.listbox.insert(tk.END, student)

        self.listbox.bind("<Double-1>", lambda event: self.show_date_folders(event, students_folder))
        self.current_folder = students_folder  # Mevcut klasörü güncelle

    def show_date_folders(self, event, parent_folder_path):
        """Bir öğrenci ya da mekan klasörü seçildikten sonra tarih klasörlerini göster"""
        selected_item = self.listbox.get(self.listbox.curselection())
        folder_path = os.path.join(parent_folder_path, selected_item)

        # Tarih klasörlerini listele
        date_folders = self.list_folders(folder_path)
        if not date_folders:
            messagebox.showwarning("Uyarı", "Bu klasörde herhangi bir tarih klasörü bulunamadı!")
            return

        self.listbox.delete(0, tk.END)

        for date_folder in date_folders:
            self.listbox.insert(tk.END, date_folder)

        self.listbox.bind("<Double-1>", lambda event: self.show_csv_files_in_date_folder(event, folder_path))

    def show_csv_files_in_date_folder(self, event, parent_folder_path):
        """Bir tarih klasörü seçildiğinde CSV dosyalarını göster"""
        selected_item = self.listbox.get(self.listbox.curselection())
        folder_path = os.path.join(parent_folder_path, selected_item)

        # CSV dosyalarını listele
        csv_files = self.list_csv_files(folder_path)

        if not csv_files:
            messagebox.showwarning("Uyarı", "Bu klasörde herhangi bir CSV dosyası bulunamadı!")
            return

        self.listbox.delete(0, tk.END)
        for csv_file in csv_files:
            self.listbox.insert(tk.END, csv_file)

        self.listbox.bind("<Double-1>", lambda event: self.open_csv_file(event, folder_path))

    def open_csv_file(self, event, folder_path):
        """Bir CSV dosyasını seçildiğinde içeriğini göster"""
        # Seçili öğe var mı diye kontrol et
        selected_csv_file = self.listbox.curselection()
        if not selected_csv_file:
            messagebox.showwarning("Uyarı", "Lütfen bir CSV dosyası seçin.")
            return

        selected_csv_file = self.listbox.get(selected_csv_file)
        file_path = os.path.join(folder_path, selected_csv_file)
        self.show_csv_content(file_path)

    def on_item_select(self, event):
        """Listbox öğesine tıklanınca yapılacak işlem"""
        selected_item = self.listbox.get(self.listbox.curselection())
        print(f"Seçilen öğe: {selected_item}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectApp(root)
    root.mainloop()
