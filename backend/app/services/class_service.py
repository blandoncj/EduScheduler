from repositories.class_repository import ClassRepository


class ClassService:
    def __init__(self):
        self.repository = ClassRepository()

    def get_all_classes(self):
        return self.repository.get_all()

    def get_class_by_id(self, id: str):
        return self.repository.get_by_id(id)

    def get_classes_by_teacher_id(self, teacher_id: str):
        return self.repository.get_by_teacher_id(teacher_id)

    def save_class(self, class_model):
        self.repository.save(class_model)
