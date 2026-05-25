import tkinter as tk
from tkinter import ttk, messagebox
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HousingAnalysis:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.load_csv_data()
        self.setup_ui()
    
    def load_csv_data(self):
        # Загружаем данные из CSV файла
        self.years = []
        self.price_1 = []
        self.price_2 = []
        self.price_3 = []
        self.price_4 = []
        
        try:
            with open('prices.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.years.append(int(row['Год']))
                    self.price_1.append(int(row['1-комн']))
                    self.price_2.append(int(row['2-комн']))
                    self.price_3.append(int(row['3-комн']))
                    self.price_4.append(int(row['4-комн+']))
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл prices.csv не найден")
    
    def setup_ui(self):
        # Заголовок
        label = tk.Label(self.parent, text="Цены на первичное жилье в России", 
                        font=("Arial", 14, "bold"))
        label.pack(pady=10)
        
        # Таблица
        columns = ("Год", "1-комн", "2-комн", "3-комн", "4+ комн")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Заполняем таблицу
        for i in range(len(self.years)):
            self.tree.insert("", "end", values=(
                self.years[i],
                f"{self.price_1[i]:,}",
                f"{self.price_2[i]:,}",
                f"{self.price_3[i]:,}",
                f"{self.price_4[i]:,}"
            ))
        
        self.tree.pack(pady=10)
        
        # Кнопки
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=10)
        
        btn1 = tk.Button(btn_frame, text="График цен по годам", 
                        command=self.show_graph, bg="lightblue", width=20)
        btn1.pack(side="left", padx=5)
        
        btn2 = tk.Button(btn_frame, text="Что подорожало/подешевело", 
                        command=self.show_analysis, bg="lightgreen", width=25)
        btn2.pack(side="left", padx=5)
        
        btn3 = tk.Button(btn_frame, text="Прогноз на N лет", 
                        command=self.show_forecast, bg="lightyellow", width=20)
        btn3.pack(side="left", padx=5)
        
        # Поле для вывода результатов
        self.result = tk.Text(self.parent, height=8, width=80)
        self.result.pack(pady=10)
        self.result.config(state="disabled")
    
    def show_graph(self):
        # График цен
        window = tk.Toplevel(self.parent)
        window.title("График цен")
        window.geometry("700x500")
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        ax.plot(self.years, self.price_1, marker="o", label="1-комнатная", linewidth=2)
        ax.plot(self.years, self.price_2, marker="s", label="2-комнатная", linewidth=2)
        ax.plot(self.years, self.price_3, marker="^", label="3-комнатная", linewidth=2)
        ax.plot(self.years, self.price_4, marker="d", label="4+ комнат", linewidth=2)
        
        ax.set_xlabel("Год")
        ax.set_ylabel("Цена (руб.)")
        ax.set_title("Цены на жилье по годам")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, window)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def show_analysis(self):
        # Анализ: какие квартиры сильнее всего подорожали/подешевели
        
        # Берем цены первого и последнего года
        start_prices = [self.price_1[0], self.price_2[0], self.price_3[0], self.price_4[0]]
        end_prices = [self.price_1[-1], self.price_2[-1], self.price_3[-1], self.price_4[-1]]
        names = ["1-комнатные", "2-комнатные", "3-комнатные", "4+ комнатные"]
        
        # Считаем процент изменения
        changes = []
        for i in range(4):
            percent = ((end_prices[i] - start_prices[i]) / start_prices[i]) * 100
            changes.append((names[i], percent, end_prices[i] - start_prices[i]))
        
        # Сортируем по проценту (от большего к меньшему)
        changes.sort(key=lambda x: x[1], reverse=True)
        
        # Формируем текст
        text = "=" * 50 + "\n"
        text += "АНАЛИЗ ЦЕН ЗА 15 ЛЕТ (2010-2024)\n"
        text += "=" * 50 + "\n\n"
        
        text += "СИЛЬНЕЕ ВСЕГО ПОДОРОЖАЛИ:\n"
        text += f"  {changes[0][0]}: +{changes[0][1]:.1f}% ({changes[0][2]:,.0f} руб.)\n\n"
        
        text += "СИЛЬНЕЕ ВСЕГО ПОДЕШЕВЕЛИ (или меньше подорожали):\n"
        text += f"  {changes[3][0]}: +{changes[3][1]:.1f}% ({changes[3][2]:,.0f} руб.)\n\n"
        
        text += "ПОДРОБНО ПО ВСЕМ ТИПАМ:\n"
        text += "-" * 40 + "\n"
        for item in changes:
            arrow = "↑" if item[1] > 0 else "↓"
            text += f"{arrow} {item[0]}: +{item[1]:.1f}%\n"
        
        # Выводим в текстовое поле
        self.result.config(state="normal")
        self.result.delete(1.0, tk.END)
        self.result.insert(1.0, text)
        self.result.config(state="disabled")
    
    def show_forecast(self):
        # Прогноз на N лет методом скользящей средней
        
        # Спрашиваем количество лет
        dialog = tk.Toplevel(self.parent)
        dialog.title("Прогноз")
        dialog.geometry("300x120")
        
        tk.Label(dialog, text="На сколько лет вперед прогноз?").pack(pady=10)
        entry = tk.Entry(dialog)
        entry.pack(pady=5)
        entry.insert(0, "5")
        
        def calculate():
            try:
                n = int(entry.get())
                dialog.destroy()
                self.draw_forecast(n)
            except:
                messagebox.showerror("Ошибка", "Введите число")
        
        tk.Button(dialog, text="Рассчитать", command=calculate).pack(pady=10)
    
    def draw_forecast(self, n_years):
        # Строим график с прогнозом
        
        window = tk.Toplevel(self.parent)
        window.title(f"Прогноз на {n_years} лет")
        window.geometry("800x600")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Данные для прогноза
        all_prices = [self.price_1, self.price_2, self.price_3, self.price_4]
        names = ["1-комн", "2-комн", "3-комн", "4+ комн"]
        colors = ["blue", "green", "orange", "red"]
        
        for i in range(4):
            hist_prices = all_prices[i]
            hist_years = self.years
            
            # Скользящая средняя (окно 3 года)
            ma = []
            for j in range(len(hist_prices) - 2):
                avg = (hist_prices[j] + hist_prices[j+1] + hist_prices[j+2]) / 3
                ma.append(avg)
            
            # Прогноз: берем последнюю скользящую среднюю и добавляем тренд
            last_ma = ma[-1]
            forecast = []
            current = last_ma
            
            # Считаем средний рост за последние 5 лет
            last_5_growth = []
            for j in range(len(hist_prices)-5, len(hist_prices)-1):
                if hist_prices[j] > 0:
                    growth = hist_prices[j+1] / hist_prices[j]
                    last_5_growth.append(growth)
            
            avg_growth = sum(last_5_growth) / len(last_5_growth)
            
            # Прогнозируем
            forecast_years = list(range(hist_years[-1] + 1, hist_years[-1] + n_years + 1))
            current_price = hist_prices[-1]
            
            for _ in range(n_years):
                current_price = current_price * avg_growth
                forecast.append(current_price)
            
            # Рисуем историю (сплошная линия)
            ax.plot(hist_years, hist_prices, color=colors[i], marker='o', 
                   linewidth=2, label=f'{names[i]} (история)')
            
            # Рисуем прогноз (пунктир)
            ax.plot(forecast_years, forecast, color=colors[i], 
                   linestyle='--', linewidth=2, marker='s', 
                   label=f'{names[i]} (прогноз)')
        
        # Разделительная линия
        ax.axvline(x=self.years[-1], color='gray', linestyle=':', linewidth=2, label='Сегодня')
        
        ax.set_xlabel("Год")
        ax.set_ylabel("Цена (руб.)")
        ax.set_title(f"Прогноз цен на жилье на {n_years} лет")
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        canvas = FigureCanvasTkAgg(fig, window)
        canvas.draw()
        canvas.get_tk_widget().pack()

# Запуск программы
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Анализ цен на жилье")
    root.geometry("900x600")
    app = HousingAnalysis(root)
    root.mainloop()
