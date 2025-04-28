from repositories.teacher_repository import TeacherRepository


class TeacherService:
    def __init__(self):
        self.repository = TeacherRepository()

    def get_all_teachers(self):
        return self.repository.get_all()

    def get_teacher_by_id(self, id: str):
        return self.repository.get_by_id(id)

    def get_teacher_by_dni(self, dni: str):
        return self.repository.get_by_dni(dni)

    def get_teachers_by_name(self, name: str):
        return self.repository.get_by_name(name)

    def save_teacher(self, teacher):
        existing_teachers = self.get_all_teachers()

        if any(
            existing.dni == teacher.dni for existing in existing_teachers
        ):
            raise ValueError(f"Teacher with dni '{
                             teacher.name}' already exists.")

        self.repository.save(teacher)
