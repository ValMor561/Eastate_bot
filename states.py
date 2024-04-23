from aiogram.filters.state import State, StatesGroup

class AllField(StatesGroup):
    city = State()
    district = State()
    flat_type = State()
    payment_type = State()
    cost_limit = State()
    fioandphone = State()
    time = State()

class Saratov(StatesGroup):
    type = State()
    fioandphone = State()
    time = State()

class Consult(StatesGroup):
    fioandphone = State()
    comment = State()
    time = State()

class Policy(StatesGroup):
    type = State()
    offer = State()
    fioandphone = State()
    position = State()
    employer = State()
    weight = State()
    height = State()
    diseases = State()
    bank = State()
    count = State()
    year = State()
    gas = State()
    time = State()