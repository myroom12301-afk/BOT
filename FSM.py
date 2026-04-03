from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    meet_time = State()
    date = State()
    who = State()
    name = State()
    number = State()
    conf = State()
    event_title = State()
    event_date = State()
    event_description = State()
    event_link = State()
    event_button_text = State()
