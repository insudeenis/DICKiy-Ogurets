import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os

# ------------------------------------------------------------
# 1. ЗАГРУЗЧИК ДАННЫХ
# ------------------------------------------------------------
class DataLoader:
    def load(self, filepath):
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath, encoding='utf-8')
        elif filepath.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        else:
            raise ValueError("Нужен CSV или Excel")
        # ожидаемые колонки: Год, Субъект, Доля_плохих_дорог_%
        if not all(col in df.columns for col in ['Год', 'Субъект', 'Доля_плохих_дорог_%']):
            raise ValueError("Файл должен содержать колонки: Год, Субъект, Доля_плохих_дорог_%")
        return df

# ------------------------------------------------------------
# 2. ТАБЛИЦА
# ------------------------------------------------------------
class TableView:
    def display(self, parent, df):
        for w in parent.winfo_children():
            w.destroy()
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(frame, columns=list(df.columns), show='headings')
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        for _, row in df.iterrows():
            tree.insert('', 'end', values=list(row))
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)


# 3. АНАЛИЗАТОР (макс/мин уменьшение)

class Analyzer:
    def max_min_decrease(self, df):
        subjects = df['Субъект'].unique()
        changes = {}
        for subj in subjects:
            subj_df = df[df['Субъект'] == subj].sort_values('Год')
            if len(subj_df) < 2:
                continue
            first = subj_df.iloc[0]['Доля_плохих_дорог_%']
            last = subj_df.iloc[-1]['Доля_плохих_дорог_%']
            changes[subj] = first - last   # положительное = уменьшение
        if not changes:
            return "Нет данных"
        max_subj = max(changes, key=changes.get)
        min_subj = min(changes, key=changes.get)
        return (f"📉 Макс. уменьшение: {max_subj} ({changes[max_subj]:.2f} п.п.)\n"
                f"📈 Мин. уменьшение (или рост): {min_subj} ({changes[min_subj]:.2f} п.п.)")


# 4. ПОСТРОИТЕЛЬ ГРАФИКОВ + ПРОГНОЗ (скользящая средняя)
# -----------------------------------------------------------
class Plotter:
    def __init__(self):
        self.current_fig = None

    def moving_average_forecast(self, values, n, steps):
        """Прогноз методом скользящей средней"""
        vals = list(values)
        forecast = []
        for _ in range(steps):
            window = vals[-n:]
            avg = sum(window) / len(window)
            forecast.append(avg)
            vals.append(avg)  # для следующего шага используем прогноз
        return forecast

    def plot_subject(self, parent, df, subject, n_window, forecast_years):
        subj_df = df[df['Субъект'] == subject].sort_values('Год')
        years = subj_df['Год'].values
        values = subj_df['Доля_плохих_дорог_%'].values

        # Прогноз
        forecast_vals = self.moving_average_forecast(values, n_window, forecast_years)
        last_year = years[-1]
        forecast_years_range = np.arange(last_year + 1, last_year + forecast_years + 1)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(years, values, 'o-', label='История', color='blue')
        ax.plot(forecast_years_range, forecast_vals, 's--', label='Прогноз (скользящая средняя)', color='red')
        ax.set_title(f'Доля плохих дорог: {subject}')
        ax.set_xlabel('Год')
        ax.set_ylabel('% плохих дорог')
        ax.legend()
        ax.grid(True)

        # Очистка и вставка графика в окно
        for w in parent.winfo_children():
            w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_fig = fig

# ------------------------------------------------------------
# 5. ЭКСПОРТЕР
# ------------------------------------------------------------
class Exporter:
    def export(self, fig, path):
        fig.savefig(path, dpi=150, bbox_inches='tight')

# ------------------------------------------------------------
# 6. ГЛАВНОЕ ПРИЛОЖЕНИЕ (GUI)
# ------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Вариант 16: Анализ плохих дорог по регионам РФ")
        self.root.geometry("1100x700")

        self.data = None
        self.loader = DataLoader()
        self.table = TableView()
        self.analyzer = Analyzer()
        self.plotter = Plotter()
        self.exporter = Exporter()

        self._build_ui()

    def _build_ui(self):
        # Верхняя панель
        top = ttk.Frame(self.root)
        top.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(top, text="1. Загрузить файл", command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="2. Показать анализ", command=self.show_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="3. Построить график + прогноз", command=self.plot_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="4. Экспорт графика", command=self.export_plot).pack(side=tk.LEFT, padx=5)

        # Таблица
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Область для графика
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")])
        if not path:
            return
        try:
            self.data = self.loader.load(path)
            self.table.display(self.table_frame, self.data)
            messagebox.showinfo("OK", f"Загружено {len(self.data)} строк")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_analysis(self):
        if self.data is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл")
            return
        res = self.analyzer.max_min_decrease(self.data)
        messagebox.showinfo("Результат анализа", res)

    def plot_dialog(self):
        if self.data is None:
            messagebox.showwarning("Нет данных", "Сначала загрузите файл")
            return
        subjects = sorted(self.data['Субъект'].unique())
        if len(subjects) == 0:
            return

        win = tk.Toplevel(self.root)
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
            self.plotter.plot_subject(self.plot_frame, self.data, subj_var.get(), n_var.get(), f_var.get())
            win.destroy()
        ttk.Button(win, text="Построить", command=do).pack(pady=10)

    def export_plot(self):
        if self.plotter.current_fig is None:
            messagebox.showwarning("Нет графика", "Сначала постройте график")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("SVG", "*.svg")])
        if path:
            self.exporter.export(self.plotter.current_fig, path)
            messagebox.showinfo("Экспорт", f"Сохранён: {path}")

# ------------------------------------------------------------
# ЗАПУСК
# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
