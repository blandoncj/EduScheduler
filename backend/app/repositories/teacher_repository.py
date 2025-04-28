import os
import json

from typing import List

from models.teacher_model import TeacherModel


class TeacherRepository:
    def __init__(self):
        self.file_path = os.path.join('./storage/teachers.json')

    def get_all(self) -> List[TeacherModel]:
        if not os.path.exists(self.file_path):
            return []

        if os.path.getsize(self.file_path) == 0:
            return []

        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, dict):
                return [TeacherModel.from_dict(data)]
            return [TeacherModel.from_dict(teacher) for teacher in data]

    def get_by_id(self, id: str) -> TeacherModel:
        teachers = self.get_all()
        for teacher in teachers:
            if teacher.id == id:
                return teacher
        return None

    def get_by_dni(self, dni: str) -> TeacherModel:
        teachers = self.get_all()
        for teacher in teachers:
            if teacher.dni == dni:
                return teacher
        return None

    def get_by_name(self, name: str) -> List[TeacherModel]:
        teachers = self.get_all()
        return [
            teacher for teacher in teachers
            if teacher.name.lower().startswith(name.lower())
        ]

    def save(self, teacher: TeacherModel) -> None:
        teachers = self.get_all()
        teachers.append(teacher)
        with open(self.file_path, 'w') as file:
            json.dump(
                [teacher.to_dict() for teacher in teachers],
                file, ensure_ascii=False, indent=2
            )
