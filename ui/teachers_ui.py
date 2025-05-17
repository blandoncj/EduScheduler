import tkinter as tk
from tkinter import ttk, messagebox
from ui.config_ui import (
    COLOR_FILA_PAR, COLOR_FILA_IMPAR, DIAS_SEMANA,
    FRANJAS_HORARIAS_DISPONIBILIDAD, FUENTE_LABELS_FORMULARIOS
)
from repositories.teacher_repository import TeacherRepository


class VentanaDisponibilidad(tk.Toplevel):
    """
    Muestra la disponibilidad de un profesor.
    Esta clase no necesita cambios para la integración del repositorio,
    ya que recibe los datos de disponibilidad ya procesados.
    """

    def __init__(
            self,
            parent_controller,
            profesor_nombre_completo,
            # Este es un diccionario {dia: [franjas]}
            datos_disponibilidad_profesor
    ):
        super().__init__(parent_controller)
        self.title(f"Disponibilidad de {profesor_nombre_completo}")
        self.geometry("450x350")
        self.transient(parent_controller)
        self.grab_set()
        self.configure(bg=ttk.Style().lookup('TFrame', 'background'))

        self.datos_disponibilidad_profesor = datos_disponibilidad_profesor if datos_disponibilidad_profesor else {}

        frame_tabla = ttk.Frame(self, padding="10")
        frame_tabla.pack(expand=True, fill="both")

        cols_disponibilidad = ("Día", "Franjas Horarias")
        self.tree_disponibilidad = ttk.Treeview(
            frame_tabla, columns=cols_disponibilidad, show="headings", selectmode="none")

        self.tree_disponibilidad.heading(
            "Día", text="Día de la Semana", anchor="w")
        self.tree_disponibilidad.column(
            "Día", width=150, anchor="w", stretch=tk.NO)
        self.tree_disponibilidad.heading(
            "Franjas Horarias", text="Franjas Disponibles", anchor="w")
        self.tree_disponibilidad.column(
            "Franjas Horarias", width=250, anchor="w", stretch=tk.YES)

        self.tree_disponibilidad.tag_configure(
            'par_disp', background=COLOR_FILA_PAR)
        self.tree_disponibilidad.tag_configure(
            'impar_disp', background=COLOR_FILA_IMPAR)

        self._cargar_datos_en_treeview()

        self.tree_disponibilidad.pack(expand=True, fill="both", side="left")

        scrollbar_disponibilidad = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tree_disponibilidad.yview)
        self.tree_disponibilidad.configure(
            yscrollcommand=scrollbar_disponibilidad.set)
        scrollbar_disponibilidad.pack(side="right", fill="y")

        frame_botones_disp = ttk.Frame(self, padding="0 10 10 10")
        frame_botones_disp.pack(fill="x", side="bottom")
        frame_botones_disp.columnconfigure(0, weight=1)
        frame_botones_disp.columnconfigure(2, weight=1)

        btn_cerrar = ttk.Button(
            frame_botones_disp, text="Cerrar", command=self.destroy)
        btn_cerrar.grid(row=0, column=1, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    def _cargar_datos_en_treeview(self):
        for i in self.tree_disponibilidad.get_children():
            self.tree_disponibilidad.delete(i)
        idx = 0
        # DIAS_SEMANA debe estar definido en ui.config_ui
        for dia in DIAS_SEMANA:
            franjas = self.datos_disponibilidad_profesor.get(dia, [])
            tag = 'par_disp' if idx % 2 == 0 else 'impar_disp'
            franjas_str = ", ".join(franjas) if franjas else "No disponible"
            self.tree_disponibilidad.insert(
                "", "end", values=(dia, franjas_str), tags=(tag,))
            idx += 1


class VentanaGestionDisponibilidad(tk.Toplevel):
    """
    Permite editar la disponibilidad de un profesor.
    Esta clase no necesita cambios para la integración del repositorio,
    ya que opera sobre un diccionario de disponibilidad que se le pasa
    y devuelve el diccionario actualizado.
    """

    def __init__(self, parent, disponibilidad_actual):  # disponibilidad_actual es un dict
        super().__init__(parent)
        self.title("Gestionar Disponibilidad")
        self.transient(parent)
        self.grab_set()
        self.geometry("450x370")
        self.configure(bg=ttk.Style().lookup('TFrame', 'background'))

        # Asegura que disponibilidad_actualizada sea un diccionario
        self.disponibilidad_actualizada = disponibilidad_actual.copy(
        ) if isinstance(disponibilidad_actual, dict) else {}
        self.check_vars = {}

        frame_principal = ttk.Frame(self, padding="15")
        frame_principal.pack(expand=True, fill="both")

        ttk.Label(frame_principal, text="Marque las franjas disponibles:", font=FUENTE_LABELS_FORMULARIOS + ("bold",)).grid(
            row=0, column=0, columnspan=len(FRANJAS_HORARIAS_DISPONIBILIDAD) + 1, pady=(0, 10), sticky="w")

        for col_idx, franja in enumerate(FRANJAS_HORARIAS_DISPONIBILIDAD):
            ttk.Label(frame_principal, text=franja, font=FUENTE_LABELS_FORMULARIOS).grid(
                row=1, column=col_idx + 1, padx=5, pady=2, sticky="nsew")

        for row_idx, dia in enumerate(DIAS_SEMANA):
            ttk.Label(frame_principal, text=dia + ":", font=FUENTE_LABELS_FORMULARIOS).grid(
                row=row_idx + 2, column=0, padx=5, pady=5, sticky="w")
            self.check_vars[dia] = {}
            for col_idx, franja in enumerate(FRANJAS_HORARIAS_DISPONIBILIDAD):
                var = tk.BooleanVar()
                # Verifica si la franja está en la disponibilidad actual para ese día
                if dia in self.disponibilidad_actualizada and franja in self.disponibilidad_actualizada.get(dia, []):
                    var.set(True)
                chk = ttk.Checkbutton(frame_principal, variable=var)
                chk.grid(row=row_idx + 2, column=col_idx +
                         1, padx=5, pady=2, sticky="nsew")
                self.check_vars[dia][franja] = var

        for i in range(len(FRANJAS_HORARIAS_DISPONIBILIDAD) + 1):
            frame_principal.columnconfigure(i, weight=1 if i > 0 else 0)

        frame_botones = ttk.Frame(frame_principal, padding="10 0 0 0")
        frame_botones.grid(row=len(DIAS_SEMANA) + 2, column=0,
                           columnspan=len(FRANJAS_HORARIAS_DISPONIBILIDAD) + 1, pady=10)

        frame_botones.columnconfigure(0, weight=1)
        frame_botones.columnconfigure(1, weight=0)
        frame_botones.columnconfigure(2, weight=1)

        btn_guardar = ttk.Button(
            frame_botones, text="Guardar Cambios", command=self._guardar_cambios)
        btn_guardar.grid(row=0, column=0, padx=5, sticky="e")

        btn_cancelar = ttk.Button(
            frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.grid(row=0, column=2, padx=5, sticky="w")

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _guardar_cambios(self):
        nueva_disponibilidad = {}
        for dia, franjas_vars in self.check_vars.items():
            franjas_seleccionadas = []
            for franja, var in franjas_vars.items():
                if var.get():
                    franjas_seleccionadas.append(franja)

            if franjas_seleccionadas:
                nueva_disponibilidad[dia] = franjas_seleccionadas
            elif dia in self.disponibilidad_actualizada and not franjas_seleccionadas:
                nueva_disponibilidad[dia] = []
        self.disponibilidad_actualizada = nueva_disponibilidad
        self.destroy()


class VentanaProfesor(tk.Toplevel):
    """
    Ventana para registrar o editar la información de un profesor.
    """

    def __init__(self, parent_frame, controller, modo="registrar", profesor_data=None):
        # profesor_data es una lista: [cedula, nombre, apellido, disponibilidad_dict]
        super().__init__(controller)
        self.parent_frame = parent_frame  # ProfesoresFrame
        self.modo = modo
        self.profesor_original_cedula = str(
            profesor_data[0]) if profesor_data and self.modo == "editar" else None

        if self.modo == "editar" and profesor_data and len(profesor_data) > 3 and isinstance(profesor_data[3], dict):
            self.disponibilidad_para_editar = profesor_data[3].copy()
        else:
            # Para modo registro o si no hay datos de disponibilidad, iniciar como dict vacío
            # VentanaGestionDisponibilidad lo manejará correctamente.
            self.disponibilidad_para_editar = {}

        self.title("Registrar Profesor" if self.modo ==
                   "registrar" else "Editar Profesor")
        self.geometry("450x320")
        self.transient(controller)
        self.grab_set()
        self.configure(bg=ttk.Style().lookup('TFrame', 'background'))

        frame_form = ttk.Frame(self, padding="15")
        frame_form.pack(expand=True, fill="both")

        labels_text = ["Cédula:", "Nombre:", "Apellido:"]
        self.entries = {}
        self.entry_keys_map = {"Cédula:": "cedula",
                               "Nombre:": "nombre", "Apellido:": "apellido"}

        for i, text_label in enumerate(labels_text):
            label = ttk.Label(frame_form, text=text_label,
                              font=FUENTE_LABELS_FORMULARIOS)
            label.grid(row=i, column=0, padx=5, pady=8, sticky="w")
            entry_var = tk.StringVar()
            entry_widget = ttk.Entry(
                frame_form, textvariable=entry_var, width=35)
            entry_widget.grid(row=i, column=1, padx=5, pady=8, sticky="ew")

            key_entry = self.entry_keys_map[text_label]
            self.entries[key_entry] = entry_var

            if self.modo == "editar" and profesor_data:
                # profesor_data[0]=cedula, profesor_data[1]=nombre, profesor_data[2]=apellido
                if i < 3:
                    entry_var.set(profesor_data[i])
                if key_entry == "cedula":
                    # La cédula no se puede editar
                    entry_widget.config(state="readonly")

        btn_gestionar_disp = ttk.Button(
            frame_form, text="Gestionar Disponibilidad", command=self._abrir_ventana_gestion_disponibilidad)
        btn_gestionar_disp.grid(row=len(labels_text),
                                column=0, columnspan=2, pady=10)

        frame_form.columnconfigure(1, weight=1)

        frame_botones = ttk.Frame(self, padding="0 10 10 10")
        frame_botones.pack(fill="x", side="bottom")
        frame_botones.columnconfigure(0, weight=1)
        frame_botones.columnconfigure(3, weight=1)

        btn_guardar = ttk.Button(
            frame_botones, text="Guardar", command=self._guardar)
        btn_guardar.grid(row=0, column=1, padx=5, pady=5)

        btn_cancelar = ttk.Button(
            frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.grid(row=0, column=2, padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    def _abrir_ventana_gestion_disponibilidad(self):
        ventana_disp = VentanaGestionDisponibilidad(
            self, self.disponibilidad_para_editar.copy())
        self.wait_window(ventana_disp)

        if hasattr(ventana_disp, 'disponibilidad_actualizada'):
            self.disponibilidad_para_editar = ventana_disp.disponibilidad_actualizada

    def _guardar(self):
        datos_formulario = [
            self.entries["cedula"].get().strip(),
            self.entries["nombre"].get().strip(),
            self.entries["apellido"].get().strip()
        ]
        if not all(datos_formulario):
            messagebox.showwarning(
                "Campos Vacíos", "Cédula, Nombre y Apellido son obligatorios.", parent=self)
            return

        # datos_completos_profesor = [cedula, nombre, apellido, disponibilidad_dict]
        datos_completos_profesor = datos_formulario + \
            [self.disponibilidad_para_editar]

        if self.parent_frame.guardar_datos_profesor(datos_completos_profesor, self.profesor_original_cedula):
            self.destroy()  # Se cierra si el guardado en ProfesoresFrame fue exitoso


class ProfesoresFrame(ttk.Frame):
    """
    Frame principal para la gestión de Profesores (CRUD y visualización).
    """

    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        # Inicializar el repositorio de profesores
        self.teacher_repo = TeacherRepository()  # <--- USA EL REPOSITORIO

        self.profesores_data_actual = []
        self.profesor_seleccionado_id_tree = None  # Cédula del profesor seleccionado

        frame_controles = ttk.Frame(self, style="Controls.TFrame")
        frame_controles.pack(pady=(0, 10), padx=0, fill="x")

        ttk.Label(frame_controles, text="Buscar Profesor:").pack(
            side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._filtrar_profesores_live)
        search_entry = ttk.Entry(
            frame_controles, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5, fill="x", expand=True)

        frame_botones_accion = ttk.Frame(frame_controles)
        frame_botones_accion.pack(side="right", padx=(10, 0))

        btn_registrar = ttk.Button(
            frame_botones_accion, text="Registrar Nuevo", command=self._abrir_ventana_registrar)
        btn_registrar.pack(side="left", padx=(0, 5))

        self.btn_editar = ttk.Button(
            frame_botones_accion, text="Editar", command=self._abrir_ventana_editar, state="disabled")
        self.btn_editar.pack(side="left", padx=5)

        self.btn_eliminar = ttk.Button(
            frame_botones_accion, text="Eliminar", command=self._eliminar_profesor, state="disabled")
        self.btn_eliminar.pack(side="left", padx=(5, 0))

        self.btn_ver_disponibilidad = ttk.Button(
            frame_botones_accion, text="Ver Disponibilidad", command=self._abrir_ventana_disponibilidad, state="disabled")
        self.btn_ver_disponibilidad.pack(side="left", padx=(5, 0))

        cols = ("Cédula", "Nombre", "Apellido")
        self.tree_profesores = ttk.Treeview(
            self, columns=cols, show="headings", selectmode="browse")

        self.tree_profesores.tag_configure('par', background=COLOR_FILA_PAR)
        self.tree_profesores.tag_configure(
            'impar', background=COLOR_FILA_IMPAR)

        col_widths = {"Cédula": 120, "Nombre": 250, "Apellido": 250}
        for col in cols:
            self.tree_profesores.heading(col, text=col, anchor="w")
            self.tree_profesores.column(col, width=col_widths.get(col, 150), anchor="w",
                                        stretch=tk.YES if col in ["Nombre", "Apellido"] else tk.NO)

        self.tree_profesores.pack(
            expand=True, fill="both", padx=0, pady=(0, 10), side="left")

        scrollbar_tree_profesores = ttk.Scrollbar(
            self, orient="vertical", command=self.tree_profesores.yview)
        self.tree_profesores.configure(
            yscrollcommand=scrollbar_tree_profesores.set)
        scrollbar_tree_profesores.pack(side="right", fill="y")

        self.tree_profesores.bind(
            "<<TreeviewSelect>>", self._on_profesor_seleccionado)

        self.actualizar_contenido()

    def actualizar_contenido(self):
        """Actualiza la vista de profesores cargando datos desde el repositorio."""
        self.profesores_data_actual = self.teacher_repo.get_all_teachers()  # <--- USA EL REPOSITORIO

        if self.tree_profesores.selection():
            self.tree_profesores.selection_remove(
                self.tree_profesores.selection())
        self.profesor_seleccionado_id_tree = None
        self._cargar_profesores_en_treeview(self.profesores_data_actual)
        self._actualizar_estado_botones()

    def _cargar_profesores_en_treeview(self, data_a_cargar):
        """Carga o recarga los datos en el widget Treeview."""
        for i in self.tree_profesores.get_children():
            self.tree_profesores.delete(i)

        for idx, profesor_data_completa in enumerate(data_a_cargar):
            profesor_row_display = profesor_data_completa[:3]
            tag = 'par' if idx % 2 == 0 else 'impar'
            self.tree_profesores.insert(
                "", "end", values=profesor_row_display, iid=str(profesor_data_completa[0]), tags=(tag,))

    def _filtrar_profesores_live(self, *args):
        """Filtra los profesores en el Treeview basado en el texto de búsqueda."""
        query = self.search_var.get().lower()
        todos_los_profesores = self.teacher_repo.get_all_teachers()  # <--- USA EL REPOSITORIO

        if not query:
            self.profesores_data_actual = todos_los_profesores
        else:
            self.profesores_data_actual = [
                list(prof_data) for prof_data in todos_los_profesores
                if any(query in str(val).lower() for val in prof_data[:3])
            ]
        self._cargar_profesores_en_treeview(self.profesores_data_actual)

        if self.profesor_seleccionado_id_tree and \
           not self.tree_profesores.exists(self.profesor_seleccionado_id_tree):
            self.profesor_seleccionado_id_tree = None
        self._actualizar_estado_botones()

    def _on_profesor_seleccionado(self, event=None):
        """Manejador para cuando un profesor es seleccionado en el Treeview."""
        seleccion = self.tree_profesores.selection()
        self.profesor_seleccionado_id_tree = seleccion[0] if seleccion else None
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self):
        """Habilita o deshabilita los botones según haya selección."""
        estado = "normal" if self.profesor_seleccionado_id_tree else "disabled"
        self.btn_editar.config(state=estado)
        self.btn_eliminar.config(state=estado)
        self.btn_ver_disponibilidad.config(state=estado)

    def _abrir_ventana_registrar(self):
        """Abre la ventana para registrar un nuevo profesor."""
        VentanaProfesor(self, self.controller, modo="registrar")

    def _abrir_ventana_editar(self):
        """Abre la ventana para editar el profesor seleccionado."""
        if not self.profesor_seleccionado_id_tree:
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona un profesor para editar.", parent=self.controller)
            return

        profesor_a_editar_data = self.teacher_repo.get_teacher_by_id(
            self.profesor_seleccionado_id_tree)  # <--- USA EL REPOSITORIO

        if profesor_a_editar_data:
            VentanaProfesor(self, self.controller, modo="editar",
                            profesor_data=profesor_a_editar_data)
        else:
            messagebox.showerror(
                "Error", "No se encontró el profesor seleccionado.", parent=self.controller)
            self.actualizar_contenido()

    def _abrir_ventana_disponibilidad(self):
        """Abre la ventana para ver la disponibilidad del profesor seleccionado."""
        if not self.profesor_seleccionado_id_tree:
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona un profesor.", parent=self.controller)
            return

        prof_data_completa = self.teacher_repo.get_teacher_by_id(
            self.profesor_seleccionado_id_tree)  # <--- USA EL REPOSITORIO

        if prof_data_completa:
            nombre_completo = f"{prof_data_completa[1]} {
                prof_data_completa[2]}"
            disponibilidad_dict = prof_data_completa[3] if len(
                prof_data_completa) > 3 and isinstance(prof_data_completa[3], dict) else {}
            VentanaDisponibilidad(
                self.controller, nombre_completo, disponibilidad_dict)
        else:
            messagebox.showerror(
                "Error", "No se encontró el profesor.", parent=self.controller)
            self.actualizar_contenido()

    def _eliminar_profesor(self):
        """Elimina el profesor seleccionado del repositorio y actualiza la vista."""
        if not self.profesor_seleccionado_id_tree:
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona un profesor para eliminar.", parent=self.controller)
            return

        if messagebox.askyesno("Confirmar Eliminación",
                               f"¿Está seguro de que desea eliminar al profesor con Cédula {
                                   self.profesor_seleccionado_id_tree}?",
                               parent=self.controller):
            # <--- USA EL REPOSITORIO
            if self.teacher_repo.delete_teacher(self.profesor_seleccionado_id_tree):
                messagebox.showinfo(
                    "Eliminado", "Profesor eliminado correctamente.", parent=self.controller)
                self.actualizar_contenido()
                if hasattr(self.controller, 'frames') and 'ClasesFrame' in self.controller.frames:
                    # Asumiendo que ClasesFrame también necesita actualizarse
                    if hasattr(self.controller.frames['ClasesFrame'], 'actualizar_combobox_profesores'):
                        self.controller.frames['ClasesFrame'].actualizar_combobox_profesores(
                        )
                    elif hasattr(self.controller.frames['ClasesFrame'], 'actualizar_contenido'):
                        self.controller.frames['ClasesFrame'].actualizar_contenido(
                        )

            else:
                messagebox.showerror(
                    "Error", "No se pudo eliminar el profesor.", parent=self.controller)
                self.actualizar_contenido()

    def guardar_datos_profesor(self, datos_profesor_completos, cedula_original=None):
        """
        Guarda los datos del profesor (nuevo o editado) usando el TeacherRepository.
        Maneja la lógica de mostrar mensajes al usuario y actualiza la UI.
        Retorna True si la operación fue exitosa (y VentanaProfesor puede cerrarse), False si no.
        """
        nueva_cedula = str(datos_profesor_completos[0])

        active_toplevel = self
        if self.controller and hasattr(self.controller, 'winfo_children'):
            for child_window in self.controller.winfo_children():
                if isinstance(child_window, tk.Toplevel) and child_window.grab_status() != "none":
                    active_toplevel = child_window
                    break

        operacion_exitosa = False
        if cedula_original:
            if nueva_cedula != str(cedula_original) and self.teacher_repo.teacher_id_exists(nueva_cedula):
                messagebox.showerror("Error de Validación",
                                     f"La Cédula '{
                                         nueva_cedula}' ya existe. No se puede cambiar la cédula a una existente.",
                                     parent=active_toplevel)
                return False

            if self.teacher_repo.update_teacher(cedula_original, datos_profesor_completos):
                operacion_exitosa = True
            else:
                messagebox.showerror(
                    "Error", "No se pudo actualizar el profesor.", parent=active_toplevel)
        else:
            if self.teacher_repo.teacher_id_exists(nueva_cedula):
                messagebox.showerror("Error de Validación",
                                     f"La Cédula '{
                                         nueva_cedula}' ya existe para otro profesor.",
                                     parent=active_toplevel)
                return False

            if self.teacher_repo.add_teacher(datos_profesor_completos):
                operacion_exitosa = True
            else:
                messagebox.showerror(
                    "Error", "No se pudo registrar el profesor.", parent=active_toplevel)

        if operacion_exitosa:
            messagebox.showinfo(
                "Éxito", "Profesor guardado correctamente.", parent=active_toplevel)
            self.actualizar_contenido()

            if self.tree_profesores.exists(nueva_cedula):
                self.tree_profesores.selection_set(nueva_cedula)
                self.tree_profesores.focus(nueva_cedula)
                self.tree_profesores.see(nueva_cedula)
                self.profesor_seleccionado_id_tree = nueva_cedula
            else:
                self.profesor_seleccionado_id_tree = None

            self._actualizar_estado_botones()

            if hasattr(self.controller, 'frames') and 'ClasesFrame' in self.controller.frames:
                # Asumiendo que ClasesFrame también necesita actualizarse
                if hasattr(self.controller.frames['ClasesFrame'], 'actualizar_combobox_profesores'):
                    self.controller.frames['ClasesFrame'].actualizar_combobox_profesores(
                    )
                elif hasattr(self.controller.frames['ClasesFrame'], 'actualizar_contenido'):
                    self.controller.frames['ClasesFrame'].actualizar_contenido(
                    )
            return True

        return False
