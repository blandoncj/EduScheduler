import uuid


class SubjectModel:
    def __init__(
        self,
        name: str,
        hours: int,
        systems_room: bool = False,
        id: str = None
    ):
        self.name = name
        self.hours = hours
        self.systems_room = systems_room
        self.id = str(uuid.uuid4()) if id is None else id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hours': self.hours,
            'systems_room': self.systems_room
        }

    @staticmethod
    def from_dict(data):
        return SubjectModel(
            id=data.get('id'),
            name=data['name'],
            hours=data['hours'],
            systems_room=data['systems_room']
        )
