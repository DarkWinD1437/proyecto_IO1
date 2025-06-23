# main.py
import tkinter as tk
from modulos.controladores import MainController
from modulos.vistas import MainView

def main():
    root = tk.Tk()
    controller = MainController(None)  # La vista se asignará después
    view = MainView(root, controller)
    controller.view = view  # Completar la referencia circular
    root.mainloop()

if __name__ == "__main__":
    main()