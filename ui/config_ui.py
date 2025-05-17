from tkinter import ttk

APP_THEME = 'arc'
COLOR_FILA_PAR = "#ECECEC"
COLOR_FILA_IMPAR = "#FFFFFF"
COLOR_SELECCION_TREEVIEW_BG = "#347083"
COLOR_SELECCION_TREEVIEW_FG = "#FFFFFF"
COLOR_CABECERA_TREEVIEW_BG = "#B0C4DE"
COLOR_CABECERA_TREEVIEW_FG = "#000000"
FUENTE_GENERAL = ("Segoe UI", 10)
FUENTE_TITULOS_FRAMES = ("Segoe UI", 16, "bold")
FUENTE_LABELS_FORMULARIOS = ("Segoe UI", 10)
FUENTE_TREEVIEW_CABECERA = ("Segoe UI", 10, "bold")
FUENTE_TREEVIEW_FILA = ("Segoe UI", 10)
FUENTE_MENU = ("Segoe UI", 9)

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
FRANJAS_HORARIAS_DISPONIBILIDAD = ["Mañana", "Tarde", "Noche"]
FRANJAS_HORARIAS_MATERIA = ["Diurna", "Nocturna"]
BLOQUES_SALON = ["A", "B"]


def configurar_estilos_ttk():
    style = ttk.Style()
    style.configure("TFrame", background=style.lookup('TFrame', 'background'))
    style.configure(
        "Treeview",
        background=COLOR_FILA_IMPAR,
        fieldbackground=COLOR_FILA_IMPAR,
        foreground="black", rowheight=28, font=FUENTE_TREEVIEW_FILA
    )
    style.map(
        "Treeview",
        background=[('selected', COLOR_SELECCION_TREEVIEW_BG)],
        foreground=[('selected', COLOR_SELECCION_TREEVIEW_FG)]
    )
    style.configure(
        "Treeview.Heading",
        background=COLOR_CABECERA_TREEVIEW_BG,
        foreground=COLOR_CABECERA_TREEVIEW_FG,
        font=FUENTE_TREEVIEW_CABECERA, padding=(6, 6), relief="flat"
    )
    style.map("Treeview.Heading", relief=[
              ('active', 'groove'), ('!active', 'flat')])
    style.configure("TButton", padding=(8, 4), relief="flat",
                    font=FUENTE_GENERAL, anchor="center")
    style.configure("TLabel", font=FUENTE_LABELS_FORMULARIOS, padding=(0, 2))
    style.configure("Title.TLabel", font=FUENTE_TITULOS_FRAMES,
                    padding=(0, 10))
    style.configure("TEntry", font=FUENTE_GENERAL, padding=(5, 4))
    style.configure("TCombobox", font=FUENTE_GENERAL, padding=(5, 4))
    # Mantener readonly para comboboxes
    style.map("TCombobox", fieldbackground=[('readonly', COLOR_FILA_IMPAR)])
    style.configure(
        "TCheckbutton", font=FUENTE_LABELS_FORMULARIOS, padding=(5, 5))
    style.configure("TSpinbox", font=FUENTE_GENERAL, padding=(5, 4))
    style.configure("Controls.TFrame", padding=10)
