import uuid
from datetime import time

from models.subject_model import SubjectModel
from models.teacher_model import TeacherModel
from models.classroom_model import ClassroomModel


class ClassModel:
    def __init__(
        self,
        day_of_week: int,
        start_time: time,
        end_time: time,
        subject: SubjectModel,
        teacher: TeacherModel,
        classroom: ClassroomModel,
        id: str = None
    ):
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.subject = subject
        self.teacher = teacher
        self.classroom = classroom
        self.id = str(uuid.uuid4()) if id is None else id

    def to_dict(self):
        return {
            'id': self.id,
            'teacher': self.teacher.to_dict(),
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'subject': self.subject.to_dict(),
            'classroom': self.classroom.to_dict()
        }

    @staticmethod
    def from_dict(data):
        return ClassModel(
            id=data.get('id'),
            teacher=TeacherModel.from_dict(data['teacher']),
            day_of_week=data['day_of_week'],
            start_time=time.fromisoformat(data['start_time']),
            end_time=time.fromisoformat(data['end_time']),
            subject=SubjectModel.from_dict(data['subject']),
            classroom=ClassroomModel.from_dict(data['classroom'])
        )
