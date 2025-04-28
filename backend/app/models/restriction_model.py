import uuid

from models.time_slot_model import TimeSlotModel


class RestrictionModel:
    def __init__(
        self, day_of_week: int, time_slot: TimeSlotModel, id: int = None
    ):
        self.day_of_week = day_of_week
        self.time_slot = time_slot
        self.id = str(uuid.uuid4()) if id is None else id

    def to_dict(self):
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'time_slot': self.time_slot
        }

    @staticmethod
    def from_dict(data):
        return RestrictionModel(
            id=data.get('id'),
            day_of_week=data['day_of_week'],
            time_slot=[data['time_slot']]
        )
