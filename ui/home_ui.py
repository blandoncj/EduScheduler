import tkinter.ttk as ttk


class InicioFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="20")
        self.controller = controller
        label = ttk.Label(
            self,
            text="Bienvenido al Sistema de Gestión Académica",
            style="Title.TLabel"
        )
        label.pack(padx=20, pady=50, expand=True)

    def actualizar_contenido(self): pass
