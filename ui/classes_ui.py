import tkinter as tk
from tkinter import ttk, messagebox
import uuid
from datetime import datetime, timedelta, date
try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

from ui.config_ui import COLOR_FILA_PAR, COLOR_FILA_IMPAR, FUENTE_GENERAL

from repositories.scheduled_class_repository import ScheduledClassRepository


class VentanaClase(tk.Toplevel):
    def __init__(self, parent_frame, controller, modo="programar", clase_data=None):
        super().__init__(controller)
        self.parent_frame = parent_frame  # ClasesFrame
        self.controller = controller
        self.modo = modo
        self.clase_original_id = str(
            clase_data[0]) if clase_data and self.modo == "editar" else None

        self.title("Programar Nueva Clase" if self.modo ==
                   "programar" else "Editar/Reprogramar Clase")
        self.geometry("550x380")  # Ajustada la altura
        self.transient(controller)
        self.grab_set()
        self.configure(bg=ttk.Style().lookup('TFrame', 'background'))

        frame_form = ttk.Frame(self, padding="15")
        frame_form.pack(expand=True, fill="both")

        self.id_clase_var = tk.StringVar()
        if self.modo == "programar":
            # ID único para la clase
            self.id_clase_var.set(str(uuid.uuid4()).upper())
        elif clase_data:
            self.id_clase_var.set(clase_data[0])

        current_row = 0

        # Profesor
        ttk.Label(frame_form, text="Profesor:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.profesor_var = tk.StringVar()
        self.profesor_combobox = ttk.Combobox(
            frame_form, textvariable=self.profesor_var, width=43, state="readonly", font=FUENTE_GENERAL)
        self.profesor_combobox.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")
        # Formato: [(id_profesor, "Nombre Apellido"), ...]
        self.profesores_listos = []
        self._cargar_profesores_para_combobox()
        current_row += 1

        # Materia
        ttk.Label(frame_form, text="Materia:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.materia_var = tk.StringVar()
        self.materia_combobox = ttk.Combobox(
            frame_form, textvariable=self.materia_var, width=43, state="readonly", font=FUENTE_GENERAL)
        self.materia_combobox.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")
        self.materia_combobox.bind(
            "<<ComboboxSelected>>", self._actualizar_hora_fin_label)
        # Formato: [(id_materia, nombre, intensidad, req_sistemas), ...]
        self.materias_listas = []
        self._cargar_materias_para_combobox()
        current_row += 1

        # Salón
        ttk.Label(frame_form, text="Salón:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.salon_var = tk.StringVar()
        self.salon_combobox = ttk.Combobox(
            frame_form, textvariable=self.salon_var, width=43, state="readonly", font=FUENTE_GENERAL)
        self.salon_combobox.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")
        # Formato: [("id_salon-bloque", capacidad, es_sistemas), ...]
        self.salones_listos = []
        self._cargar_salones_para_combobox()
        current_row += 1

        # Fecha
        ttk.Label(frame_form, text="Fecha:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.fecha_var = tk.StringVar()
        if TKCALENDAR_AVAILABLE:
            self.fecha_entry = DateEntry(frame_form, width=40, textvariable=self.fecha_var,
                                         date_pattern='yyyy-mm-dd', mindate=date.today(),
                                         # readonly para forzar uso de calendario
                                         state="readonly", font=FUENTE_GENERAL)
            self.fecha_entry.grid(row=current_row, column=1,
                                  padx=5, pady=7, sticky="ew")
        else:  # Fallback si tkcalendar no está
            self.fecha_entry_fallback = ttk.Entry(
                frame_form, textvariable=self.fecha_var, width=45, font=FUENTE_GENERAL)
            self.fecha_entry_fallback.grid(
                row=current_row, column=1, padx=5, pady=7, sticky="ew")
            if self.modo == "programar":
                self.fecha_var.set(datetime.now().strftime("%Y-%m-%d"))
        current_row += 1

        # Hora Inicio
        ttk.Label(frame_form, text="Hora Inicio:", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.hora_inicio_var = tk.StringVar()
        horas_disponibles_clase = [
            f"{h:02d}:00" for h in range(7, 22)]  # 7 AM a 9 PM (21:00)

        self.hora_inicio_combobox = ttk.Combobox(
            frame_form, textvariable=self.hora_inicio_var, values=horas_disponibles_clase,
            width=43, state="readonly", font=FUENTE_GENERAL)
        self.hora_inicio_combobox.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")
        self.hora_inicio_combobox.bind(
            "<<ComboboxSelected>>", self._actualizar_hora_fin_label)
        if horas_disponibles_clase and self.modo == "programar":
            self.hora_inicio_var.set(
                horas_disponibles_clase[0])  # Default 07:00
        current_row += 1

        # Hora Fin (Calculada)
        ttk.Label(frame_form, text="Hora Fin (Calculada):", font=FUENTE_GENERAL).grid(
            row=current_row, column=0, padx=5, pady=7, sticky="w")
        self.hora_fin_label_var = tk.StringVar(value="N/A")
        hora_fin_display_label = ttk.Label(
            frame_form, textvariable=self.hora_fin_label_var, font=FUENTE_GENERAL + ("bold",))
        hora_fin_display_label.grid(
            row=current_row, column=1, padx=5, pady=7, sticky="ew")
        current_row += 1

        frame_form.columnconfigure(1, weight=1)

        # Cargar datos si estamos en modo edición
        if self.modo == "editar" and clase_data:
            # clase_data: [id, fecha, hora_inicio, hora_fin, id_materia, id_profesor, id_salon]
            prof_display = self._get_display_val_from_id(
                clase_data[5], self.profesores_listos)
            if prof_display:
                self.profesor_var.set(prof_display)

            materia_display = self._get_display_val_from_id(
                clase_data[4], self.materias_listas, item_index_for_display=1)
            if materia_display:
                self.materia_var.set(materia_display)

            salon_display = self._get_display_val_from_id(
                clase_data[6], self.salones_listos, item_index_for_display=0)
            if salon_display:
                self.salon_var.set(salon_display)

            if TKCALENDAR_AVAILABLE:
                try:
                    fecha_obj_editar = datetime.strptime(
                        clase_data[1], "%Y-%m-%d").date()
                    self.fecha_entry.set_date(fecha_obj_editar)
                except ValueError:
                    # Fallback si el formato es incorrecto
                    self.fecha_var.set(clase_data[1])
            else:
                self.fecha_var.set(clase_data[1])

            self.hora_inicio_var.set(clase_data[2])

        self._actualizar_hora_fin_label()  # Calcular hora fin inicial

        frame_botones = ttk.Frame(self, padding="15 10 10 10")
        frame_botones.pack(fill="x", side="bottom")
        frame_botones.columnconfigure(0, weight=1)
        frame_botones.columnconfigure(3, weight=1)
        btn_guardar = ttk.Button(
            frame_botones, text="Guardar Clase", command=self._guardar_clase)
        btn_guardar.grid(row=0, column=1, padx=7, pady=7)
        btn_cancelar = ttk.Button(
            frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.grid(row=0, column=2, padx=7, pady=7)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    def _cargar_profesores_para_combobox(self):
        self.profesores_listos = []
        prof_frame = self.controller.frames.get('ProfesoresFrame')
        if prof_frame and hasattr(prof_frame, 'teacher_repo'):
            try:
                todos_los_profesores = prof_frame.teacher_repo.get_all_teachers()
                # Formato esperado por get_all_teachers: [[id, nombre, apellido, disponibilidad_dict], ...]
                for p_data in todos_los_profesores:
                    if len(p_data) >= 3:
                        self.profesores_listos.append(
                            (str(p_data[0]), f"{p_data[1]} {p_data[2]}"))
                self.profesor_combobox['values'] = [
                    display for _, display in self.profesores_listos]
            except Exception as e:
                print(f"Error cargando profesores en VentanaClase: {e}")
                self.profesor_combobox['values'] = []
        else:
            self.profesor_combobox['values'] = []
            print(
                "Advertencia (VentanaClase): No se pudo acceder a ProfesoresFrame o su teacher_repo.")

    def _cargar_materias_para_combobox(self):
        self.materias_listas = []
        mat_frame = self.controller.frames.get('MateriasFrame')
        if mat_frame and hasattr(mat_frame, 'subject_repo'):
            try:
                todas_las_materias = mat_frame.subject_repo.get_all_subjects()
                # Formato esperado: [[id, nombre, intensidad, req_sist, id_prof, franja], ...]
                for m_data in todas_las_materias:
                    if len(m_data) >= 4:  # id, nombre, intensidad, req_sist
                        self.materias_listas.append((str(m_data[0]), str(
                            m_data[1]), int(m_data[2]), bool(m_data[3])))
                self.materia_combobox['values'] = [
                    nombre for _, nombre, _, _ in self.materias_listas]
            except Exception as e:
                print(f"Error cargando materias en VentanaClase: {e}")
                self.materia_combobox['values'] = []

        else:
            self.materia_combobox['values'] = []
            print(
                "Advertencia (VentanaClase): No se pudo acceder a MateriasFrame o su subject_repo.")

    def _cargar_salones_para_combobox(self):
        self.salones_listos = []
        sal_frame = self.controller.frames.get('ClassroomsFrame')
        if sal_frame and hasattr(sal_frame, 'classroom_repo'):
            try:
                todos_los_salones = sal_frame.classroom_repo.get_all_classrooms()
                # Formato esperado: [[numero, bloque, capacidad, es_sistemas], ...]
                for s_data in todos_los_salones:
                    if len(s_data) >= 4:
                        id_compuesto = f"{s_data[0]}-{s_data[1]}"
                        self.salones_listos.append(
                            (id_compuesto, int(s_data[2]), bool(s_data[3])))
                self.salon_combobox['values'] = [
                    display_id for display_id, _, _ in self.salones_listos]
            except Exception as e:
                print(f"Error cargando salones en VentanaClase: {e}")
                self.salon_combobox['values'] = []
        else:
            self.salon_combobox['values'] = []
            print(
                "Advertencia (VentanaClase): No se pudo acceder a SalonesFrame o su classroom_repo.")

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

    def _actualizar_hora_fin_label(self, event=None):
        materia_nombre_seleccionada = self.materia_var.get()
        hora_inicio_str = self.hora_inicio_var.get()

        if not materia_nombre_seleccionada or not hora_inicio_str:
            self.hora_fin_label_var.set("N/A")
            return

        # self.materias_listas tiene formato [(id_materia, nombre, intensidad, req_sistemas), ...]
        materia_encontrada_data = next(
            (m_data for m_data in self.materias_listas if m_data[1] == materia_nombre_seleccionada), None)

        if not materia_encontrada_data:
            self.hora_fin_label_var.set("Error: Materia no válida")
            return

        # Intensidad está en el índice 2
        intensidad_materia = materia_encontrada_data[2]

        try:
            hora_inicio_obj = datetime.strptime(hora_inicio_str, "%H:%M")
            hora_fin_obj = hora_inicio_obj + \
                timedelta(hours=intensidad_materia)
            self.hora_fin_label_var.set(hora_fin_obj.strftime("%H:%M"))
        except ValueError:
            self.hora_fin_label_var.set("Error: Hora inicio inválida")

    def _guardar_clase(self):
        id_clase = self.id_clase_var.get()
        profesor_display = self.profesor_var.get()
        materia_display = self.materia_var.get()
        salon_display_compuesto = self.salon_var.get()  # Este es "numero-bloque"

        id_profesor = self._get_id_from_display(
            profesor_display, self.profesores_listos)

        materia_data_sel = next(
            (m for m in self.materias_listas if m[1] == materia_display), None)
        id_materia = materia_data_sel[0] if materia_data_sel else None

        # El ID del salón para guardar es el display compuesto "numero-bloque"
        id_salon_para_guardar = salon_display_compuesto if salon_display_compuesto else None

        fecha_str = self.fecha_var.get()
        hora_inicio_str = self.hora_inicio_var.get().strip()
        hora_fin_str = self.hora_fin_label_var.get().strip()

        if not all([id_clase, id_profesor, id_materia, id_salon_para_guardar, fecha_str, hora_inicio_str]) or \
           hora_fin_str == "N/A" or "Error" in hora_fin_str:
            messagebox.showwarning(
                "Campos Incompletos o Error",
                "Todos los campos son obligatorios y la hora de fin debe ser válida.", parent=self)
            return
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_obj.weekday() == 6:  # 6 es Domingo
                messagebox.showwarning(
                    "Fecha Inválida", "No se pueden programar clases los domingos.", parent=self)
                return

            # Si se usa el Entry de fallback para la fecha (tkcalendar no disponible)
            if not TKCALENDAR_AVAILABLE or not isinstance(self.fecha_entry, DateEntry):
                if fecha_obj < date.today():
                    messagebox.showwarning(
                        "Fecha Inválida", "No se pueden programar clases en fechas pasadas.", parent=self)
                    return
            # Si tkcalendar está disponible, DateEntry ya maneja mindate.

            datetime.strptime(hora_inicio_str, "%H:%M")  # Valida formato
            datetime.strptime(hora_fin_str, "%H:%M")   # Valida formato
        except ValueError:
            messagebox.showwarning("Formato Inválido",
                                   "Fecha u horas tienen formato incorrecto (YYYY-MM-DD, HH:MM).", parent=self)
            return

        datos_clase = [id_clase, fecha_str, hora_inicio_str, hora_fin_str,
                       id_materia, id_profesor, id_salon_para_guardar]

        if self.parent_frame.guardar_datos_clase(datos_clase, self.clase_original_id):
            self.destroy()


class ClasesFrame(ttk.Frame):
    """
    Frame principal para la gestión de Clases Programadas.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        # Inicializar el repositorio de clases programadas
        self.scheduled_class_repo = ScheduledClassRepository()  # <--- USA EL REPOSITORIO

        # ID de la clase seleccionada (UUID)
        self.clase_seleccionada_id_tree = None
        self.filtro_fecha_var = tk.StringVar()
        # self.clases_data_actual se llenará en actualizar_contenido
        self.clases_data_actual = []

        frame_controles_superior = ttk.Frame(self, style="Controls.TFrame")
        frame_controles_superior.pack(pady=(0, 5), padx=0, fill="x")

        ttk.Label(frame_controles_superior, text="Filtrar por Fecha:").pack(
            side="left", padx=(0, 5))
        if TKCALENDAR_AVAILABLE:
            self.filtro_fecha_entry = DateEntry(frame_controles_superior, width=12,
                                                textvariable=self.filtro_fecha_var,
                                                date_pattern='yyyy-mm-dd', state="readonly")
            self.filtro_fecha_entry.pack(side="left", padx=5)
        else:
            self.filtro_fecha_entry_fallback = ttk.Entry(
                frame_controles_superior, textvariable=self.filtro_fecha_var, width=15)
            self.filtro_fecha_entry_fallback.pack(side="left", padx=5)
            # self.filtro_fecha_var.set(datetime.now().strftime("%Y-%m-%d")) # Opcional: default

        btn_filtrar = ttk.Button(
            frame_controles_superior, text="Filtrar", command=self._aplicar_filtro_fecha)
        btn_filtrar.pack(side="left", padx=5)
        btn_mostrar_todas = ttk.Button(
            frame_controles_superior, text="Mostrar Todas", command=self._mostrar_todas_las_clases)
        btn_mostrar_todas.pack(side="left", padx=5)

        frame_botones_accion = ttk.Frame(frame_controles_superior)
        frame_botones_accion.pack(side="right", padx=(10, 0))

        btn_programar_clase = ttk.Button(
            frame_botones_accion, text="Programar Nueva Clase", command=self._abrir_ventana_programar_clase)
        btn_programar_clase.pack(side="left", padx=(0, 5))
        self.btn_editar_clase = ttk.Button(
            frame_botones_accion, text="Editar/Reprogramar", command=self._abrir_ventana_editar_clase, state="disabled")
        self.btn_editar_clase.pack(side="left", padx=5)
        self.btn_cancelar_clase = ttk.Button(
            frame_botones_accion, text="Cancelar Clase", command=self._cancelar_clase, state="disabled")
        self.btn_cancelar_clase.pack(side="left", padx=(5, 0))

        cols_clases = ("ID Clase", "Fecha", "Día", "Hora Inicio",
                       "Hora Fin", "Materia", "Profesor", "Salón")
        self.tree_clases = ttk.Treeview(
            self, columns=cols_clases, show="headings", selectmode="browse")
        self.tree_clases.tag_configure('par', background=COLOR_FILA_PAR)
        self.tree_clases.tag_configure('impar', background=COLOR_FILA_IMPAR)

        col_defs = {
            "ID Clase": {"w": 100, "s": tk.NO, "a": "w"}, "Fecha": {"w": 90, "s": tk.NO, "a": "center"},
            "Día": {"w": 80, "s": tk.NO, "a": "center"}, "Hora Inicio": {"w": 80, "s": tk.NO, "a": "center"},
            "Hora Fin": {"w": 80, "s": tk.NO, "a": "center"}, "Materia": {"w": 180, "s": tk.YES, "a": "w"},
            "Profesor": {"w": 150, "s": tk.YES, "a": "w"}, "Salón": {"w": 100, "s": tk.NO, "a": "center"}
        }
        for col in cols_clases:
            self.tree_clases.heading(col, text=col, anchor=col_defs[col]["a"])
            self.tree_clases.column(
                col, width=col_defs[col]["w"], anchor=col_defs[col]["a"], stretch=col_defs[col]["s"])

        self.tree_clases.pack(expand=True, fill="both",
                              padx=0, pady=(0, 10), side="left")
        scrollbar_clases = ttk.Scrollbar(
            self, orient="vertical", command=self.tree_clases.yview)
        self.tree_clases.configure(yscrollcommand=scrollbar_clases.set)
        scrollbar_clases.pack(side="right", fill="y")
        self.tree_clases.bind("<<TreeviewSelect>>",
                              self._on_clase_seleccionada)

        self.actualizar_contenido()

    def _aplicar_filtro_fecha(self):
        self.actualizar_contenido()  # Llama a actualizar_contenido que ya usa el filtro

    def _mostrar_todas_las_clases(self):
        self.filtro_fecha_var.set("")  # Limpiar el filtro de fecha
        self.actualizar_contenido()  # Recargar todas las clases

    def _get_nombre_profesor(self, id_profesor):
        if not id_profesor:
            return "N/A"
        prof_frame = self.controller.frames.get('ProfesoresFrame')
        if prof_frame and hasattr(prof_frame, 'teacher_repo'):
            prof_data = prof_frame.teacher_repo.get_teacher_by_id(id_profesor)
            return f"{prof_data[1]} {prof_data[2]}" if prof_data else "Prof. Desconocido"
        return "Error Acceso Prof."

    def _get_nombre_materia(self, id_materia):
        if not id_materia:
            return "N/A"
        mat_frame = self.controller.frames.get('MateriasFrame')
        if mat_frame and hasattr(mat_frame, 'subject_repo'):
            mat_data = mat_frame.subject_repo.get_subject_by_id(id_materia)
            return str(mat_data[1]) if mat_data else "Materia Desconocida"
        return "Error Acceso Mat."

    # El ID del salón ya es "numero-bloque"
    def _get_display_salon(self, id_salon_compuesto):
        return str(id_salon_compuesto) if id_salon_compuesto else "N/A"

    def actualizar_contenido(self):
        """Actualiza el TreeView con las clases, aplicando el filtro de fecha si existe."""
        # El filtro de fecha se aplica en _cargar_clases_en_treeview
        self._cargar_clases_en_treeview()
        self._actualizar_estado_botones_clase()

    def _cargar_clases_en_treeview(self):
        """Carga las clases en el TreeView, aplicando el filtro de fecha."""
        for i in self.tree_clases.get_children():
            self.tree_clases.delete(i)

        # <--- USA EL REPOSITORIO
        todas_las_clases = self.scheduled_class_repo.get_all_scheduled_classes()

        filtro_fecha_str = self.filtro_fecha_var.get()
        datos_a_mostrar = todas_las_clases

        if filtro_fecha_str:
            try:
                # Validar que el filtro de fecha sea válido antes de usarlo
                datetime.strptime(filtro_fecha_str, "%Y-%m-%d")
                datos_a_mostrar = [
                    clase for clase in todas_las_clases if clase[1] == filtro_fecha_str]
            except ValueError:
                # Si el filtro no es una fecha válida, no se aplica o se muestra un error
                # Aquí optamos por no filtrar si el formato es incorrecto, mostrando todas.
                # Podrías añadir un messagebox si prefieres.
                print(f"Advertencia: Filtro de fecha '{
                      filtro_fecha_str}' no es válido. Mostrando todas las clases.")
                self.filtro_fecha_var.set("")  # Limpiar filtro inválido
                # datos_a_mostrar ya es todas_las_clases

        dias_es = ["Lunes", "Martes", "Miércoles",
                   "Jueves", "Viernes", "Sábado", "Domingo"]

        # Ordenar por fecha y luego por hora de inicio
        try:
            data_ordenada = sorted(
                datos_a_mostrar,
                key=lambda x: (datetime.strptime(
                    x[1], "%Y-%m-%d"), datetime.strptime(x[2], "%H:%M"))
            )
        # Manejar posibles errores si los datos no son como se esperan
        except (TypeError, ValueError) as e:
            print(f"Error al ordenar clases: {e}. Mostrando sin ordenar.")
            data_ordenada = datos_a_mostrar

        for idx, clase_row in enumerate(data_ordenada):
            # clase_row: [id, fecha, hora_inicio, hora_fin, id_materia, id_profesor, id_salon_compuesto]
            id_clase, fecha_str, hora_inicio_str, hora_fin_str, id_materia, id_profesor, id_salon_compuesto = clase_row

            nombre_materia = self._get_nombre_materia(id_materia)
            nombre_profesor = self._get_nombre_profesor(id_profesor)
            display_salon = self._get_display_salon(id_salon_compuesto)

            try:
                dia_semana = dias_es[datetime.strptime(
                    fecha_str, "%Y-%m-%d").weekday()]
            except ValueError:
                dia_semana = "N/A"

            visual_row = [id_clase, fecha_str, dia_semana, hora_inicio_str,
                          hora_fin_str, nombre_materia, nombre_profesor, display_salon]
            tag = 'par' if idx % 2 == 0 else 'impar'
            self.tree_clases.insert(
                "", "end", values=visual_row, iid=id_clase, tags=(tag,))

        if self.clase_seleccionada_id_tree and not self.tree_clases.exists(self.clase_seleccionada_id_tree):
            self.clase_seleccionada_id_tree = None
        # Asegurar que los botones se actualicen
        self._actualizar_estado_botones_clase()

    def _on_clase_seleccionada(self, event=None):
        seleccion = self.tree_clases.selection()
        self.clase_seleccionada_id_tree = seleccion[0] if seleccion else None
        self._actualizar_estado_botones_clase()

    def _actualizar_estado_botones_clase(self):
        estado = "normal" if self.clase_seleccionada_id_tree else "disabled"
        self.btn_editar_clase.config(state=estado)
        self.btn_cancelar_clase.config(state=estado)

    def _abrir_ventana_programar_clase(self):
        VentanaClase(self, self.controller, modo="programar")

    def _abrir_ventana_editar_clase(self):
        if not self.clase_seleccionada_id_tree:
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona una clase para editar.", parent=self.controller)
            return

        clase_a_editar_data = self.scheduled_class_repo.get_scheduled_class_by_id(
            self.clase_seleccionada_id_tree)  # <--- USA EL REPOSITORIO

        if clase_a_editar_data:
            VentanaClase(self, self.controller, modo="editar",
                         clase_data=clase_a_editar_data)
        else:
            messagebox.showerror(
                "Error", "No se encontró la clase seleccionada.", parent=self.controller)
            self.actualizar_contenido()

    def _cancelar_clase(self):
        if not self.clase_seleccionada_id_tree:
            messagebox.showwarning(
                "Selección Requerida", "Por favor, selecciona una clase para cancelar.", parent=self.controller)
            return

        if messagebox.askyesno("Confirmar Cancelación",
                               f"¿Está seguro de que desea cancelar la clase con ID {
                                   self.clase_seleccionada_id_tree}?",
                               parent=self.controller):
            # <--- USA EL REPOSITORIO
            if self.scheduled_class_repo.delete_scheduled_class(self.clase_seleccionada_id_tree):
                messagebox.showinfo(
                    "Cancelada", "Clase cancelada correctamente.", parent=self.controller)
                self.actualizar_contenido()
            else:
                messagebox.showerror(
                    "Error", "No se pudo cancelar la clase.", parent=self.controller)
                self.actualizar_contenido()  # Sincronizar

    def guardar_datos_clase(self, datos_clase, id_clase_original=None):
        """
        Guarda los datos de la clase (nueva o editada) usando el ScheduledClassRepository.
        Realiza validaciones de negocio antes de guardar.
        Retorna True si la operación fue exitosa, False si no.
        """
        # datos_clase: [id_clase, fecha_str, hora_inicio_str, hora_fin_str,
        #               id_materia, id_profesor, id_salon_compuesto]
        nueva_id_clase = datos_clase[0]
        nueva_fecha_str, nueva_hora_inicio_str, nueva_hora_fin_str = datos_clase[
            1], datos_clase[2], datos_clase[3]
        nuevo_id_materia, nuevo_id_profesor, nuevo_id_salon_compuesto = datos_clase[
            4], datos_clase[5], datos_clase[6]

        active_toplevel = self.controller.focus_get()
        if not isinstance(active_toplevel, tk.Toplevel):
            active_toplevel = self  # Fallback al frame si no hay Toplevel activo

        # 1. Validaciones de Formato y Lógica Básica (ya hechas en VentanaClase, pero se pueden re-verificar)
        try:
            nueva_fecha_obj = datetime.strptime(
                nueva_fecha_str, "%Y-%m-%d").date()
            nueva_inicio_obj = datetime.strptime(
                nueva_hora_inicio_str, "%H:%M").time()
            nueva_fin_obj = datetime.strptime(
                nueva_hora_fin_str, "%H:%M").time()
            if nueva_inicio_obj >= nueva_fin_obj:
                messagebox.showerror(
                    "Error de Horas", "La hora de inicio no puede ser igual o posterior a la hora de fin.", parent=active_toplevel)
                return False
        except ValueError:
            messagebox.showerror(
                "Error Interno", "Formato de fecha/hora incorrecto al procesar para guardar.", parent=active_toplevel)
            return False

        # 2. Validaciones de Negocio (Conflictos, etc.)
        # Acceder a los repositorios de otros frames
        prof_frame = self.controller.frames.get('ProfesoresFrame')
        mat_frame = self.controller.frames.get('MateriasFrame')
        sal_frame = self.controller.frames.get(
            'SalonesFrame')  # Asumiendo que es ClassroomsFrame

        if not (prof_frame and mat_frame and sal_frame and
                hasattr(prof_frame, 'teacher_repo') and
                hasattr(mat_frame, 'subject_repo') and
                hasattr(sal_frame, 'classroom_repo')):
            messagebox.showerror(
                "Error Interno", "No se pudieron cargar los datos necesarios para la validación.", parent=active_toplevel)
            return False

        # 2.1. Conflicto de Profesor
        if self.scheduled_class_repo.check_teacher_availability_conflict(
                nuevo_id_profesor, nueva_fecha_str, nueva_hora_inicio_str, nueva_hora_fin_str,
                excluding_class_id=id_clase_original):
            prof_nombre = self._get_nombre_profesor(nuevo_id_profesor)
            messagebox.showerror("Conflicto de Horario",
                                 f"El profesor {
                                     prof_nombre} ya tiene otra clase programada en ese horario.",
                                 parent=active_toplevel)
            return False

        # 2.2. Conflicto de Salón
        if self.scheduled_class_repo.check_classroom_availability_conflict(
                nuevo_id_salon_compuesto, nueva_fecha_str, nueva_hora_inicio_str, nueva_hora_fin_str,
                excluding_class_id=id_clase_original):
            messagebox.showerror("Conflicto de Horario",
                                 f"El salón {
                                     nuevo_id_salon_compuesto} ya está ocupado en ese horario.",
                                 parent=active_toplevel)
            return False

        # 2.3. Compatibilidad Materia-Salón (requiere sala de sistemas)
        materia_sel_data_list = mat_frame.subject_repo.get_subject_by_id(
            nuevo_id_materia)
        # classroom_repo.get_classroom espera (numero, bloque)
        num_salon_busqueda, bloque_salon_busqueda = None, None
        if nuevo_id_salon_compuesto and '-' in nuevo_id_salon_compuesto:
            try:
                num_salon_busqueda, bloque_salon_busqueda = nuevo_id_salon_compuesto.split(
                    '-', 1)
            except ValueError:
                messagebox.showerror("Error de Datos", f"ID de salón '{
                                     nuevo_id_salon_compuesto}' con formato incorrecto.", parent=active_toplevel)
                return False
        else:  # Si el ID no es compuesto, podría ser un error o una lógica diferente
            messagebox.showerror("Error de Datos", f"ID de salón '{
                                 nuevo_id_salon_compuesto}' no tiene el formato esperado 'Numero-Bloque'.", parent=active_toplevel)
            return False

        salon_sel_data_list = sal_frame.classroom_repo.get_classroom(
            num_salon_busqueda, bloque_salon_busqueda)

        if not materia_sel_data_list:
            messagebox.showerror(
                "Error de Datos", "Materia seleccionada no encontrada.", parent=active_toplevel)
            return False
        if not salon_sel_data_list:
            messagebox.showerror("Error de Datos", f"Salón '{
                                 nuevo_id_salon_compuesto}' no encontrado.", parent=active_toplevel)
            return False

        materia_requiere_lab = materia_sel_data_list[3]  # requires_lab
        salon_es_lab = salon_sel_data_list[3]  # is_lab (o es_sistemas)

        if materia_requiere_lab and not salon_es_lab:
            messagebox.showerror("Conflicto de Salón",
                                 f"La materia '{materia_sel_data_list[1]}' requiere sala de sistemas, pero el salón '{
                                     nuevo_id_salon_compuesto}' no lo es.",
                                 parent=active_toplevel)
            return False

        # 3. Guardar en el repositorio
        operacion_exitosa_repo = False
        if id_clase_original:  # Modo edición
            if self.scheduled_class_repo.update_scheduled_class(id_clase_original, datos_clase):
                operacion_exitosa_repo = True
        else:  # Modo programar (nuevo)
            if self.scheduled_class_repo.add_scheduled_class(datos_clase):
                operacion_exitosa_repo = True

        if operacion_exitosa_repo:
            messagebox.showinfo(
                "Éxito", "Clase guardada correctamente.", parent=active_toplevel)
            self.actualizar_contenido()
            if self.tree_clases.exists(nueva_id_clase):
                self.tree_clases.selection_set(nueva_id_clase)
                self.tree_clases.focus(nueva_id_clase)
                self.tree_clases.see(nueva_id_clase)
                self.clase_seleccionada_id_tree = nueva_id_clase
            else:
                self.clase_seleccionada_id_tree = None
            self._actualizar_estado_botones_clase()
            return True
        else:
            messagebox.showerror(
                "Error de Guardado", "No se pudo guardar la clase en el repositorio.", parent=active_toplevel)
            return False
