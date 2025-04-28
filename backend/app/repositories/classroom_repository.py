import os
import json

from typing import List

from models.classroom_model import ClassroomModel


class ClassroomRepository:
    def __init__(self):
        self.file_path = os.path.join('./storage/classrooms.json')

    def get_all(self) -> List[ClassroomModel]:
        if not os.path.exists(self.file_path):
            return []

        if os.path.getsize(self.file_path) == 0:
            return []

        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, dict):
                return [ClassroomModel.from_dict(data)]
            return [ClassroomModel.from_dict(cla) for cla in data]

    def get_by_id(self, id: str) -> ClassroomModel:
        classes = self.get_all()
        for cla in classes:
            if cla.id == id:
                return cla
        return None

    def save(self, classroom: ClassroomModel) -> None:
        classrooms = self.get_all()
        classrooms.append(classroom)
        with open(self.file_path, 'w') as file:
            json.dump(
                [cla.to_dict() for cla in classrooms],
                file, ensure_ascii=False, indent=2
            )
