from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_gender = State()
    collecting_voices = State()

class AdminStates(StatesGroup):
    waiting_for_count = State() # For manual input of surah count
