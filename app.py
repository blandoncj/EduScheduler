# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk

from ui.config_ui import configurar_estilos_ttk, APP_THEME, FUENTE_MENU
from ui.home_ui import InicioFrame
from ui.teachers_ui import ProfesoresFrame
from ui.subjects_ui import MateriasFrame
from ui.classrooms_ui import ClassroomsFrame
from ui.classes_ui import ClasesFrame


class Aplicacion(ThemedTk):
    def __init__(self):
        super().__init__()
        self.set_theme(APP_THEME)  # Usa APP_THEME de config_ui
        self.title("Sistema de Gestión Académica")
        self.geometry("1200x800")

        configurar_estilos_ttk()  # Llama a la función importada

        self.contenedor_principal = ttk.Frame(self, padding="5")
        self.contenedor_principal.pack(side="top", fill="both", expand=True)
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.contenedor_principal.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (
                InicioFrame, ProfesoresFrame, MateriasFrame, ClassroomsFrame, ClasesFrame
        ):
            nombre_clase = F.__name__
            frame = F(parent=self.contenedor_principal, controller=self)
            self.frames[nombre_clase] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self._crear_menu()
        self.mostrar_frame("InicioFrame")

    def _crear_menu(self):
        # Usa FUENTE_MENU de config_ui
        menubar = tk.Menu(self, font=FUENTE_MENU)
        self.config(menu=menubar)
        # Usa FUENTE_MENU de config_ui
        menu_options = {"tearoff": 0, "font": FUENTE_MENU}
        archivo_menu = tk.Menu(menubar, **menu_options)
        menubar.add_cascade(
            label="Archivo", menu=archivo_menu, font=FUENTE_MENU)  # Usa FUENTE_MENU
        archivo_menu.add_command(label="Salir", command=self.salir_aplicacion)

        gestion_menu = tk.Menu(menubar, **menu_options)
        menubar.add_cascade(
            label="Gestión", menu=gestion_menu, font=FUENTE_MENU)  # Usa FUENTE_MENU
        gestion_menu.add_command(
            label="Profesores", command=lambda: self.mostrar_frame("ProfesoresFrame"))
        gestion_menu.add_command(
            label="Materias", command=lambda: self.mostrar_frame("MateriasFrame"))
        gestion_menu.add_command(
            label="Salones", command=lambda: self.mostrar_frame("ClassroomsFrame"))
        gestion_menu.add_command(
            label="Clases", command=lambda: self.mostrar_frame("ClasesFrame"))

    def mostrar_frame(self, nombre_clase_frame):
        frame = self.frames[nombre_clase_frame]
        if hasattr(frame, 'actualizar_contenido'):
            self.after(10, frame.actualizar_contenido)
        frame.tkraise()

    def salir_aplicacion(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?", parent=self):
            self.destroy()


if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
