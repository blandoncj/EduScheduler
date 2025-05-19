import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from ttkthemes import ThemedTk

from ui.config_ui import configurar_estilos_ttk, APP_THEME, FUENTE_MENU
from ui.home_ui import InicioFrame
from ui.teachers_ui import ProfesoresFrame # Ya lo tienes
from ui.subjects_ui import MateriasFrame
from ui.classrooms_ui import ClassroomsFrame
from ui.classes_ui import ClasesFrame
from repositories.teacher_repository import TeacherRepository
from repositories.scheduled_class_repository import ScheduledClassRepository

try:
    from repositories.subject_repository import SubjectRepository
    from repositories.classroom_repository import ClassroomRepository
except ImportError:
    SubjectRepository = None
    ClassroomRepository = None
    print("Advertencia: SubjectRepository o ClassroomRepository no encontrados. El horario exportado usará IDs.")

from utils.excel_exporter import export_teacher_schedule_to_excel # Nueva importación

class Aplicacion(ThemedTk):
    def __init__(self):
        super().__init__()
        self.set_theme(APP_THEME)
        self.title("Sistema de Gestión Académica")
        self.geometry("1200x800")

        configurar_estilos_ttk()

        # Inicializar repositorios que se usarán en la aplicación principal o se pasarán
        self.teacher_repo = TeacherRepository()
        self.schedule_repo = ScheduledClassRepository()
        self.subject_repo = SubjectRepository() if SubjectRepository else None
        self.classroom_repo = ClassroomRepository() if ClassroomRepository else None


        self.contenedor_principal = ttk.Frame(self, padding="5")
        self.contenedor_principal.pack(side="top", fill="both", expand=True)
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.contenedor_principal.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # Pasa las instancias de los repositorios a los frames que los necesiten
        # Ejemplo: si ProfesoresFrame necesita teacher_repo, ya lo está creando internamente,
        # pero si ClasesFrame necesita schedule_repo, teacher_repo, etc., deberías pasarlos.
        # Por ahora, la estructura original de inicialización de frames se mantiene,
        # ajusta según cómo tus frames acceden a los repositorios.

        for F in (
                InicioFrame, ProfesoresFrame, MateriasFrame, ClassroomsFrame, ClasesFrame
        ):
            nombre_clase = F.__name__
            # Modifica la instanciación si tus frames necesitan los repositorios
            # Ejemplo para ClasesFrame que podría necesitar varios repositorios:
            # if F == ClasesFrame:
            #     frame = F(parent=self.contenedor_principal, controller=self,
            #               schedule_repo=self.schedule_repo,
            #               teacher_repo=self.teacher_repo,
            #               subject_repo=self.subject_repo,
            #               classroom_repo=self.classroom_repo)
            # else:
            #     frame = F(parent=self.contenedor_principal, controller=self)
            frame = F(parent=self.contenedor_principal, controller=self) # Usando tu forma original por ahora
            self.frames[nombre_clase] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self._crear_menu()
        self.mostrar_frame("InicioFrame")

    def _crear_menu(self):
        menubar = tk.Menu(self, font=FUENTE_MENU)
        self.config(menu=menubar)
        menu_options = {"tearoff": 0, "font": FUENTE_MENU}

        archivo_menu = tk.Menu(menubar, **menu_options)
        menubar.add_cascade(
            label="Archivo", menu=archivo_menu, font=FUENTE_MENU)
        
        # NUEVA OPCIÓN DE MENÚ
        archivo_menu.add_command(
            label="Descargar Horario", 
            command=self._descargar_horario_profesor_excel
        )
        archivo_menu.add_command(label="Salir", command=self.salir_aplicacion)

        gestion_menu = tk.Menu(menubar, **menu_options)
        menubar.add_cascade(
            label="Gestión", menu=gestion_menu, font=FUENTE_MENU)
        gestion_menu.add_command(
            label="Profesores", command=lambda: self.mostrar_frame("ProfesoresFrame"))
        gestion_menu.add_command(
            label="Materias", command=lambda: self.mostrar_frame("MateriasFrame"))
        gestion_menu.add_command(
            label="Salones", command=lambda: self.mostrar_frame("ClassroomsFrame"))
        gestion_menu.add_command(
            label="Clases", command=lambda: self.mostrar_frame("ClasesFrame"))

    def _descargar_horario_profesor_excel(self):
        # 1. Obtener lista de profesores para seleccionar
        # ProfesoresFrame ya usa teacher_repo, podemos instanciarlo aquí también o accederlo si está en controller
        # Para simplificar, lo instanciamos o usamos el que ya tenemos en self.
        
        # Asegurarse de que el repositorio de profesores esté inicializado
        if not hasattr(self, 'teacher_repo') or not self.teacher_repo:
            self.teacher_repo = TeacherRepository()

        profesores_data = self.teacher_repo.get_all_teachers() # Retorna lista de listas/tuplas [cedula, nombre, apellido, disponibilidad]
        
        if not profesores_data:
            messagebox.showinfo("Información", "No hay profesores registrados para seleccionar.", parent=self)
            return

        # Crear una lista de nombres de profesores para el diálogo
        # (nombre apellido (cedula))
        choices = {f"{p[1]} {p[2]} (C.C: {p[0]})": p[0] for p in profesores_data} # {display_name: cedula}
        
        if not choices:
             messagebox.showinfo("Información", "No hay profesores disponibles para la selección.", parent=self)
             return

        # 2. Mostrar un diálogo para seleccionar el profesor
        # Usaremos un Toplevel personalizado para mostrar una lista seleccionable.
        
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar Profesor")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Seleccione un profesor para generar su horario:").pack(pady=10)
        
        listbox_var = tk.StringVar(value=list(choices.keys()))
        listbox = tk.Listbox(dialog, listvariable=listbox_var, height=10, exportselection=False)
        listbox.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Scrollbar para el Listbox
        scrollbar = ttk.Scrollbar(listbox, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        selected_teacher_id = None

        def on_select():
            nonlocal selected_teacher_id
            try:
                selected_index = listbox.curselection()[0]
                selected_display_name = listbox.get(selected_index)
                selected_teacher_id = choices[selected_display_name]
                dialog.destroy()
            except IndexError:
                messagebox.showwarning("Advertencia", "Por favor, seleccione un profesor.", parent=dialog)
        
        def on_cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Aceptar", command=on_select).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side="left", padx=5)
        
        self.wait_window(dialog) # Esperar a que el diálogo se cierre

        if not selected_teacher_id:
            return # Usuario canceló o no seleccionó

        # 3. Obtener el nombre completo del profesor seleccionado
        profesor_seleccionado_data = self.teacher_repo.get_teacher_by_id(selected_teacher_id)
        if not profesor_seleccionado_data:
            messagebox.showerror("Error", "No se pudo obtener la información del profesor seleccionado.", parent=self)
            return
        
        teacher_full_name = f"{profesor_seleccionado_data[1]} {profesor_seleccionado_data[2]}"

        # 4. Obtener las clases del profesor
        # Asegurarse de que schedule_repo esté inicializado
        if not hasattr(self, 'schedule_repo') or not self.schedule_repo:
            self.schedule_repo = ScheduledClassRepository()
            
        clases_profesor = self.schedule_repo.get_scheduled_classes_by_teacher_id(selected_teacher_id)

        if not clases_profesor:
            messagebox.showinfo("Información", f"El profesor {teacher_full_name} no tiene clases programadas.", parent=self)
            return

        # 5. Pedir al usuario dónde guardar el archivo
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Guardar Horario del Profesor como...",
            initialfile=f"Horario_{teacher_full_name.replace(' ', '_')}.xlsx",
            parent=self
        )

        if not file_path:
            return # Usuario canceló el diálogo de guardar

        # 6. Exportar a Excel
        # Asegurarse de que subject_repo y classroom_repo estén inicializados si existen
        if SubjectRepository and (not hasattr(self, 'subject_repo') or not self.subject_repo) :
             self.subject_repo = SubjectRepository()
        if ClassroomRepository and (not hasattr(self, 'classroom_repo') or not self.classroom_repo) :
             self.classroom_repo = ClassroomRepository()


        success = export_teacher_schedule_to_excel(
            clases_profesor, 
            teacher_full_name,
            self.subject_repo, # Pasar la instancia del repo de materias
            self.classroom_repo, # Pasar la instancia del repo de salones
            file_path
        )

        if success:
            messagebox.showinfo("Éxito", f"Horario de {teacher_full_name} exportado correctamente a:\n{file_path}", parent=self)


    def mostrar_frame(self, nombre_clase_frame):
        frame = self.frames[nombre_clase_frame]
        if hasattr(frame, 'actualizar_contenido'):
            # self.after(10, frame.actualizar_contenido) # Comentado para ver si es necesario
            frame.actualizar_contenido() # Llamar directamente puede ser mejor para consistencia
        frame.tkraise()

    def salir_aplicacion(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?", parent=self):
            self.destroy()


if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()