import tkinter as tk
from tkinter import *
import sqlite3
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from tkinter import messagebox

def create_db():
    if not os.path.exists("records.db"):
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            done BOOLEAN NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

def add_record():
    record_name = entry_name.get()
    if record_name:
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (name, done) VALUES (?, ?)", (record_name, 0))
        conn.commit()
        conn.close()
        entry_name.delete(0, tk.END)
        update_record_list()
    else:
        messagebox.showwarning("Внимание", "Поле записи не может быть пустым!")

record_map = {}

def update_record_list():
    listbox.delete(0, tk.END)
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, done FROM records")
    records = cursor.fetchall()
    conn.close()

    global record_map
    record_map = {}

    for index, record in enumerate(records):
        status = "✔" if record[2] else "✘"
        listbox.insert(tk.END, f"{record[1]} [{status}]")
        record_map[index] = record[0]

def delete_record():
    try:
        selected_index = listbox.curselection()[0]
        record_id = record_map[selected_index]
        
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        
        # Перемещаем в архив
        cursor.execute("INSERT INTO archive (name, done) SELECT name, done FROM records WHERE id = ?", (record_id,))
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        
        conn.commit()
        conn.close()
        update_record_list()
    except IndexError:
        messagebox.showwarning("Внимание", "Выберите запись для удаления!")

def toggle_done():
    try:
        selected_index = listbox.curselection()
        if not selected_index:
            raise IndexError  # Генерируем ошибку, если элемент не выбран
        record_id = record_map[selected_index[0]]
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE records SET done = NOT done WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        update_record_list()
    except IndexError:
        messagebox.showwarning("Внимание", "Выберите запись для изменения статуса!")

def show_archive():
    archive_window = Toplevel(root)
    archive_window.title("Архив")
    archive_window.geometry("400x400")

    archive_listbox = tk.Listbox(archive_window, width=50, height=15)
    archive_listbox.pack(pady=10)

    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, done, deleted_at FROM archive ORDER BY deleted_at DESC")
    records = cursor.fetchall()
    conn.close()

    for record in records:
        status = "✔" if record[1] else "✘"
        archive_listbox.insert(tk.END, f"{record[0]} [{status}] - {record[2]}")

    def clear_archive():
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM archive")
        conn.commit()
        conn.close()
        archive_listbox.delete(0, tk.END)

    button_clear_archive = tk.Button(archive_window, text="Очистить архив", command=clear_archive)
    button_clear_archive.pack(pady=5)

def show_stats():
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    # Учитываем только записи, которые были завершены в нужном периоде
    query = """
    SELECT COUNT(*) FROM records WHERE done = 1 AND DATE(created_at) >= DATE(?)
    """
    cursor.execute(query, (today,))
    daily = cursor.fetchone()[0]

    cursor.execute(query, (week_ago,))
    weekly = cursor.fetchone()[0]

    cursor.execute(query, (month_ago,))
    monthly = cursor.fetchone()[0]

    cursor.execute(query, (year_ago,))
    yearly = cursor.fetchone()[0]

    # Добавляем записи из архива, завершенные в нужный период
    query_archive = """
    SELECT COUNT(*) FROM archive 
    WHERE done = 1 
    AND DATE(created_at) >= DATE(?)
    """
    
    cursor.execute(query_archive, (today,))
    daily += cursor.fetchone()[0]

    cursor.execute(query_archive, (week_ago,))
    weekly += cursor.fetchone()[0]

    cursor.execute(query_archive, (month_ago,))
    monthly += cursor.fetchone()[0]

    cursor.execute(query_archive, (year_ago,))
    yearly += cursor.fetchone()[0]

    conn.close()

    messagebox.showinfo("Статистика", f"Выполнено:\nСегодня: {daily}\nЗа неделю: {weekly}\nЗа месяц: {monthly}\nЗа год: {yearly}")
    
root = tk.Tk()
root.title("Day AGENDA")
root.geometry("800x600")

class Example(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)



        self.image = Image.open("onepiece.jpg")
        self.img_copy= self.image.copy()


        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = Label(self, image=self.background_image)
        self.background.pack(fill=BOTH, expand=YES)
        self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self,event):
        new_width = event.width
        new_height = event.height
        self.image = self.img_copy.resize((new_width, new_height))
        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image =  self.background_image)

e = Example(root)
e.grid(row=0, column=0, columnspan=3, rowspan=4, sticky="nsew")


# Главный фрейм
frame_main = tk.Frame(root)
frame_main.grid(row=0, column=0, sticky="nsew", padx=(10,300), pady=(10,300))

# Делаем `frame_main` адаптивным
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Ввод и кнопки
entry_name = tk.Entry(frame_main)
entry_name.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

button_add = tk.Button(frame_main, text="Добавить", command=add_record)
button_add.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# Контейнер для listbox и кнопок
frame_content = tk.Frame(frame_main)
frame_content.grid(row=1, column=0, columnspan=3, sticky="nsew")

# Делаем `frame_content` адаптивным
frame_main.grid_rowconfigure(1, weight=1)
frame_main.grid_columnconfigure(0, weight=1)

# Listbox (адаптивный)
listbox = tk.Listbox(frame_content)
listbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

# Делаем listbox адаптивным
frame_content.grid_rowconfigure(0, weight=1)
frame_content.grid_columnconfigure(0, weight=1)

# Фрейм для кнопок
frame_buttons = tk.Frame(frame_content)
frame_buttons.grid(row=0, column=1, padx=5, pady=5, sticky="ns")

# Кнопки справа
buttons = {
    "Удалить": delete_record,
    "Статус": toggle_done,
    "Архив": show_archive,
    "Статистика": show_stats
}

for text, command in buttons.items():
    btn = tk.Button(frame_buttons, text=text, width=15, command=command)
    btn.pack(fill=tk.X, pady=2)

update_record_list()

root.mainloop()