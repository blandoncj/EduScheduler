import uuid


class ClassroomModel:
    def __init__(
            self, number: int, systems_room: bool = False, id: str = None
    ):
        self.number = number
        self.systems_room = systems_room
        self.id = str(uuid.uuid4()) if id is None else id

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'systems_room': self.systems_room
        }

    @staticmethod
    def from_dict(data):
        return ClassroomModel(
            id=data.get('id'),
            number=data['number'],
            systems_room=data['systems_room']
        )
