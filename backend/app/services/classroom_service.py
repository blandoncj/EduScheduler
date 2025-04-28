from repositories.classroom_repository import ClassroomRepository


class ClassroomService:
    def __init__(self):
        self.repository = ClassroomRepository()

    def get_all_classrooms(self):
        return self.repository.get_all()

    def get_classroom_by_id(self, id: str):
        return self.repository.get_by_id(id)

    def save_classroom(self, classroom):
        self.repository.save(classroom)
