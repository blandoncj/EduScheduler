import os
import json

from typing import List

from models.subject_model import SubjectModel


class SubjectRepository:
    def __init__(self):
        self.file_path = os.path.join('./storage/subjects.json')

    def get_all(self) -> List[SubjectModel]:
        if not os.path.exists(self.file_path):
            return []

        if os.path.getsize(self.file_path) == 0:
            return []

        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, dict):
                return [SubjectModel.from_dict(data)]
            return [SubjectModel.from_dict(subject) for subject in data]

    def get_by_id(self, id: str) -> SubjectModel:
        subjects = self.get_all()
        for subject in subjects:
            if subject.id == id:
                return subject
        return None

    def get_all_by_name(self, name: str) -> List[SubjectModel]:
        subjects = self.get_all()
        return [
            subj for subj in subjects
            if subj.name.lower().startswith(name.lower())
        ]

    def save(self, subject: SubjectModel) -> None:
        subjects = self.get_all()
        subjects.append(subject)
        with open(self.file_path, 'w') as file:
            json.dump(
                [subject.to_dict() for subject in subjects],
                file, ensure_ascii=False, indent=2
            )
