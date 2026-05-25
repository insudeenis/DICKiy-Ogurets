import tkinter as tk
from tkinter import ttk
import subprocess
import os

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Командный проект")
        self.root.geometry("900x600")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Жилье
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Цены на жилье")
        
        try:
            from housing_analysis import HousingAnalysis
            HousingAnalysis(self.tab1)
        except ImportError:
            tk.Label(self.tab1, text="Ошибка: файл housing_analysis.py не найден", fg="red").pack(pady=50)
        except Exception as e:
            tk.Label(self.tab1, text=f"Ошибка: {e}", fg="red").pack(pady=50)
        
        # Вкладка 2: Дороги
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Плохие дороги")
        
        # Кнопка для запуска программы  Никиты (отдельным окном)
        btn = tk.Button(self.tab2, text="Запустить анализ дорог", 
                       command=self.run_roads_program, bg="lightblue", font=("Arial", 14))
        btn.pack(pady=100)
        
        # Вкладка 3: Температура
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Температура")
        tk.Label(self.tab3, text="Задание Саши (температура)", font=("Arial", 14)).pack(pady=100)
    
    def run_roads_program(self):
        # Запускаем roads.py в отдельном процессе
        try:
            subprocess.Popen(["python", "roads.py"])
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Не удалось запустить roads.py\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
