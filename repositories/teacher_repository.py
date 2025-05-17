import json
import os


class TeacherRepository:
    """
    Manages teacher data persistence in a JSON file.
    Handles loading, saving, adding, updating, and deleting teachers,
    including their availability.
    """

    def __init__(self, filepath='./storage/teachers.json'):
        """
        Initializes the repository.

        Args:
            filepath (str): The path to the JSON file where teacher data is stored.
        """
        self.filepath = filepath
        # Ensure the storage directory exists
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.teachers_data = self._load_data()

    def _load_data(self):
        """
        Loads teacher data from the JSON file.
        If the file doesn't exist or is empty, it initializes with default data (o una lista vacía).

        Returns:
            list: A list of teacher dictionaries.
        """
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading teacher data from {self.filepath}: {e}")
            return []

    def _save_data(self, data=None):
        """
        Saves the teacher data to the JSON file.

        Args:
            data (list, optional): The data to save. If None, saves self.teachers_data.
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data if data is not None else self.teachers_data,
                          f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving teacher data to {self.filepath}: {e}")

    def get_all_teachers(self):
        """
        Retrieves all teachers.

        Returns:
            list: A list of lists, where each inner list represents a teacher's
                  attributes [id_card, first_name, last_name, availability_dict].
        """
        # El orden de los valores dependerá del orden de las claves en los diccionarios
        # Asegúrate de que este orden sea consistente o accede por clave si es necesario
        # al consumir estos datos. Para el Treeview, solo se usan los 3 primeros.
        return [
            [
                t.get("id_card"),
                t.get("first_name"),
                t.get("last_name"),
                # Devuelve un dict vacío si no hay disponibilidad
                t.get("availability", {})
            ] for t in self.teachers_data
        ]

    def get_teacher_by_id(self, id_card):
        """
        Finds a teacher by their ID card number.

        Args:
            id_card (str): The ID card number of the teacher.

        Returns:
            list: A list of the teacher's attributes [id_card, first_name, last_name, availability_dict]
                  if found, otherwise None.
        """
        id_card_str = str(id_card)
        for teacher in self.teachers_data:
            if str(teacher.get("id_card")) == id_card_str:
                return [
                    teacher.get("id_card"),
                    teacher.get("first_name"),
                    teacher.get("last_name"),
                    teacher.get("availability", {})
                ]
        return None

    def teacher_id_exists(self, id_card):
        """
        Checks if a teacher with the given ID card number already exists.

        Args:
            id_card (str): The ID card number to check.

        Returns:
            bool: True if the ID card number exists, False otherwise.
        """
        id_card_str = str(id_card)
        return any(str(t.get("id_card")) == id_card_str for t in self.teachers_data)

    def add_teacher(self, teacher_details):
        """
        Adds a new teacher.

        Args:
            teacher_details (list): Teacher details in the format:
                                    [id_card, first_name, last_name, availability_dict].

        Returns:
            bool: True if added successfully, False if a teacher with the same ID card already exists.
        """
        id_card = str(teacher_details[0])
        if self.teacher_id_exists(id_card):
            return False  # Teacher with this ID card already exists

        new_teacher = {
            "id_card": id_card,
            "first_name": str(teacher_details[1]),
            "last_name": str(teacher_details[2]),
            "availability": teacher_details[3] if len(teacher_details) > 3 and isinstance(teacher_details[3], dict) else {}
        }
        self.teachers_data.append(new_teacher)
        self._save_data()
        return True

    def update_teacher(self, original_id_card, updated_details):
        """
        Updates an existing teacher. The ID card (cedula) cannot be changed.

        Args:
            original_id_card (str): The original ID card of the teacher to update.
            updated_details (list): Updated details [new_id_card, first_name, last_name, availability_dict].
                                    Note: new_id_card should be the same as original_id_card.

        Returns:
            bool: True if updated successfully. False if not found or if an attempt is made
                  to change the ID card to one that already exists for another teacher.
        """
        original_id_card_str = str(original_id_card)
        new_id_card_str = str(updated_details[0])

        # La cédula no debería cambiar. Si lo hace y ya existe para otro profesor, es un error.
        if new_id_card_str != original_id_card_str:
            # Esto implica que la UI no debería permitir cambiar la cédula en modo edición.
            # Si se intenta y la nueva cédula ya existe para otro, es un error.
            if self.teacher_id_exists(new_id_card_str):
                print(
                    f"Error: Attempt to change ID card to an existing one ({new_id_card_str}).")
                return False

        for i, teacher in enumerate(self.teachers_data):
            if str(teacher.get("id_card")) == original_id_card_str:
                self.teachers_data[i] = {
                    "id_card": new_id_card_str,  # Usualmente no se cambia la cédula
                    "first_name": str(updated_details[1]),
                    "last_name": str(updated_details[2]),
                    "availability": updated_details[3] if len(updated_details) > 3 and isinstance(updated_details[3], dict) else {}
                }
                self._save_data()
                return True
        return False  # Teacher with original_id_card not found

    def delete_teacher(self, id_card):
        """
        Deletes a teacher by their ID card number.

        Args:
            id_card (str): The ID card number of the teacher to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        id_card_str = str(id_card)
        original_len = len(self.teachers_data)
        self.teachers_data = [t for t in self.teachers_data if str(
            t.get("id_card")) != id_card_str]

        if len(self.teachers_data) < original_len:
            self._save_data()
            return True
        return False
