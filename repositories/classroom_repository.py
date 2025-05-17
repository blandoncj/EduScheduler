import json
import os


class ClassroomRepository:
    """
    Manages classroom data persistence in a JSON file.
    Handles loading, saving, adding, updating, and deleting classrooms.
    Classroom uniqueness is determined by the combination of its number and block.
    """

    def __init__(self, filepath='./storage/classrooms.json'):
        """
        Initializes the repository.

        Args:
            filepath (str): The path to the JSON file where classroom data is stored.
        """
        self.filepath = filepath
        # Ensure the storage directory exists
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.classrooms_data = self._load_data()

    def _load_data(self):
        """
        Loads classroom data from the JSON file.
        If the file doesn't exist or is empty, it returns an empty list.
        (Consider re-adding default data here if needed for a first run)

        Returns:
            list: A list of classroom dictionaries.
        """
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data from {self.filepath}: {e}")
            return []

    def _save_data(self, data=None):
        """
        Saves the classroom data to the JSON file.

        Args:
            data (list, optional): The data to save. If None, saves self.classrooms_data.
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data if data is not None else self.classrooms_data,
                          f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data to {self.filepath}: {e}")

    def get_all_classrooms(self):
        """
        Retrieves all classrooms.

        Returns:
            list: A list of lists, where each inner list represents a classroom's
                  attributes [number, block, capacity, is_lab].
                  The order of attributes is based on dict.values() behavior.
        """
        return [list(c.values()) for c in self.classrooms_data]

    def get_classroom(self, classroom_number, classroom_block):
        """
        Finds a classroom by its number and block.

        Args:
            classroom_number (str): The number of the classroom.
            classroom_block (str): The block of the classroom.

        Returns:
            list: A list of the classroom's attributes if found, otherwise None.
        """
        for classroom in self.classrooms_data:
            if str(classroom.get("number")) == str(classroom_number) and \
               str(classroom.get("block")) == str(classroom_block):
                return list(classroom.values())
        return None

    def classroom_exists(self, classroom_number, classroom_block):
        """
        Checks if a classroom with the given number and block already exists.

        Args:
            classroom_number (str): The classroom number to check.
            classroom_block (str): The classroom block to check.

        Returns:
            bool: True if the classroom (number and block combination) exists, False otherwise.
        """
        return any(
            str(c.get("number")) == str(classroom_number) and
            str(c.get("block")) == str(classroom_block)
            for c in self.classrooms_data
        )

    def add_classroom(self, classroom_details):
        """
        Adds a new classroom. classroom_details = [number, block, capacity, is_lab]

        Args:
            classroom_details (list): Classroom details [number, block, capacity, is_lab].

        Returns:
            bool: True if added successfully, False if it already exists.
        """
        number = str(classroom_details[0])
        # Ensure block is also treated as string for comparison
        block = str(classroom_details[1])

        if self.classroom_exists(number, block):
            return False  # Classroom with this number and block already exists

        new_classroom = {
            "number": number,
            "block": block,
            "capacity": int(classroom_details[2]),
            "is_lab": bool(classroom_details[3])
        }
        self.classrooms_data.append(new_classroom)
        self._save_data()
        return True

    def update_classroom(self, original_number, original_block, updated_details):
        """
        Updates an existing classroom.
        updated_details = [new_number, new_block, new_capacity, new_is_lab]

        Args:
            original_number (str): The original number of the classroom.
            original_block (str): The original block of the classroom.
            updated_details (list): Updated details [new_number, new_block, capacity, is_lab].

        Returns:
            bool: True if updated successfully. False if not found or new details conflict.
        """
        new_number = str(updated_details[0])
        new_block = str(updated_details[1])  # Ensure new_block is string

        # Check if the new combination (number, block) conflicts with another existing classroom
        # It's a conflict if classroom_exists(new_number, new_block) is True AND
        # (new_number, new_block) is different from (original_number, original_block)
        if (new_number != str(original_number) or new_block != str(original_block)) and \
           self.classroom_exists(new_number, new_block):
            return False  # New number/block combination conflicts with another existing classroom

        for i, classroom in enumerate(self.classrooms_data):
            if str(classroom.get("number")) == str(original_number) and \
               str(classroom.get("block")) == str(original_block):
                self.classrooms_data[i] = {
                    "number": new_number,
                    "block": new_block,
                    "capacity": int(updated_details[2]),
                    "is_lab": bool(updated_details[3])
                }
                self._save_data()
                return True
        return False  # Classroom with original_number and original_block not found

    def delete_classroom(self, classroom_number, classroom_block):
        """
        Deletes a classroom by its number and block.

        Args:
            classroom_number (str): The number of the classroom.
            classroom_block (str): The block of the classroom.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        classroom_number_str = str(classroom_number)
        # Ensure block is string for comparison
        classroom_block_str = str(classroom_block)
        original_len = len(self.classrooms_data)

        self.classrooms_data = [
            c for c in self.classrooms_data
            if not (str(c.get("number")) == classroom_number_str and
                    str(c.get("block")) == classroom_block_str)
        ]

        if len(self.classrooms_data) < original_len:
            self._save_data()
            return True
        return False
