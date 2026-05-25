import tkinter as tk
from tkinter import ttk

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Командный проект")
        self.root.geometry("900x600")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка 1: Жилье (Задание Иры)
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Цены на жилье")
        
        try:
            from Housing_analitics import HousingAnalysis
            HousingAnalysis(self.tab1)
        except:
            tk.Label(self.tab1, text="Ошибка: файл Housing_analitics.py не найден").pack()
        
        # Вкладка 2: Дороги Задание Никиты
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Плохие дороги")

        try:
            from roads import rroads
            rroads(self.tab2)
        except:
            tk.Label(self.tab2, text="Задание Никиты (16)").pack(pady=50)
        
        
        # Вкладка 3: Температура Задание Саши
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Температура")
        tk.Label(self.tab3, text="Задание Саши (3)").pack(pady=50)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
