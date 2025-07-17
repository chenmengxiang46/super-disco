from gui_interface import RestaurantDakaGUI
import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    # 设置应用主题
    style = ttk.Style()
    try:
        # 尝试使用更现代的主题
        style.theme_use('clam')  # 可选值: 'clam', 'alt', 'default', 'classic'
    except:
        pass
    app = RestaurantDakaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()