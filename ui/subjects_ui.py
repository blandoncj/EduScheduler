
import tkinter as tk
from tkinter import ttk, messagebox
import uuid  # VentanaMateria usa uuid
from ui.config_ui import (COLOR_FILA_PAR, COLOR_FILA_IMPAR,
                          FRANJAS_HORARIAS_MATERIA, FUENTE_GENERAL)
from repositories.subject_repository import SubjectRepository


class VentanaMateria(tk.Toplevel):
    def __init__(self, parent_frame, controller, modo="registrar", materia_data=None):
        super().__init__(controller)
        self.parent_frame = parent_frame
        self.controller = controller
        self.modo = modo
        self.materia_original_id = str(
            materia_data[0]) if materia_data and self.modo == "editar" else None

        self.profesores_listos = []
        self._cargar_profesores_para_combobox()

        self.title("Registrar Materia" if self.modo ==
                   "registrar" else "Editar Materia")
        self.geometry("480x300")
        self.transient(controller)
        self.grab_set()
        self.configure(bg=ttk.Style().lookup('TFrame', 'background'))

        frame_form = ttk.Frame(self, padding="15")
        frame_form.pack(expand=True, fill="both")

        self.id_var = tk.StringVar()
        if self.modo == "registrar":
            self.id_var.set(str(uuid.uuid4())[:8].upper())
        elif materia_data:
            self.id_var.set(materia_data[0])

        current_row = 0
        ttk.Label(frame_form, text="Nombre Materia:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.nombre_var = tk.StringVar()
        nombre_entry = ttk.Entry(
            frame_form, textvariable=self.nombre_var, width=38, font=FUENTE_GENERAL)
        nombre_entry.grid(row=current_row, column=1,
                          padx=5, pady=7, sticky="ew")
        if self.modo == "editar" and materia_data:
            self.nombre_var.set(materia_data[1])

        current_row += 1
        ttk.Label(frame_form, text="Intensidad (Horas):", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.intensidad_var = tk.IntVar()
        intensidad_combobox = ttk.Combobox(frame_form, textvariable=self.intensidad_var, values=[
                                           2, 3, 4], state="readonly", width=36, font=FUENTE_GENERAL)
        intensidad_combobox.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")
        if self.modo == "editar" and materia_data and len(materia_data) > 2:
            self.intensidad_var.set(materia_data[2])
        else:
            self.intensidad_var.set(2)

        current_row += 1
        self.requiere_sistemas_var = tk.BooleanVar()
        sistemas_check = ttk.Checkbutton(
            frame_form, text="Requiere Sala de Sistemas", variable=self.requiere_sistemas_var)
        sistemas_check.grid(row=current_row, column=0,
                            columnspan=2, padx=5, pady=7, sticky="w")
        if self.modo == "editar" and materia_data and len(materia_data) > 3:
            self.requiere_sistemas_var.set(materia_data[3])

        current_row += 1
        ttk.Label(frame_form, text="Profesor Asignado:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.profesor_asignado_var = tk.StringVar()
        self.profesor_asignado_combobox = ttk.Combobox(
            frame_form, textvariable=self.profesor_asignado_var, width=36, state="readonly", font=FUENTE_GENERAL)
        self.profesor_asignado_combobox.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")

        self.profesor_asignado_combobox['values'] = [
            p_display for p_id, p_display in self.profesores_listos]

        if self.modo == "editar" and materia_data and len(materia_data) > 4 and materia_data[4]:
            prof_display = self._get_display_val_from_id(
                materia_data[4], self.profesores_listos)
            if prof_display:
                self.profesor_asignado_var.set(prof_display)
        elif self.profesores_listos:
            self.profesor_asignado_var.set(self.profesores_listos[0][1])

        current_row += 1
        ttk.Label(frame_form, text="Franja Horaria Materia:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.franja_materia_var = tk.StringVar()
        franja_materia_combobox = ttk.Combobox(
            frame_form, textvariable=self.franja_materia_var, values=FRANJAS_HORARIAS_MATERIA,
            state="readonly", width=36, font=FUENTE_GENERAL)
        franja_materia_combobox.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")
        if self.modo == "editar" and materia_data and len(materia_data) > 5 and materia_data[5]:
            self.franja_materia_var.set(materia_data[5])
        elif FRANJAS_HORARIAS_MATERIA:
            self.franja_materia_var.set(FRANJAS_HORARIAS_MATERIA[0])

        current_row += 1
        frame_form.columnconfigure(1, weight=1)

        frame_botones = ttk.Frame(self, padding="15 10 10 10")
        frame_botones.pack(fill="x", side="bottom")
        frame_botones.columnconfigure(0, weight=1)
        frame_botones.columnconfigure(3, weight=1)

        btn_guardar = ttk.Button(
            frame_botones, text="Guardar", command=self._guardar_materia)
        btn_guardar.grid(row=0, column=1, padx=5, pady=5)

        btn_cancelar = ttk.Button(
            frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.grid(row=0, column=2, padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    def _cargar_profesores_para_combobox(self):
        """
        Carga la lista de profesores (ID, Nombre Completo) para el ComboBox.
        Obtiene los datos del TeacherRepository a través de ProfesoresFrame.
        """
        self.profesores_listos = []
        prof_frame = self.controller.frames.get('ProfesoresFrame')
        # Asegurarse que ProfesoresFrame y su teacher_repo existen
        if prof_frame and hasattr(prof_frame, 'teacher_repo') and prof_frame.teacher_repo is not None:
            todos_los_profesores_data = prof_frame.teacher_repo.get_all_teachers()
            # teacher_repo.get_all_teachers() devuelve [[id_card, first_name, last_name, availability_dict], ...]
            for prof_data in todos_los_profesores_data:
                if len(prof_data) >= 3:
                    id_prof = str(prof_data[0])
                    nombre_completo = f"{prof_data[1]} {prof_data[2]}"
                    self.profesores_listos.append((id_prof, nombre_completo))
        else:
            print("Advertencia (VentanaMateria): No se pudo acceder a ProfesoresFrame o su teacher_repo para cargar profesores.")

    def _get_id_from_display(self, display_val, lista_de_tuplas, item_index_for_id=0, item_index_for_display=1):
        if not display_val:
            return None
        for item_tupla in lista_de_tuplas:
            if len(item_tupla) > max(item_index_for_id, item_index_for_display) and \
               item_tupla[item_index_for_display] == display_val:
                return item_tupla[item_index_for_id]
        return None

    def _get_display_val_from_id(self, id_val, lista_de_tuplas, item_index_for_id=0, item_index_for_display=1):
        if not id_val:
            return None
        for item_tupla in lista_de_tuplas:
            if len(item_tupla) > max(item_index_for_id, item_index_for_display) and \
               str(item_tupla[item_index_for_id]) == str(id_val):
                return item_tupla[item_index_for_display]
        return None

    def _guardar_materia(self):
        id_val = self.id_var.get().strip()
        nombre_val = self.nombre_var.get().strip()
        try:
            intensidad_val = self.intensidad_var.get()
        except tk.TclError:
            messagebox.showwarning(
                "Dato Inválido", "La intensidad horaria debe ser un número.", parent=self)
            return

        requiere_sistemas_val = self.requiere_sistemas_var.get()
        profesor_display_val = self.profesor_asignado_var.get()

        id_profesor_asignado = self._get_id_from_display(
            profesor_display_val, self.profesores_listos)

        franja_materia_val = self.franja_materia_var.get()

        if not nombre_val:
            messagebox.showwarning(
                "Campo Vacío", "El Nombre de la materia es obligatorio.", parent=self)
            return
        if intensidad_val not in [2, 3, 4]:
            messagebox.showwarning(
                "Dato Inválido", "La intensidad horaria debe ser 2, 3 o 4.", parent=self)
            return
        # Permitir no asignar profesor si no hay profesores en la lista
        if not id_profesor_asignado and self.profesores_listos:
            messagebox.showwarning(
                "Campo Vacío", "Debe seleccionar un profesor asignado.", parent=self)
            return
        if not franja_materia_val:
            messagebox.showwarning(
                "Campo Vacío", "Debe seleccionar una franja horaria para la materia.", parent=self)
            return

        datos_procesados = [id_val, nombre_val, intensidad_val,
                            requiere_sistemas_val, id_profesor_asignado, franja_materia_val]

        if self.parent_frame.guardar_datos_materia(datos_procesados, self.materia_original_id):
            self.destroy()


class MateriasFrame(ttk.Frame):
    """
    Frame principal para la gestión de Materias (CRUD y visualización).
    """

    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        # Inicializar el repositorio de materias
        self.subject_repo = SubjectRepository()  # <--- USA EL REPOSITORIO

        self.materias_data_actual = []
        # ID de la materia seleccionada (UUID)
        self.materia_seleccionada_id_tree = None

        frame_controles = ttk.Frame(self, style="Controls.TFrame")
        frame_controles.pack(pady=(0, 10), padx=0, fill="x")

        ttk.Label(frame_controles, text="Buscar Materia:").pack(
            side="left", padx=(0, 5))
        self.search_var_materia = tk.StringVar()
        self.search_var_materia.trace_add("write", self._filtrar_materias_live)
        search_entry_materia = ttk.Entry(
            frame_controles, textvariable=self.search_var_materia, width=30)
        search_entry_materia.pack(side="left", padx=5, fill="x", expand=True)

        frame_botones_accion = ttk.Frame(frame_controles)
        frame_botones_accion.pack(side="right", padx=(10, 0))

        btn_registrar_materia = ttk.Button(
            frame_botones_accion, text="Registrar Nueva", command=self._abrir_ventana_registrar_materia)
        btn_registrar_materia.pack(side="left", padx=(0, 5))

        self.btn_editar_materia = ttk.Button(
            frame_botones_accion, text="Editar", command=self._abrir_ventana_editar_materia, state="disabled")
        self.btn_editar_materia.pack(side="left", padx=5)

        self.btn_eliminar_materia = ttk.Button(
            frame_botones_accion, text="Eliminar", command=self._eliminar_materia, state="disabled")
        self.btn_eliminar_materia.pack(side="left", padx=(5, 0))

        cols_materias = ("ID", "Nombre", "Int. (Hrs)", "Sist?",
                         "Profesor Asignado", "Franja Materia")
        self.tree_materias = ttk.Treeview(
            self, columns=cols_materias, show="headings", selectmode="browse")

        self.tree_materias.tag_configure('par', background=COLOR_FILA_PAR)
        self.tree_materias.tag_configure('impar', background=COLOR_FILA_IMPAR)

        col_widths_materias = {"ID": 80, "Nombre": 220, "Int. (Hrs)": 70,
                               "Sist?": 50, "Profesor Asignado": 180, "Franja Materia": 100}
        col_anchors_materias = {"ID": "w", "Nombre": "w", "Int. (Hrs)": "center",
                                "Sist?": "center", "Profesor Asignado": "w", "Franja Materia": "center"}
        col_stretches_materias = {"ID": tk.NO, "Nombre": tk.YES, "Int. (Hrs)": tk.NO,
                                  "Sist?": tk.NO, "Profesor Asignado": tk.YES, "Franja Materia": tk.NO}

        for col in cols_materias:
            self.tree_materias.heading(
                col, text=col, anchor=col_anchors_materias.get(col, "w"))
            self.tree_materias.column(col, width=col_widths_materias.get(col, 120),
                                      anchor=col_anchors_materias.get(
                                          col, "w"),
                                      stretch=col_stretches_materias.get(col, tk.NO))

        self.tree_materias.pack(expand=True, fill="both",
                                padx=0, pady=(0, 10), side="left")

        scrollbar_materias = ttk.Scrollbar(
            self, orient="vertical", command=self.tree_materias.yview)
        self.tree_materias.configure(yscrollcommand=scrollbar_materias.set)
        scrollbar_materias.pack(side="right", fill="y")

        self.tree_materias.bind("<<TreeviewSelect>>",
                                self._on_materia_seleccionada)

        self.actualizar_contenido()

    def _get_nombre_profesor_para_materia(self, id_profesor):
        """Obtiene el nombre completo de un profesor dado su ID (cédula)."""
        if not id_profesor:
            return "N/A"  # Si no hay ID de profesor, no se puede buscar

        prof_frame = self.controller.frames.get('ProfesoresFrame')
        # Asegurarse que ProfesoresFrame y su teacher_repo existen
        if prof_frame and hasattr(prof_frame, 'teacher_repo') and prof_frame.teacher_repo is not None:
            prof_data_list = prof_frame.teacher_repo.get_teacher_by_id(
                id_profesor)
            # teacher_repo.get_teacher_by_id devuelve [id_card, first_name, last_name, availability_dict]
            # Verificar que tenemos al menos id, nombre, apellido
            if prof_data_list and len(prof_data_list) >= 3:
                # Nombre Apellido
                return f"{prof_data_list[1]} {prof_data_list[2]}"
        else:
            print(
                "Advertencia (MateriasFrame): No se pudo acceder a ProfesoresFrame o su teacher_repo.")
        return "Prof. Desconocido"  # O "N/A" si no se encuentra o hay error

    def actualizar_contenido(self):
        """Actualiza la vista de materias cargando datos desde el repositorio."""
        self.materias_data_actual = self.subject_repo.get_all_subjects()  # <--- USA EL REPOSITORIO

        if self.tree_materias.selection():
            self.tree_materias.selection_remove(self.tree_materias.selection())
        self.materia_seleccionada_id_tree = None
        self._actualizar_estado_botones_materia()
        self._cargar_materias_en_treeview(self.materias_data_actual)

    def _cargar_materias_en_treeview(self, data_a_cargar):
        """Carga o recarga los datos en el widget Treeview."""
        for i in self.tree_materias.get_children():
            self.tree_materias.delete(i)

        for idx, materia_row_data in enumerate(data_a_cargar):
            visual_row = list(materia_row_data)

            if len(visual_row) > 3:  # Índice 3: requires_lab
                visual_row[3] = "Sí" if materia_row_data[3] else "No"
            else:
                visual_row.append("N/A")  # Placeholder si falta

            if len(visual_row) > 4:  # Índice 4: assigned_teacher_id
                visual_row[4] = self._get_nombre_profesor_para_materia(
                    materia_row_data[4])
            else:
                visual_row.append("N/A")

            if len(visual_row) > 5:  # Índice 5: time_slot
                visual_row[5] = materia_row_data[5] if materia_row_data[5] else "N/A"
            else:
                visual_row.append("N/A")

            # Asegurar que visual_row tenga la longitud esperada por las columnas del treeview
            # Esto es una salvaguarda si los datos del repo no son consistentes.
            num_cols_tree = len(self.tree_materias["columns"])
            while len(visual_row) < num_cols_tree:
                visual_row.append("N/A")

            tag = 'par' if idx % 2 == 0 else 'impar'
            self.tree_materias.insert(
                "", "end", values=visual_row[:num_cols_tree], iid=str(materia_row_data[0]), tags=(tag,))

    def _filtrar_materias_live(self, *args):
        """Filtra las materias en el Treeview basado en el texto de búsqueda."""
        query = self.search_var_materia.get().lower()
        todas_las_materias = self.subject_repo.get_all_subjects()  # <--- USA EL REPOSITORIO

        if not query:
            self.materias_data_actual = todas_las_materias
        else:
            self.materias_data_actual = []
            for m_data in todas_las_materias:
                nombre_prof_str = self._get_nombre_profesor_para_materia(
                    m_data[4] if len(m_data) > 4 else None).lower()

                if query in str(m_data[0]).lower() or \
                   query in str(m_data[1]).lower() or \
                   query in nombre_prof_str or \
                   (len(m_data) > 5 and query in str(m_data[5]).lower()):
                    self.materias_data_actual.append(list(m_data))

        self._cargar_materias_en_treeview(self.materias_data_actual)

        if self.materia_seleccionada_id_tree and \
           not self.tree_materias.exists(self.materia_seleccionada_id_tree):
            self.materia_seleccionada_id_tree = None
        self._actualizar_estado_botones_materia()

    def _on_materia_seleccionada(self, event=None):
        """Manejador para cuando una materia es seleccionada en el Treeview."""
        seleccion = self.tree_materias.selection()
        self.materia_seleccionada_id_tree = seleccion[0] if seleccion else None
        self._actualizar_estado_botones_materia()

    def _actualizar_estado_botones_materia(self):
        """Habilita o deshabilita los botones según haya selección."""
        estado = "normal" if self.materia_seleccionada_id_tree else "disabled"
        self.btn_editar_materia.config(state=estado)
        self.btn_eliminar_materia.config(state=estado)

    def _abrir_ventana_registrar_materia(self):
        """Abre la ventana para registrar una nueva materia."""
        VentanaMateria(self, self.controller, modo="registrar")

    def _abrir_ventana_editar_materia(self):
        """Abre la ventana para editar la materia seleccionada."""
        if not self.materia_seleccionada_id_tree:
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona una materia para editar.", parent=self.controller)
            return

        materia_a_editar_data = self.subject_repo.get_subject_by_id(
            self.materia_seleccionada_id_tree)  # <--- USA EL REPOSITORIO

        if materia_a_editar_data:
            VentanaMateria(self, self.controller, modo="editar",
                           materia_data=materia_a_editar_data)
        else:
            messagebox.showerror(
                "Error", "No se encontró la materia seleccionada.", parent=self.controller)
            self.actualizar_contenido()

    def _eliminar_materia(self):
        """Elimina la materia seleccionada del repositorio y actualiza la vista."""
        if not self.materia_seleccionada_id_tree:
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona una materia para eliminar.", parent=self.controller)
            return

        if messagebox.askyesno("Confirmar Eliminación",
                               f"¿Está seguro de que desea eliminar la materia con ID {
                                   self.materia_seleccionada_id_tree}?",
                               parent=self.controller):
            # <--- USA EL REPOSITORIO
            if self.subject_repo.delete_subject(self.materia_seleccionada_id_tree):
                messagebox.showinfo(
                    "Eliminado", "Materia eliminada correctamente.", parent=self.controller)
                self.actualizar_contenido()
                if hasattr(self.controller, 'frames') and 'ClasesFrame' in self.controller.frames:
                    if hasattr(self.controller.frames['ClasesFrame'], 'actualizar_combobox_materias'):
                        self.controller.frames['ClasesFrame'].actualizar_combobox_materias(
                        )
                    elif hasattr(self.controller.frames['ClasesFrame'], 'actualizar_contenido'):
                        self.controller.frames['ClasesFrame'].actualizar_contenido(
                        )
            else:
                messagebox.showerror(
                    "Error", "No se pudo eliminar la materia.", parent=self.controller)
                self.actualizar_contenido()

    def guardar_datos_materia(self, datos_materia_procesados, id_materia_original=None):
        """
        Guarda los datos de la materia (nueva o editada) usando el SubjectRepository.
        Maneja la lógica de mostrar mensajes al usuario y actualiza la UI.
        Retorna True si la operación fue exitosa (y VentanaMateria puede cerrarse), False si no.
        """
        nuevo_id_materia = str(datos_materia_procesados[0])

        active_toplevel = self
        if self.controller and hasattr(self.controller, 'winfo_children'):
            for child_window in self.controller.winfo_children():
                if isinstance(child_window, tk.Toplevel) and child_window.grab_status() != "none":
                    active_toplevel = child_window
                    break

        operacion_exitosa = False
        if id_materia_original:  # Modo edición
            if nuevo_id_materia != str(id_materia_original):
                messagebox.showerror("Error de Lógica",
                                     "El ID de la materia no puede cambiar durante la edición.",
                                     parent=active_toplevel)
                return False

            # <--- USA EL REPOSITORIO
            if self.subject_repo.update_subject(id_materia_original, datos_materia_procesados):
                operacion_exitosa = True
            else:
                messagebox.showerror(
                    "Error", "No se pudo actualizar la materia.", parent=active_toplevel)
        else:  # Modo registro
            # <--- USA EL REPOSITORIO
            if self.subject_repo.subject_id_exists(nuevo_id_materia):
                messagebox.showerror("Error de Validación",
                                     f"El ID de materia '{
                                         nuevo_id_materia}' ya existe (esto no debería ocurrir con UUIDs).",
                                     parent=active_toplevel)
                return False

            # <--- USA EL REPOSITORIO
            if self.subject_repo.add_subject(datos_materia_procesados):
                operacion_exitosa = True
            else:
                messagebox.showerror(
                    "Error", "No se pudo registrar la materia.", parent=active_toplevel)

        if operacion_exitosa:
            messagebox.showinfo(
                "Éxito", "Materia guardada correctamente.", parent=active_toplevel)
            self.actualizar_contenido()

            if self.tree_materias.exists(nuevo_id_materia):
                self.tree_materias.selection_set(nuevo_id_materia)
                self.tree_materias.focus(nuevo_id_materia)
                self.tree_materias.see(nuevo_id_materia)
                self.materia_seleccionada_id_tree = nuevo_id_materia
            else:
                self.materia_seleccionada_id_tree = None

            self._actualizar_estado_botones_materia()

            if hasattr(self.controller, 'frames') and 'ClasesFrame' in self.controller.frames:
                if hasattr(self.controller.frames['ClasesFrame'], 'actualizar_combobox_materias'):
                    self.controller.frames['ClasesFrame'].actualizar_combobox_materias(
                    )
                elif hasattr(self.controller.frames['ClasesFrame'], 'actualizar_contenido'):
                    self.controller.frames['ClasesFrame'].actualizar_contenido(
                    )
            return True

        return False
