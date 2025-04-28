import uuid


class ClassroomModel:
    def __init__(self, systems_room: bool = False, id: str = None):
        self.systems_room = systems_room
        self.id = str(uuid.uuid4()) if id is None else id

    def to_dict(self):
        return {
            'id': self.id,
            'systems_room': self.systems_room
        }

    @staticmethod
    def from_dict(data):
        return ClassroomModel(
            id=data.get('id'),
            systems_room=data['systems_room']
        )
