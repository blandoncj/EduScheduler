import os
import json

from typing import List

from models.class_model import ClassModel


class ClassRepository:
    def __init__(self):
        self.file_path = os.path.join('./storage/classes.json')

    def get_all(self) -> List[ClassModel]:
        if not os.path.exists(self.file_path):
            return []

        if os.path.getsize(self.file_path) == 0:
            return []

        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, dict):
                return [ClassModel.from_dict(data)]
            return [ClassModel.from_dict(cla) for cla in data]

    def get_by_id(self, id: str) -> ClassModel:
        classes = self.get_all()
        for cla in classes:
            if cla.id == id:
                return cla
        return None

    def get_by_teacher_id(self, teacher_id: str) -> List[ClassModel]:
        classes = self.get_all()
        return [
            cla for cla in classes
            if cla.teacher.id == teacher_id
        ]

    def save(self, cla: ClassModel) -> None:
        classes = self.get_all()
        classes.append(cla)
        with open(self.file_path, 'w') as file:
            json.dump(
                [cla.to_dict() for cla in classes],
                file, ensure_ascii=False, indent=2
            )
