from repositories.subject_repository import SubjectRepository


class SubjectService:
    def __init__(self):
        self.repository = SubjectRepository()

    def get_all_subjects(self):
        return self.repository.get_all()

    def get_subject_by_id(self, id: str):
        return self.repository.get_by_id(id)

    def get_subjects_by_name(self, name: str):
        return self.repository.get_all_by_name(name)

    def save_subject(self, subject):
        existing_subjects = self.get_all_subjects()

        if any(
                existing.name == subject.name for existing in existing_subjects
        ):
            raise ValueError(f"Subject with name '{
                             subject.name}' already exists.")

        self.repository.save(subject)
