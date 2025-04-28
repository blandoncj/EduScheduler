import uuid

from typing import List, Set

from models.restriction_model import RestrictionModel
from models.subject_model import SubjectModel
from models.time_slot_model import TimeSlotModel


class TeacherModel:
    def __init__(
        self,
        dni: str,
        name: str,
        subjects: List[SubjectModel] = [],
        restrictions: List[RestrictionModel] = [],
        time_slots: Set[TimeSlotModel] = set(),
        id: str = None
    ):
        self.dni = dni
        self.name = name
        self.subjects = subjects
        self.restrictions = restrictions
        self.time_slots = time_slots
        self.id = str(uuid.uuid4()) if id is None else id

    def to_dict(self):
        return {
            'id': self.id,
            'dni': self.dni,
            'name': self.name,
            'subjects': [
                subject.to_dict() for subject in self.subjects
            ],
            'restrictions': [
                restriction.to_dict() for restriction in self.restrictions
            ],
            'time_slots': [
                time_slot.value for time_slot in self.time_slots
            ]
        }

    @staticmethod
    def from_dict(data):
        return TeacherModel(
            dni=data['dni'],
            name=data['name'],
            subjects=[
                SubjectModel.from_dict(subject)
                for subject in data['subjects']
            ],
            restrictions=[
                RestrictionModel.from_dict(restriction)
                for restriction in data['restrictions']
            ],
            time_slots={
                TimeSlotModel(time_slot)
                for time_slot in data['time_slots']
            },
            id=data['id']
        )
