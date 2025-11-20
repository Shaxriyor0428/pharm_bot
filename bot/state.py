from aiogram.fsm.state import StatesGroup, State

class GeoVideoState(StatesGroup):
    waiting_for_location = State()
    waiting_for_video = State()
