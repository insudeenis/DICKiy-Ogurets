import tkinter as tk
from tkinter import ttk
import subprocess
import os

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Командный проект")
        self.root.geometry("1000x750")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Жилье (Ира)
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="1. Цены на жилье")
        
        try:
            from housing_analysis import HousingAnalysis
            HousingAnalysis(self.tab1)
        except ImportError:
            tk.Label(self.tab1, text="Ошибка: файл housing_analysis.py не найден", fg="red").pack(pady=50)
        except Exception as e:
            tk.Label(self.tab1, text=f"Ошибка: {e}", fg="red").pack(pady=50)
        
        # Вкладка 2: Дороги (Никита)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="2. Плохие дороги")
        
        try:
            from roads_analysis import RoadsAnalysis
            RoadsAnalysis(self.tab2)
        except ImportError:
            tk.Label(self.tab2, text="Ошибка: файл roads_analysis.py не найден", fg="red").pack(pady=50)
        except Exception as e:
            tk.Label(self.tab2, text=f"Ошибка: {e}", fg="red").pack(pady=50)
        
        # Вкладка 3: Температура (Саша)
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="3. Температура")
        
        try:
            from weather_analysis import WeatherAnalysis
            WeatherAnalysis(self.tab3)
        except ImportError:
            tk.Label(self.tab3, text="Ошибка: файл weather_analysis.py не найден", fg="red").pack(pady=50)
        except Exception as e:
            tk.Label(self.tab3, text=f"Ошибка: {e}", fg="red").pack(pady=50)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
