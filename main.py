import tkinter as tk
from tkinter import messagebox, Toplevel
import sqlite3
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk

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
        selected_index = listbox.curselection()[0]
        record_id = record_map[selected_index]
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

    cursor.execute("SELECT COUNT(*) FROM records WHERE done = 1 AND DATE(created_at) = DATE(?)", (today,))
    daily = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM records WHERE done = 1 AND DATE(created_at) >= DATE(?)", (week_ago,))
    weekly = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM records WHERE done = 1 AND DATE(created_at) >= DATE(?)", (month_ago,))
    monthly = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM records WHERE done = 1 AND DATE(created_at) >= DATE(?)", (year_ago,))
    yearly = cursor.fetchone()[0]

    conn.close()

    messagebox.showinfo("Статистика", f"Выполнено:\nСегодня: {daily}\nЗа неделю: {weekly}\nЗа месяц: {monthly}\nЗа год: {yearly}")

root = tk.Tk()
root.title("Day AGENDA")
root.geometry("800x600")

bg_image = Image.open("onepiece.jpg")
bg_image = bg_image.resize((800, 600))
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

entry_name = tk.Entry(root, width=40)
button_add = tk.Button(root, text="Добавить запись", command=add_record, width=15)
button_delete = tk.Button(root, text="Удалить запись", command=delete_record, width=15)
button_toggle = tk.Button(root, text="Изменить статус", command=toggle_done, width=15)
button_archive = tk.Button(root, text="Архив", command=show_archive, width=15)
button_stats = tk.Button(root, text="Статистика", command=show_stats, width=15)

listbox = tk.Listbox(root, width=40, height=15)

entry_name.place(x=50, y=30)
button_add.place(x=450, y=30)
button_delete.place(x=450, y=70)
button_toggle.place(x=450, y=110)
button_archive.place(x=450, y=150)
button_stats.place(x=450, y=190)
listbox.place(x=50, y=70)

create_db()
update_record_list()

root.mainloop()