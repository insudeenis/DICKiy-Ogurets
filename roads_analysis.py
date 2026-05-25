import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class RoadsAnalysis:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.data = None
        self.current_fig = None
        self.columns = []
        self.setup_ui()
    
    def setup_ui(self):
        # Верхняя панель с кнопками
        top = ttk.Frame(self.parent)
        top.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(top, text="1. Загрузить CSV файл", command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="2. Показать анализ", command=self.show_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="3. График + прогноз", command=self.plot_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="4. Экспорт графика", command=self.export_plot).pack(side=tk.LEFT, padx=5)
        
        # Таблица
        self.table_frame = ttk.Frame(self.parent)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Область для графика
        self.plot_frame = ttk.Frame(self.parent)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            # Читаем CSV файл без pandas
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                self.columns = next(reader)  # Первая строка - заголовки
                
                # Проверка на нужные колонки
                if 'Год' not in self.columns or 'Субъект' not in self.columns or 'Доля_плохих_дорог_%' not in self.columns:
                    raise ValueError("Файл должен содержать колонки: Год, Субъект, Доля_плохих_дорог_%")
                
                # Читаем все строки
                self.data = []
                for row in reader:
                    self.data.append(row)
            
            self.display_table()
            messagebox.showinfo("OK", f"Загружено {len(self.data)} строк")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def display_table(self):
        # Очищаем старую таблицу
        for w in self.table_frame.winfo_children():
            w.destroy()
        
        frame = ttk.Frame(self.table_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(frame, columns=self.columns, show='headings')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        for col in self.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        for row in self.data:
            tree.insert('', 'end', values=row)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
    
    def get_column_index(self, col_name):
        # Возвращает индекс колонки по имени
        return self.columns.index(col_name)
    
    def get_unique_subjects(self):
        # Получает уникальные субъекты из данных
        subj_idx = self.get_column_index('Субъект')
        subjects = set()
        for row in self.data:
            subjects.add(row[subj_idx])
        return sorted(list(subjects))
    
    def get_subject_data(self, subject):
        # Получает данные для конкретного субъекта, отсортированные по годам
        year_idx = self.get_column_index('Год')
        road_idx = self.get_column_index('Доля_плохих_дорог_%')
        subj_idx = self.get_column_index('Субъект')
        
        years = []
        values = []
        
        for row in self.data:
            if row[subj_idx] == subject:
                years.append(int(row[year_idx]))
                values.append(float(row[road_idx]))
        
        # Сортировка по годам
        sorted_pairs = sorted(zip(years, values))
        years = [p[0] for p in sorted_pairs]
        values = [p[1] for p in sorted_pairs]
        
        return years, values
    
    def show_analysis(self):
        if self.data is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл")
            return
        
        subjects = self.get_unique_subjects()
        changes = {}
        
        for subj in subjects:
            years, values = self.get_subject_data(subj)
            if len(values) < 2:
                continue
            first = values[0]
            last = values[-1]
            changes[subj] = first - last  # положительное = уменьшение
        
        if not changes:
            messagebox.showinfo("Результат", "Нет данных для анализа")
            return
        
        max_subj = max(changes, key=changes.get)
        min_subj = min(changes, key=changes.get)
        
        result = (f"Макс. уменьшение плохих дорог: {max_subj} ({changes[max_subj]:.2f} п.п.)\n"
                  f"Мин. уменьшение (или рост): {min_subj} ({changes[min_subj]:.2f} п.п.)")
        messagebox.showinfo("Результат анализа", result)
    
    def moving_average_forecast(self, values, n, steps):
        vals = list(values)
        forecast = []
        for _ in range(steps):
            window = vals[-n:]
            avg = sum(window) / len(window)
            forecast.append(avg)
            vals.append(avg)
        return forecast
    
    def plot_dialog(self):
        if self.data is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл")
            return
        
        subjects = self.get_unique_subjects()
        if len(subjects) == 0:
            return
        
        win = tk.Toplevel(self.parent)
        win.title("Параметры графика")
        win.geometry("300x200")
        
        tk.Label(win, text="Субъект:").pack(pady=5)
        subj_var = tk.StringVar(value=subjects[0])
        ttk.Combobox(win, textvariable=subj_var, values=subjects, state='readonly').pack()
        
        tk.Label(win, text="Период скользящей средней (N):").pack(pady=5)
        n_var = tk.IntVar(value=3)
        ttk.Spinbox(win, from_=2, to=10, textvariable=n_var, width=5).pack()
        
        tk.Label(win, text="Прогноз на (лет):").pack(pady=5)
        f_var = tk.IntVar(value=3)
        ttk.Spinbox(win, from_=1, to=10, textvariable=f_var, width=5).pack()
        
        def do():
            self.plot_subject(subj_var.get(), n_var.get(), f_var.get())
            win.destroy()
        
        ttk.Button(win, text="Построить", command=do).pack(pady=10)
    
    def plot_subject(self, subject, n_window, forecast_years):
        years, values = self.get_subject_data(subject)
        
        forecast_vals = self.moving_average_forecast(values, n_window, forecast_years)
        last_year = years[-1]
        forecast_years_range = list(range(last_year + 1, last_year + forecast_years + 1))
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(years, values, 'o-', label='История', color='blue')
        ax.plot(forecast_years_range, forecast_vals, 's--', label='Прогноз', color='red')
        ax.set_title(f'Доля плохих дорог: {subject}')
        ax.set_xlabel('Год')
        ax.set_ylabel('% плохих дорог')
        ax.legend()
        ax.grid(True)
        
        # Очистка и вставка графика
        for w in self.plot_frame.winfo_children():
            w.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_fig = fig
    
    def export_plot(self):
        if self.current_fig is None:
            messagebox.showwarning("Нет графика", "Сначала постройте график")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if path:
            self.current_fig.savefig(path, dpi=150, bbox_inches='tight')
            messagebox.showinfo("Экспорт", f"Сохранён: {path}")
