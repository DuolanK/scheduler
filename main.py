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
            name TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
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

record_map = {}  # Словарь для хранения ID записей

def update_record_list():
    listbox.delete(0, tk.END)
    conn = sqlite3.connect("records.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, done FROM records")
    records = cursor.fetchall()
    conn.close()
    
    global record_map
    record_map = {}  # Очищаем словарь перед обновлением

    for index, record in enumerate(records):
        status = "✔" if record[2] else "✘"
        listbox.insert(tk.END, f"{record[1]} [{status}]")  # Показываем только текст и статус
        record_map[index] = record[0]  # Связываем индекс Listbox с ID записи

def delete_record():
    try:
        selected_index = listbox.curselection()[0]  # Получаем выбранный индекс
        record_id = record_map[selected_index]  # Получаем ID из record_map
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        update_record_list()
    except IndexError:
        messagebox.showwarning("Внимание", "Выберите запись для удаления!")

def toggle_done():
    try:
        selected_index = listbox.curselection()[0]  # Получаем выбранный индекс
        record_id = record_map[selected_index]  # Получаем ID из record_map
        conn = sqlite3.connect("records.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE records SET done = NOT done WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        update_record_list()
    except IndexError:
        messagebox.showwarning("Внимание", "Выберите запись для изменения статуса!")

root = tk.Tk()
root.title("Day AGENDA")
root.geometry("800x600")

# Загружаем изображение для фона
bg_image = Image.open("onepiece.jpg")
bg_image = bg_image.resize((800, 600))
bg_photo = ImageTk.PhotoImage(bg_image)

# Создаём Label и помещаем его в самое нижнее положение (фон)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Создаём виджеты
entry_name = tk.Entry(root, width=40)
button_add = tk.Button(root, text="Добавить запись", command=add_record, width=15)
button_delete = tk.Button(root, text="Удалить запись", command=delete_record, width=15)
button_toggle = tk.Button(root, text="Изменить статус", command=toggle_done, width=15)
listbox = tk.Listbox(root, width=40, height=15)

# Размещаем виджеты поверх фона
entry_name.place(x=50, y=30)
button_add.place(x=450, y=30)
button_delete.place(x=450, y=70)
button_toggle.place(x=450, y=110)
listbox.place(x=50, y=70)

create_db()
update_record_list()

# Запуск главного цикла
root.mainloop()
