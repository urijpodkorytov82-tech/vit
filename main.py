import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from datetime import datetime

# --- Настройки ---
DATA_FILE = "data.json"
DATE_FORMAT = "%d.%m.%Y" # Формат даты: ДД.ММ.ГГГГ

# --- Функции работы с данными ---
def load_data():
    """Загружает данные из файла JSON."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_data():
    """Сохраняет данные в файл JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Функции валидации и логики ---
def validate_input(date, temp, desc):
    """Проверяет корректность введенных данных."""
    # Проверка даты
    try:
        datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        messagebox.showerror("Ошибка", f"Дата должна быть в формате ДД.ММ.ГГГГ (например, 29.04.2026)")
        return False

    # Проверка температуры
    try:
        float(temp)
    except ValueError:
        messagebox.showerror("Ошибка", "Температура должна быть числом.")
        return False

    # Проверка описания
    if not desc.strip():
        messagebox.showerror("Ошибка", "Описание погоды не может быть пустым.")
        return False

    return True

def add_record():
    """Обрабатывает добавление новой записи."""
    date = date_entry.get()
    temp = temp_entry.get()
    desc = desc_entry.get("1.0", tk.END).strip()
    precip = precip_var.get() == "Да"

    if validate_input(date, temp, desc):
        record = {
            "date": date,
            "temperature": float(temp),
            "description": desc,
            "precipitation": precip
        }
        data.append(record)
        update_treeview()
        save_data()
        clear_inputs()

def clear_inputs():
    """Очищает поля ввода после добавления записи."""
    date_entry.delete(0, tk.END)
    temp_entry.delete(0, tk.END)
    desc_entry.delete("1.0", tk.END)
    precip_var.set("Нет")

def filter_records():
    """Фильтрует записи в таблице на основе критериев пользователя."""
    filtered_data = data.copy()

    # Фильтр по дате
    date_filter = filter_date_entry.get()
    if date_filter:
        try:
            datetime.strptime(date_filter, DATE_FORMAT)
            filtered_data = [r for r in filtered_data if r['date'] == date_filter]
        except ValueError:
            messagebox.showerror("Ошибка", "Дата для фильтра в неверном формате.")
            return

    # Фильтр по температуре
    temp_filter = filter_temp_entry.get()
    if temp_filter:
        try:
            temp_val = float(temp_filter)
            # Показываем записи с температурой ВЫШЕ указанного значения
            filtered_data = [r for r in filtered_data if r['temperature'] > temp_val]
        except ValueError:
            messagebox.showerror("Ошибка", "Температура для фильтра должна быть числом.")
            return

    update_treeview(filtered_data)

def update_treeview(records=None):
    """Обновляет виджет таблицы."""
    for i in tree.get_children():
        tree.delete(i)
    
    # Если records не передан, показываем все данные
    records_to_show = records if records is not None else data

    for record in records_to_show:
        precip_str = "Да" if record['precipitation'] else "Нет"
        tree.insert("", "end", values=(
            record['date'],
            record['temperature'],
            record['description'],
            precip_str
        ))

# --- Инициализация данных ---
data = load_data()

# --- Создание окна ---
root = tk.Tk()
root.title("Weather Diary")
root.geometry("800x500")

# --- Основная рамка для ввода данных ---
input_frame = ttk.LabelFrame(root, text="Добавить новую запись")
input_frame.pack(padx=10, pady=10, fill="x")

# Поля ввода (Дата, Температура)
ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
date_entry = ttk.Entry(input_frame, width=15)
date_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Температура:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
temp_entry = ttk.Entry(input_frame, width=10)
temp_entry.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky="ne")
desc_entry = tk.Text(input_frame, height=3, width=30)
desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="we")

ttk.Label(input_frame, text="Осадки:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
precip_var = tk.StringVar(value="Нет")
ttk.Radiobutton(input_frame, text="Да", variable=precip_var, value="Да").grid(row=2, column=1, sticky="w")
ttk.Radiobutton(input_frame, text="Нет", variable=precip_var, value="Нет").grid(row=2, column=2, sticky="w")

ttk.Button(input_frame, text="Добавить запись", command=add_record).grid(row=2, column=3, padx=5, pady=5)


# --- Рамка для фильтрации ---
filter_frame = ttk.LabelFrame(root, text="Фильтр записей")
filter_frame.pack(padx=10, pady=(0, 10), fill="x")

ttk.Label(filter_frame, text="Дата:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
filter_date_entry = ttk.Entry(filter_frame, width=15)
filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(filter_frame, text="Темп. выше:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
filter_temp_entry = ttk.Entry(filter_frame, width=10)
filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)

ttk.Button(filter_frame, text="Применить фильтр", command=filter_records).grid(row=0, column=4, padx=5, pady=5)
ttk.Button(filter_frame, text="Сбросить фильтр", command=lambda: [filter_date_entry.delete(0,'end'), filter_temp_entry.delete(0,'end'), update_treeview()]).grid(row=0, column=5, padx=5, pady=5)


# --- Таблица для отображения записей ---
tree_frame = ttk.Frame(root)
tree_frame.pack(padx=10, pady=10, fill="both", expand=True)

columns = ("date", "temperature", "description", "precipitation")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
tree.heading("date", text="Дата")
tree.heading("temperature", text="Температура °C")
tree.heading("description", text="Описание")
tree.heading("precipitation", text="Осадки")
tree.column("date", width=120)
tree.column("temperature", width=100)
tree.column("description", width=350)
tree.column("precipitation", width=80)
tree.pack(fill="both", expand=True)

# Заполняем таблицу при запуске
update_treeview()

root.mainloop()