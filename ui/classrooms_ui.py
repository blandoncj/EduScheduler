import tkinter as tk
from tkinter import ttk, messagebox
from ui.config_ui import COLOR_FILA_PAR, COLOR_FILA_IMPAR, BLOQUES_SALON
from repositories.classroom_repository import ClassroomRepository


class ClassroomWindow(tk.Toplevel):
    """
    Ventana para registrar o editar la información de un salón (classroom).
    """

    def __init__(
        self,
        parent_frame,
        controller,
        mode="registrar",  # 'registrar' o 'editar'
        # Lista: [numero, bloque, capacidad, es_lab] para editar
        classroom_data=None
    ):
        super().__init__(controller)
        self.parent_frame = parent_frame  # ClassroomsFrame
        self.mode = mode

        self.salon_numero_original = None
        # Para guardar el bloque original en modo edición
        self.salon_bloque_original = None

        if self.mode == "editar" and classroom_data:
            self.salon_numero_original = str(classroom_data[0])
            if len(classroom_data) > 1:  # Asegurar que el bloque está presente
                self.salon_bloque_original = str(classroom_data[1])

        self.title("Registrar Salón" if self.mode ==
                   "registrar" else "Editar Salón")
        self.geometry("420x320")
        self.transient(controller)
        self.grab_set()
        self.configure(bg=ttk.Style().lookup(
            'TFrame', 'background'))

        frame_form = ttk.Frame(self, padding="15")
        frame_form.pack(expand=True, fill="both")

        current_row = 0
        # Campo: Número Salón
        ttk.Label(frame_form, text="Número Salón:").grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.numero_var = tk.StringVar()
        numero_entry = ttk.Entry(
            frame_form, textvariable=self.numero_var, width=35)
        numero_entry.grid(row=current_row, column=1,
                          padx=5, pady=7, sticky="ew")
        if self.mode == "editar" and classroom_data:
            self.numero_var.set(classroom_data[0])

        current_row += 1
        # Campo: Bloque
        ttk.Label(frame_form, text="Bloque:").grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.bloque_var = tk.StringVar()
        bloque_combobox = ttk.Combobox(
            frame_form,
            textvariable=self.bloque_var,
            values=BLOQUES_SALON,  # Definido en ui.config_ui
            state="readonly", width=33
        )
        bloque_combobox.grid(row=current_row, column=1,
                             padx=5, pady=7, sticky="ew")
        if self.mode == "editar" and classroom_data and len(classroom_data) > 1:
            self.bloque_var.set(classroom_data[1])
        elif BLOQUES_SALON:  # Valor por defecto para registro
            self.bloque_var.set(BLOQUES_SALON[0])

        current_row += 1
        # Campo: Capacidad
        ttk.Label(frame_form, text="Capacidad:").grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.capacidad_var = tk.IntVar()
        default_capacidad = 25
        if self.mode == "editar" and classroom_data and len(classroom_data) > 2 and classroom_data[2] is not None:
            try:
                cap = int(classroom_data[2])
                default_capacidad = cap if cap > 0 else default_capacidad
            except (ValueError, TypeError):
                pass

        capacidad_spinbox = ttk.Spinbox(
            frame_form,
            from_=1,
            to=200,
            textvariable=self.capacidad_var, width=33
        )
        self.capacidad_var.set(default_capacidad)
        capacidad_spinbox.grid(row=current_row, column=1,
                               padx=5, pady=7, sticky="ew")

        current_row += 1
        # Campo: Es Sala de Sistemas (Laboratorio)
        self.es_sistemas_var = tk.BooleanVar()
        sistemas_check = ttk.Checkbutton(
            frame_form,
            text="Es Sala de Sistemas",
            variable=self.es_sistemas_var
        )
        sistemas_check.grid(row=current_row, column=0,
                            columnspan=2, padx=5, pady=7, sticky="w")
        if self.mode == "editar" and classroom_data and len(classroom_data) > 3:
            self.es_sistemas_var.set(bool(classroom_data[3]))

        current_row += 1
        frame_form.columnconfigure(1, weight=1)

        frame_botones = ttk.Frame(self, padding="15 10 10 10")
        frame_botones.pack(fill="x", side="bottom")
        frame_botones.columnconfigure(0, weight=1)
        frame_botones.columnconfigure(3, weight=1)

        btn_cancelar = ttk.Button(
            frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.grid(row=0, column=2, padx=5, pady=5)

        btn_guardar = ttk.Button(
            frame_botones, text="Guardar", command=self._guardar_salon)
        btn_guardar.grid(row=0, column=1, padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    def _guardar_salon(self):
        numero_val = self.numero_var.get().strip()
        bloque_val = self.bloque_var.get()
        try:
            capacidad_val = self.capacidad_var.get()
            if capacidad_val <= 0:
                messagebox.showwarning(
                    "Dato Inválido",
                    "La capacidad debe ser un número positivo.",
                    parent=self
                )
                return
        except tk.TclError:
            messagebox.showwarning(
                "Dato Inválido",
                "La capacidad debe ser un número entero.",
                parent=self
            )
            return
        es_sistemas_val = self.es_sistemas_var.get()

        if not numero_val:
            messagebox.showwarning(
                "Campo Vacío",
                "El Número del salón es obligatorio.",
                parent=self
            )
            return
        if not bloque_val:
            messagebox.showwarning(
                "Campo Vacío", "Debe seleccionar un bloque.", parent=self)
            return

        datos_procesados = [numero_val, bloque_val,
                            capacidad_val, es_sistemas_val]

        if self.parent_frame.guardar_datos_salon(
            datos_procesados, self.salon_numero_original, self.salon_bloque_original
        ):
            self.destroy()


class ClassroomsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.classroom_repo = ClassroomRepository()

        # Almacenará el iid COMPUESTO ("numero-bloque")
        self.salon_seleccionado_iid = None
        self.salones_data_actual = []

        frame_controles = ttk.Frame(self, style="Controls.TFrame")
        frame_controles.pack(pady=(0, 10), padx=0, fill="x")

        ttk.Label(
            frame_controles, text="Buscar Salón (Número o Bloque):").pack(
            side="left", padx=(0, 5)
        )
        self.search_var_salon = tk.StringVar()
        self.search_var_salon.trace_add(
            "write", self._filtrar_salones_live)
        search_entry_salon = ttk.Entry(
            frame_controles, textvariable=self.search_var_salon, width=25)
        search_entry_salon.pack(side="left", padx=5, fill="x", expand=True)

        frame_botones_accion = ttk.Frame(frame_controles)
        frame_botones_accion.pack(side="right", padx=(10, 0))

        btn_registrar_salon = ttk.Button(
            frame_botones_accion,
            text="Registrar Nuevo",
            command=self._abrir_ventana_registrar_salon
        )
        btn_registrar_salon.pack(side="left", padx=(0, 5))

        self.btn_editar_salon = ttk.Button(
            frame_botones_accion, text="Editar", command=self._abrir_ventana_editar_salon, state="disabled")
        self.btn_editar_salon.pack(side="left", padx=5)

        self.btn_eliminar_salon = ttk.Button(
            frame_botones_accion, text="Eliminar", command=self._eliminar_salon, state="disabled")
        self.btn_eliminar_salon.pack(side="left", padx=(5, 0))

        cols_salones = ("Número", "Bloque", "Capacidad", "Es Sala de Sistemas")
        self.tree_salones = ttk.Treeview(
            self, columns=cols_salones, show="headings", selectmode="browse")

        self.tree_salones.tag_configure('par', background=COLOR_FILA_PAR)
        self.tree_salones.tag_configure('impar', background=COLOR_FILA_IMPAR)

        col_widths_salones = {"Número": 120, "Bloque": 70,
                              "Capacidad": 80, "Es Sala de Sistemas": 120}
        col_anchors_salones = {"Número": "w", "Bloque": "center",
                               "Capacidad": "center", "Es Sala de Sistemas": "center"}
        col_stretches_salones = {"Número": tk.YES, "Bloque": tk.NO,
                                 "Capacidad": tk.NO, "Es Sala de Sistemas": tk.NO}
        for col in cols_salones:
            self.tree_salones.heading(
                col, text=col, anchor=col_anchors_salones.get(col, "w"))
            self.tree_salones.column(col, width=col_widths_salones.get(
                col, 100), anchor=col_anchors_salones.get(col, "w"),
                stretch=col_stretches_salones.get(col, tk.NO))

        self.tree_salones.pack(expand=True, fill="both",
                               padx=0, pady=(0, 10), side="left")

        scrollbar_salones = ttk.Scrollbar(
            self, orient="vertical", command=self.tree_salones.yview)
        self.tree_salones.configure(yscrollcommand=scrollbar_salones.set)
        scrollbar_salones.pack(side="right", fill="y")

        self.tree_salones.bind("<<TreeviewSelect>>",
                               self._on_salon_seleccionado)

        self.actualizar_contenido()

    def _parse_selected_iid(self):
        """Parsea el iid compuesto ("numero-bloque") y devuelve (numero, bloque)."""
        if not self.salon_seleccionado_iid:
            return None, None
        try:
            numero, bloque = self.salon_seleccionado_iid.rsplit(
                '-', 1)  # rsplit para manejar números con guiones
            return numero, bloque
        except ValueError:
            # Esto podría pasar si el iid no tiene el formato esperado, aunque no debería.
            print(f"Error: IID seleccionado con formato incorrecto: {
                  self.salon_seleccionado_iid}")
            return None, None

    def actualizar_contenido(self):
        self.salones_data_actual = self.classroom_repo.get_all_classrooms()
        if self.tree_salones.selection():
            self.tree_salones.selection_remove(self.tree_salones.selection())
        self.salon_seleccionado_iid = None  # CAMBIADO
        self._actualizar_estado_botones_salon()
        self._cargar_salones_en_treeview(self.salones_data_actual)

    def _cargar_salones_en_treeview(self, data_a_cargar):
        for i in self.tree_salones.get_children():
            self.tree_salones.delete(i)
        for idx, salon_row_data in enumerate(data_a_cargar):
            visual_row = list(salon_row_data)
            if len(visual_row) > 3:
                visual_row[3] = "Sí" if salon_row_data[3] else "No"

            tag = 'par' if idx % 2 == 0 else 'impar'

            # --- CAMBIO CRÍTICO: Generar iid único ---
            numero_salon = str(salon_row_data[0])
            bloque_salon = str(salon_row_data[1])
            item_iid = f"{numero_salon}-{bloque_salon}"
            # --- FIN CAMBIO CRÍTICO ---

            self.tree_salones.insert(
                # USA item_iid
                "", "end", values=visual_row, iid=item_iid, tags=(tag,))

    def _filtrar_salones_live(self, *args):
        query = self.search_var_salon.get().lower()
        todos_los_salones = self.classroom_repo.get_all_classrooms()
        if not query:
            self.salones_data_actual = todos_los_salones
        else:
            self.salones_data_actual = [
                list(s_data) for s_data in todos_los_salones
                if query in str(s_data[0]).lower() or query in str(s_data[1]).lower()
            ]
        self._cargar_salones_en_treeview(self.salones_data_actual)

        # Verificar si el iid seleccionado sigue existiendo en los items cargados
        if self.salon_seleccionado_iid and not self.tree_salones.exists(self.salon_seleccionado_iid):
            self.salon_seleccionado_iid = None
        self._actualizar_estado_botones_salon()

    def _on_salon_seleccionado(self, event=None):
        seleccion = self.tree_salones.selection()
        # CAMBIADO
        self.salon_seleccionado_iid = seleccion[0] if seleccion else None
        self._actualizar_estado_botones_salon()

    def _actualizar_estado_botones_salon(self):
        estado = "normal" if self.salon_seleccionado_iid else "disabled"  # CAMBIADO
        self.btn_editar_salon.config(state=estado)
        self.btn_eliminar_salon.config(state=estado)

    def _abrir_ventana_registrar_salon(self):
        ClassroomWindow(self, self.controller, mode="registrar")

    def _abrir_ventana_editar_salon(self):
        if not self.salon_seleccionado_iid:  # CAMBIADO
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona un salón para editar.", parent=self.controller)
            return

        numero_seleccionado, bloque_seleccionado = self._parse_selected_iid()  # NUEVO
        if not numero_seleccionado or not bloque_seleccionado:
            messagebox.showerror(
                "Error", "No se pudo obtener la información completa del salón seleccionado.", parent=self.controller)
            return

        salon_a_editar_data = self.classroom_repo.get_classroom(
            numero_seleccionado, bloque_seleccionado)  # USA numero y bloque parseados

        if salon_a_editar_data:
            ClassroomWindow(self, self.controller, mode="editar",
                            classroom_data=salon_a_editar_data)
        else:
            messagebox.showerror(
                "Error", "No se encontró el salón seleccionado en la base de datos.", parent=self.controller)
            self.actualizar_contenido()

    def _eliminar_salon(self):
        if not self.salon_seleccionado_iid:  # CAMBIADO
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona un salón para eliminar.", parent=self.controller)
            return

        numero_seleccionado, bloque_seleccionado = self._parse_selected_iid()  # NUEVO
        if not numero_seleccionado or not bloque_seleccionado:
            messagebox.showerror(
                "Error", "No se pudo obtener la información completa del salón para eliminar.", parent=self.controller)
            return

        if messagebox.askyesno("Confirmar Eliminación",
                               f"¿Está seguro de que desea eliminar el salón número {
                                   numero_seleccionado} del bloque {bloque_seleccionado}?",  # Mensaje actualizado
                               parent=self.controller):
            # USA numero y bloque parseados
            if self.classroom_repo.delete_classroom(numero_seleccionado, bloque_seleccionado):
                messagebox.showinfo(
                    "Eliminado", "Salón eliminado correctamente.", parent=self.controller)
                self.actualizar_contenido()
                if hasattr(self.controller, 'frames') and 'ClasesFrame' in self.controller.frames:
                    if hasattr(self.controller.frames['ClasesFrame'], 'actualizar_por_cambio_salon'):
                        self.controller.frames['ClasesFrame'].actualizar_por_cambio_salon(
                        )
                    elif hasattr(self.controller.frames['ClasesFrame'], 'actualizar_contenido'):
                        self.controller.frames['ClasesFrame'].actualizar_contenido(
                        )
            else:
                messagebox.showerror(
                    "Error", "No se pudo eliminar el salón.", parent=self.controller)
                self.actualizar_contenido()

    def guardar_datos_salon(self, datos_salon_procesados, numero_salon_original=None, bloque_salon_original=None):
        nuevo_numero_salon = str(datos_salon_procesados[0])
        nuevo_bloque_salon = str(datos_salon_procesados[1])

        active_toplevel = self
        if self.controller and hasattr(self.controller, 'winfo_children'):
            for child_window in self.controller.winfo_children():
                if isinstance(child_window, tk.Toplevel) and child_window.grab_status() != "none":
                    active_toplevel = child_window
                    break

        operacion_exitosa = False
        if numero_salon_original is not None and bloque_salon_original is not None:
            if (nuevo_numero_salon != str(numero_salon_original) or nuevo_bloque_salon != str(bloque_salon_original)) and \
               self.classroom_repo.classroom_exists(nuevo_numero_salon, nuevo_bloque_salon):
                messagebox.showerror("Error de Validación",
                                     f"El salón '{nuevo_numero_salon}' en el bloque '{
                                         nuevo_bloque_salon}' ya existe.",
                                     parent=active_toplevel)
                return False

            if self.classroom_repo.update_classroom(numero_salon_original, bloque_salon_original, datos_salon_procesados):
                operacion_exitosa = True
            else:
                messagebox.showerror(
                    "Error", "No se pudo actualizar el salón. Verifique los datos.", parent=active_toplevel)
        else:
            if self.classroom_repo.classroom_exists(nuevo_numero_salon, nuevo_bloque_salon):
                messagebox.showerror("Error de Validación",
                                     f"El salón '{nuevo_numero_salon}' en el bloque '{
                                         nuevo_bloque_salon}' ya existe.",
                                     parent=active_toplevel)
                return False

            if self.classroom_repo.add_classroom(datos_salon_procesados):
                operacion_exitosa = True
            else:
                messagebox.showerror(
                    "Error", "No se pudo registrar el salón. Verifique los datos.", parent=active_toplevel)

        if operacion_exitosa:
            messagebox.showinfo(
                "Éxito", "Salón guardado correctamente.", parent=active_toplevel)
            self.actualizar_contenido()

            # Seleccionar el salón recién guardado/editado usando el iid compuesto
            nuevo_iid = f"{
                nuevo_numero_salon}-{nuevo_bloque_salon}"  # NUEVO iid
            try:
                # CAMBIADO para usar nuevo_iid
                if self.tree_salones.exists(nuevo_iid):
                    self.tree_salones.selection_set(nuevo_iid)
                    self.tree_salones.focus(nuevo_iid)
                    self.tree_salones.see(nuevo_iid)
                    self.salon_seleccionado_iid = nuevo_iid  # CAMBIADO
                else:
                    self.salon_seleccionado_iid = None
            except Exception as e:
                print(
                    f"Advertencia: No se pudo seleccionar el salón en TreeView después de guardar: {e}")
                self.salon_seleccionado_iid = None

            self._actualizar_estado_botones_salon()

            if hasattr(self.controller, 'frames') and 'ClasesFrame' in self.controller.frames:
                if hasattr(self.controller.frames['ClasesFrame'], 'actualizar_por_cambio_salon'):
                    self.controller.frames['ClasesFrame'].actualizar_por_cambio_salon(
                    )
                elif hasattr(self.controller.frames['ClasesFrame'], 'actualizar_contenido'):
                    self.controller.frames['ClasesFrame'].actualizar_contenido(
                    )
            return True

        return False
