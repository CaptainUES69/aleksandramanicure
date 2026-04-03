from aiogram.filters.state import State, StatesGroup


class ViewText(StatesGroup):
    view = State()

class ChangeText(StatesGroup):
    get_text = State()
    again = State()

class ForwardMessage(StatesGroup):
    choose_course = State()
    collect_data = State()
    set_name = State()