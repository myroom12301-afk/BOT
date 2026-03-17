from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    meet_time = State()
    date = State()
    who = State()
    name = State()
    number = State()
    conf = State()