import tkinter as tk
from tkinter import messagebox
import sqlite3
import os
from PIL import Image, ImageTk  # Импортируем для работы с изображениями

def create_db():
    if not os.path.exists("records.db"):
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

def add_record():
    record_name = entry_name.get()
    if record_name:
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (name) VALUES (?)", (record_name,))
        conn.commit()
        conn.close()
        entry_name.delete(0, tk.END)
        update_record_list()
    else:
        messagebox.showwarning("Внимание", "Поле записи не может быть пустым!")

def delete_record():
    try:
        record_id = listbox.curselection()[0]
        record_name = listbox.get(record_id)
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM records WHERE name = ?", (record_name,))
        conn.commit()
        conn.close()
        update_record_list()
    except IndexError:
        messagebox.showwarning("Внимание", "Выберите запись для удаления!")

def update_record_list():
    listbox.delete(0, tk.END)
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM records")
    records = cursor.fetchall()
    conn.close()
    
    for record in records:
        listbox.insert(tk.END, record[0])

root = tk.Tk()
root.title("Day AGENDA")
root.geometry("800x600")  # Устанавливаем размер окна

# Загружаем изображение для фона
bg_image = Image.open("onepiece.jpg")  # Подставь свой файл
bg_image = bg_image.resize((800, 600))  # Подгоняем под размер окна
bg_photo = ImageTk.PhotoImage(bg_image)

# Создаём Label и помещаем его в самое нижнее положение (фон)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)  # Растягиваем на весь экран

# Создаём виджеты
entry_name = tk.Entry(root, width=40)
button_add = tk.Button(root, text="Добавить запись", command=add_record)
button_delete = tk.Button(root, text="Удалить запись", command=delete_record)
listbox = tk.Listbox(root, width=40, height=10)

# Размещаем виджеты поверх фона
entry_name.place(x=50, y=30)
button_add.place(x=400, y=30)
button_delete.place(x=400, y=70)
listbox.place(x=50, y=70)

create_db()
update_record_list()

# Запуск главного цикла
root.mainloop()