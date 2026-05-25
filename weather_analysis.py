import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class WeatherAnalysis:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.records = []
        self.setup_ui()
    
    def setup_ui(self):
        # Верхняя панель с кнопками
        top = ttk.Frame(self.parent)
        top.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(top, text="1. Открыть JSON файл", command=self.load_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top, text="Период сглаживания (n):").pack(side=tk.LEFT, padx=(20, 5))
        self.spin_n = tk.Spinbox(top, from_=2, to=10, width=5)
        self.spin_n.pack(side=tk.LEFT)
        self.spin_n.delete(0, tk.END)
        self.spin_n.insert(0, "3")
        
        ttk.Label(top, text="Дней прогноза:").pack(side=tk.LEFT, padx=(10, 5))
        self.spin_pred = tk.Spinbox(top, from_=0, to=15, width=5)
        self.spin_pred.pack(side=tk.LEFT)
        self.spin_pred.delete(0, tk.END)
        self.spin_pred.insert(0, "5")
        
        ttk.Button(top, text="2. Обновить график", command=self.update_chart).pack(side=tk.LEFT, padx=10)
        
        # Таблица
        self.table_frame = ttk.Frame(self.parent)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Область для статистики
        self.stats_label = tk.Label(self.parent, text="Статистика: файл не загружен", 
                                    font=("Arial", 10), fg="blue", justify=tk.LEFT)
        self.stats_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Область для графика
        self.plot_frame = ttk.Frame(self.parent)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.current_fig = None
    
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not path:
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.records = []
            for item in data:
                self.records.append({
                    'day': int(item['day']),
                    't_min': float(item['t_min']),
                    't_max': float(item['t_max']),
                    't_avg': float(item['t_avg']),
                    'desc': str(item['desc']),
                    'amplitude': float(item['t_max']) - float(item['t_min'])
                })
            
            self.display_table()
            self.update_chart()
            messagebox.showinfo("OK", f"Загружено {len(self.records)} дней")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def display_table(self):
        # Очищаем старую таблицу
        for w in self.table_frame.winfo_children():
            w.destroy()
        
        # Создаем таблицу
        columns = ("День", "Мин t", "Макс t", "Средняя t", "Описание", "Перепад")
        tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', height=8)
        
        # Настройка заголовков
        col_widths = [50, 80, 80, 80, 150, 80]
        for col, width in zip(columns, col_widths):
            tree.heading(col, text=col)
            tree.column(col, width=width)
        
        # Заполнение данными
        for rec in self.records:
            tree.insert("", "end", values=(
                rec['day'],
                rec['t_min'],
                rec['t_max'],
                rec['t_avg'],
                rec['desc'],
                f"{rec['amplitude']:.1f}"
            ))
        
        # Скроллбары
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
    
    def predict_moving_average(self, data, n, days_to_predict):
        if not data or n <= 0:
            return []
        
        history = list(data)
        predictions = []
        
        for _ in range(days_to_predict):
            current_window = history[-n:]
            avg_value = sum(current_window) / len(current_window)
            predictions.append(avg_value)
            history.append(avg_value)
        
        return predictions
    
    def update_chart(self):
        if not self.records:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл")
            return
        
        try:
            window_size = int(self.spin_n.get())
            forecast_days = int(self.spin_pred.get())
        except:
            messagebox.showerror("Ошибка", "Введите корректные числа")
            return
        
        if window_size > len(self.records):
            messagebox.showwarning("Ошибка", f"Период n ({window_size}) больше данных ({len(self.records)})")
            return
        
        # Поиск перепадов
        max_amp = max(self.records, key=lambda x: x['amplitude'])
        min_amp = min(self.records, key=lambda x: x['amplitude'])
        
        stats_text = (f"Самый СИЛЬНЫЙ перепад: День {max_amp['day']} (Перепад: {max_amp['amplitude']:.1f}°C, "
                     f"с {max_amp['t_min']} до {max_amp['t_max']}°C)\n"
                     f"Самый СЛАБЫЙ перепад: День {min_amp['day']} (Перепад: {min_amp['amplitude']:.1f}°C, "
                     f"с {min_amp['t_min']} до {min_amp['t_max']}°C)")
        self.stats_label.config(text=stats_text)
        
        # Построение графика
        days = [r['day'] for r in self.records]
        t_min = [r['t_min'] for r in self.records]
        t_max = [r['t_max'] for r in self.records]
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        ax.plot(days, t_min, 'o-', label='Мин. температура', color='blue', linewidth=2)
        ax.plot(days, t_max, 's-', label='Макс. температура', color='red', linewidth=2)
        
        # Прогноз
        if forecast_days > 0 and len(t_max) >= window_size:
            predictions = self.predict_moving_average(t_max, window_size, forecast_days)
            forecast_days_x = list(range(days[-1] + 1, days[-1] + 1 + forecast_days))
            ax.plot(forecast_days_x, predictions, 's--', label=f'Прогноз (n={window_size})', 
                   color='orange', linewidth=2)
        
        ax.set_title('График температур и прогноз')
        ax.set_xlabel('День месяца')
        ax.set_ylabel('Температура (°C)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Очистка и отображение
        for w in self.plot_frame.winfo_children():
            w.destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_fig = fig
