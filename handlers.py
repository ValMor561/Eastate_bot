from aiogram import types, Router, Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder 
import config
import states
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest, TelegramForbiddenError
from datetime import datetime, timedelta
from bd import BDRequests
from aiogram.filters.callback_data import CallbackData
from aiogram.types.input_file import FSInputFile
import os
import sys
from aiogram.fsm.strategy import FSMStrategy

bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)
router = Router()
BD = BDRequests()

#Запуск бота и вход в режим бесконечного цикла
@router.message(Command("start"))
async def cmd_start(msg: Message):
    if str(msg.chat.id) not in config.ADMINS:
        await msg.answer("Рада приветствовать Вас в своем телеграмм-канале.\nЗдесь я рассказываю о лучших предложениях по ипотеке, о ЖК в Москве, Санкт-Петербурге, Краснодаре и Саратове, о налогах, страховании и о том, что так или иначе связано с Недвижимостью.\nОставайтесь с нами, чтобы всегда быть в курсе о рынке Недвижимости!")
        await check_subscribe(msg)
    else:
        builder = ReplyKeyboardBuilder()
        builder.row(types.KeyboardButton(text='/big_city', callback_data='big_city'), types.KeyboardButton(text='/saratov', callback_data='saratov'))
        builder.row(types.KeyboardButton(text='/consult', callback_data='consult'), types.KeyboardButton(text='/policy', callback_data='policy'))
        builder.row(types.KeyboardButton(text='/restart', callback_data='restart'))

        keyboard = builder.as_markup(resize_keyboard=True)
        await msg.answer("Добро пожаловать в панель администратора:\nКоманды:\n/big_city - Отображение заявок в Москве/Краснодаре/Санкт-Петербурге\n/saratov - Отображение заявок в Саратове\n/consult - Отображение заявок на консультацию\n/policy - Отображение заявок на оформление страхового полиса\n/restart - Перезапуск всего бота\n", reply_markup=keyboard)

@router.message(Command("big_city"))
async def get_big_city(msg: Message):
    posts = BD.select_all("AllField")
    if len(posts) == 0 and msg.text == '/big_city':
        await msg.answer("Нет заявок")
    for post in posts:
        builder = InlineKeyboardBuilder()
        button = types.InlineKeyboardButton(text="Удалить" , callback_data=f"ID:AllField:{post[0]}")
        builder.add(button)
        keyboard = builder.as_markup(resize_keyboard=True)
        await msg.answer(f"Заявка:\nГород: {post[1]}\nРайон: {post[2]}\nПараметры квартиры: {post[3]}\nФорма оплаты: {post[4]}\nСумма покупки: {post[5]}\nФИО и телефон: {post[6]}\nУдобное для звонка время: {post[7]}", reply_markup=keyboard)

@router.message(Command("saratov"))
async def get_saratov(msg: Message):
    posts = BD.select_all("Saratov")
    if len(posts) == 0 and msg.text == '/saratov':
        await msg.answer("Нет заявок")
    for post in posts:
        builder = InlineKeyboardBuilder()
        button = types.InlineKeyboardButton(text="Удалить" , callback_data=f"ID:Saratov:{post[0]}")
        builder.add(button)
        keyboard = builder.as_markup(resize_keyboard=True)
        await msg.answer(f"Заявка:\nГород: Саратов\nТип сделки: {post[1]}\nФИО и телефон: {post[2]}\nУдобное для звонка время: {post[3]}", reply_markup=keyboard)

@router.message(Command("consult"))
async def get_consult(msg: Message):
    posts = BD.select_all("Consult")
    if len(posts) == 0 and msg.text == '/consult':
        await msg.answer("Нет заявок")
    for post in posts:
        builder = InlineKeyboardBuilder()
        button = types.InlineKeyboardButton(text="Удалить" , callback_data=f"ID:Consult:{post[0]}")
        builder.add(button)
        keyboard = builder.as_markup(resize_keyboard=True)
        await msg.answer(f"Заявка:\nКонсультация\nФИО и телефон: {post[1]}\nТема вопроса: {post[2]}\nУдобное для звонка время: {post[3]}", reply_markup=keyboard)

@router.message(Command("policy"))
async def get_policy(msg: Message):
    posts = BD.select_all("Policy")
    if len(posts) == 0 and msg.text == '/policy':
        await msg.answer("Нет заявок")
    for post in posts:
        builder = InlineKeyboardBuilder()
        button = types.InlineKeyboardButton(text="Удалить" , callback_data=f"ID:Policy:{post[0]}")
        builder.add(button)
        keyboard = builder.as_markup(resize_keyboard=True)
        if post[2] == "Продлить полис в рамках ипотеки":
            await msg.answer(f"Заявка:\nСтраховой полис\nСтраховой продукт: {post[1]}\nЦель страховки: {post[2]}\nФИО и телефон: {post[3]}\nДолжность: {post[4]}\nРаботодатель: {post[5]}\nВес: {post[6]}\n Рост: {post[7]}\nХронические заболевания: {post[8]}\nБанк: {post[9]}\nРазмер кредитных средств: {post[10]}\nГод постройки {post[11]}\nГазифицирован: {post[12]}\nУдобное для звонка время: {post[13]}", reply_markup=keyboard)
        else:
            await msg.answer(f"Заявка:\nСтраховой полис\nСтраховой продукт: {post[1]}\nЦель страховки: {post[2]}\nФИО и телефон: {post[3]}\nУдобное для звонка время: {post[13]}", reply_markup=keyboard)

@router.callback_query(lambda c: "ID" in c.data)
async def delet_task(callback_query: types.CallbackQuery):
    data = callback_query.data.split(":")
    tablename = data[1]
    id = data[2]
    BD.delete_by_id(tablename,id)
    await callback_query.message.answer(f"Заявка удалена")

@router.message(Command("restart"))
async def restart(msg: Message):
    if str(msg.from_user.id) in config.ADMINS:
        await msg.answer("Перезапуск бота...\n")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    else:
        await msg.answer("Недостаточно прав\n")

@router.callback_query(lambda c: c.data == 'main_menu')
async def main_menu(msg):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Подбор недвижимости в Москве/Краснодаре/Санкт-Петербурге', callback_data='bigcity'))
    builder.add(types.InlineKeyboardButton(text='Продать или купить квартиру в Саратове', callback_data='Саратов'))
    builder.add(types.InlineKeyboardButton(text='Оформление страхового полиса', callback_data='policy'), types.InlineKeyboardButton(text='Скачать чек-лист', callback_data='checklist'))
    builder.add(types.InlineKeyboardButton(text='Оставить заявку на бесплатную консультацию', callback_data='Консультация'))       
    builder.adjust(1) 
    keyboard = builder.as_markup(resize_keyboard=True)
    if type(msg) is Message:
        await msg.answer("Выберите, что вас интересует", reply_markup=keyboard)
    elif type(msg) is types.CallbackQuery:
        await msg.message.answer("Выберите, что вас интересует", reply_markup=keyboard)

async def end_phrase(msg):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Выбрать услугу', callback_data='main_menu'))
    keyboard = builder.as_markup(resize_keyboard=True)
    if type(msg) is Message:
        await msg.answer("Мы получили Вашу заявку и скоро свяжемся с Вами")
        await msg.answer("Оставайтесь с нами, чтобы всегда быть в курсе о рынке Недвижимости!", reply_markup=keyboard)
    elif type(msg) is types.CallbackQuery:
        await msg.message.answer("Мы получили Вашу заявку и скоро свяжемся с Вами")
        await msg.message.answer("Оставайтесь с нами, чтобы всегда быть в курсе о рынке Недвижимости!", reply_markup=keyboard)


@router.callback_query(lambda c: c.data == 'check_sub')
async def check_subscribe(msg):
    sub = await bot.get_chat_member(chat_id=config.CHANELL_ID, user_id=msg.from_user.id)
    if sub.status != "left":
        await main_menu(msg)
    else:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text='Канал', url=config.CHANELL_URL), types.InlineKeyboardButton(text='Проверить подписку', callback_data='check_sub'))
        keyboard = builder.as_markup(resize_keyboard=True)
        await msg.answer("Для продолжения работы, подпишитесь на канал", reply_markup=keyboard)

#Обработка цепочки москва/краснодар/питер
@router.callback_query(lambda c: c.data == 'bigcity')
async def cmd_bigcity(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.AllField.city)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='В Москве', callback_data='Москва'), types.InlineKeyboardButton(text='В Краснодаре', callback_data='Краснодар'))
    builder.add(types.InlineKeyboardButton(text='В Санкт-Петербурге', callback_data='Санкт-Петербург'))
    builder.adjust(1) 
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer("Укажите, в каком городе Вы хотите приобрести Недвижимость", reply_markup=keyboard)

@router.callback_query(states.AllField.city)
async def cmd_city(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.AllField.district)
    await state.update_data(city=callback_query.data)
    await callback_query.message.answer("Укажите, в каком районе Вы хотите приобрести Недвижимость")

@router.message(states.AllField.district)
async def get_district(message: types.Message, state: FSMContext):
    await state.update_data(district=message.text)
    await state.set_state(states.AllField.flat_type)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Студия', callback_data='Студия'), types.InlineKeyboardButton(text='1-комнатная', callback_data='1-комнатная'))
    builder.add(types.InlineKeyboardButton(text='2-комнатная', callback_data='2-комнатная'), types.InlineKeyboardButton(text='3-комнатная', callback_data='3-комнатная'))
    builder.add(types.InlineKeyboardButton(text='4-комнатная и более', callback_data='4-комнатная и более'))       
    builder.adjust(1) 
    keyboard = builder.as_markup(resize_keyboard=True)
    await message.answer("Выберете параметры квартиры:", reply_markup=keyboard)

@router.callback_query(states.AllField.flat_type)
async def get_flat_type(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(flat_type=callback_query.data)
    await state.set_state(states.AllField.payment_type)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Наличные', callback_data='Наличные'), types.InlineKeyboardButton(text='Ипотека', callback_data='Ипотека'))
    builder.adjust(1) 
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer("Какая у Вас форма оплаты:", reply_markup=keyboard)

@router.callback_query(states.AllField.payment_type)
async def get_payment_type(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(payment_type=callback_query.data)
    await state.set_state(states.AllField.cost_limit)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='До 10 миллионов', callback_data='До 10 миллионов'), types.InlineKeyboardButton(text='До 14 миллионов', callback_data='До 14 миллионов'))
    builder.add(types.InlineKeyboardButton(text='До 18 миллионов', callback_data='До 18 миллионов'), types.InlineKeyboardButton(text='Другое', callback_data='Другое'))
    builder.adjust(1) 
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer("До какой суммы планируете покупку:", reply_markup=keyboard)

@router.callback_query(states.AllField.cost_limit, lambda c: c.data == 'Другое')
async def get_cost_limit_another(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите сумму:")

@router.callback_query(states.AllField.cost_limit)
@router.message(states.AllField.cost_limit)
async def get_cost_limit(data, state: FSMContext):
    await state.set_state(states.AllField.fioandphone)
    if type(data) is Message:
        await state.update_data(cost_limit=data.text)
        await data.answer("Укажите свое ФИО и контактный номер телефона:")
    elif type(data) is types.CallbackQuery:
        await state.update_data(cost_limit=data.data)
        await data.message.answer("Укажите свое ФИО и контактный номер телефона:")
    
@router.message(states.AllField.fioandphone)
async def get_fio(message: types.Message, state: FSMContext):
    await state.update_data(fioandphone=message.text)
    await state.set_state(states.AllField.time)
    await message.answer("Укажите удобное по Мск время для звонка:")

@router.message(states.AllField.time)
async def get_phone(message: types.Message, state: FSMContext):
    all = await state.get_data()
    BD.insert_big_city(all, message.text)
    for id in config.ADMINS:
        try:
            await bot.send_message(id, f"Новая заявка:\nГород: {all['city']}\nРайон: {all['district']}\nПараметры квартиры: {all['flat_type']}\nФорма оплаты: {all['payment_type']}\nСумма покупки: {all['cost_limit']}\nФИО и телефон: {all['fioandphone']}\nУдобное для звонка время: {message.text}")
        except TelegramBadRequest as e:
            print(e)
            continue
            
    await state.clear()
    await end_phrase(message)

#Обработка цепочки саратов
@router.callback_query(lambda c: c.data == 'Саратов')
async def cmd_moscow(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.Saratov.type)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Купить', callback_data='Купить'), types.InlineKeyboardButton(text='Продать', callback_data='Продать'))
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer("Вы хотите купить или продать:" , reply_markup=keyboard)

@router.callback_query(states.Saratov.type)
async def cmd_moscow(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(type=callback_query.data)
    await state.set_state(states.Saratov.fioandphone)
    await callback_query.message.answer("Укажите свое ФИО и контактный номер телефона:")

@router.message(states.Saratov.fioandphone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(fioandphone=message.text)
    await state.set_state(states.Saratov.time)
    await message.answer("Укажите удобное по Мск время для звонка:")

@router.message(states.Saratov.time)
async def get_phone(message: types.Message, state: FSMContext):
    all = await state.get_data()
    BD.insert_saratov(all, message.text)
    for id in config.ADMINS:
        try:
            await bot.send_message(id,f"Новая заявка:\nГород: Саратов\nТип сделки: {all['type']}\nФИО и телефон: {all['fioandphone']}\nУдобное для звонка время: {message.text}")
        except TelegramBadRequest as e:
            print(e)
            continue
    await state.clear()
    await end_phrase(message)

#Получение чек-листа
@router.callback_query(lambda c: c.data == 'checklist')
async def send_check_list(callback_query: types.CallbackQuery):
    document = FSInputFile("check.pdf")
    await callback_query.message.answer_document(document)
    await end_phrase(callback_query)

#Обработка цепочки консультации
@router.callback_query(lambda c: c.data == 'Консультация')
async def cmd_moscow(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.Consult.fioandphone)
    await callback_query.message.answer("Укажите свое ФИО и контактный номер телефона:")

@router.message(states.Consult.fioandphone)
async def get_fio(message: types.Message, state: FSMContext):
    await state.update_data(fioandphone=message.text)
    await state.set_state(states.Consult.comment)
    await message.answer("Кратко опишите тему вопроса:")

@router.message(states.Consult.comment)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(states.Consult.time)
    await message.answer("Укажите удобное по Мск время для звонка:")


@router.message(states.Consult.time)
async def get_time(message: types.Message, state: FSMContext):
    all = await state.get_data()
    BD.insert_consult(all, message.text)
    for id in config.ADMINS:
        try:
            await bot.send_message(id,f"Новая заявка:\nКонсультация\nФИО и телефон: {all['fioandphone']}\n\nТема вопроса: {all['comment']}\nУдобное для звонка время: {message.text}")
        except TelegramBadRequest as e:
            print(e)
            continue
    await state.clear()
    await end_phrase(message)

#Обработка цепочки страховки
@router.callback_query(lambda c: c.data == 'policy')
async def cmd_policy(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(states.Policy.type)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Жизнь', callback_data='Жизнь'), types.InlineKeyboardButton(text='Объект', callback_data='Объект'))
    builder.add(types.InlineKeyboardButton(text='Внутреннюю отделку квартиры', callback_data='Внутреннюю отделку квартиры'), types.InlineKeyboardButton(text='Страховку от потери права собственности', callback_data='right'))
    builder.add(types.InlineKeyboardButton(text='Несколько видов страхования', callback_data='Несколько видов страхования'))
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer("Что нужно застраховать?", reply_markup=keyboard)

@router.callback_query(states.Policy.type)
async def cmd_policy(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'right':
        await state.update_data(type='Страховку от потери права собственности')
    else:
        await state.update_data(type=callback_query.data)
    await state.set_state(states.Policy.offer)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Оформить страховой полис для сделки', callback_data='deal'))
    builder.add(types.InlineKeyboardButton(text='Оформить страховой полис не в рамках ипотеки', callback_data='not a mortgage') , types.InlineKeyboardButton(text='Продлить полис в рамках ипотеки', callback_data='mortgage'))
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    await callback_query.message.answer("Что нужно застраховать?", reply_markup=keyboard)

@router.callback_query(states.Policy.offer)
async def get_offer(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'deal':
        await state.update_data(offer='Оформить страховой полис для сделки')
    elif callback_query.data == 'mortgage':
        await state.update_data(offer='Продлить полис в рамках ипотеки')
    elif callback_query.data == 'not a mortgage':
        await state.update_data(offer='Оформить страховой полис не в рамках ипотеки')
    await state.set_state(states.Policy.fioandphone)
    await callback_query.message.answer("Укажите свое ФИО и контактный номер телефона:")


@router.message(states.Policy.fioandphone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(fioandphone=message.text)
    data = await state.get_data()
    if data['offer'] == 'Продлить полис в рамках ипотеки':
        await state.set_state(states.Policy.position)
        await message.answer("Укажите свою должность:")
    else:
        await state.set_state(states.Policy.time)
        await message.answer("Укажите удобное по Мск время для звонка:")

@router.message(states.Policy.position)
async def get_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(states.Policy.employer)
    await message.answer("Укажите наименование работодателя:")

@router.message(states.Policy.employer)
async def get_employer(message: types.Message, state: FSMContext):
    await state.update_data(employer=message.text)
    await state.set_state(states.Policy.weight)
    await message.answer("Укажите свой вес:")

@router.message(states.Policy.weight)
async def get_weight(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(states.Policy.height)
    await message.answer("Укажите свой рост:")

@router.message(states.Policy.height)
async def get_height(message: types.Message, state: FSMContext):
    await state.update_data(height=message.text)
    await state.set_state(states.Policy.diseases)
    await message.answer("Имеются ли у Вас хронические заболевания:")
    
@router.message(states.Policy.diseases)
async def get_diseases(message: types.Message, state: FSMContext):
    await state.update_data(diseases=message.text)
    await state.set_state(states.Policy.bank)
    await message.answer("Укажите Ваш банк ипотеки:")

@router.message(states.Policy.bank)
async def get_bank(message: types.Message, state: FSMContext):
    await state.update_data(bank=message.text)
    await state.set_state(states.Policy.count)
    await message.answer("Укажите размер кредитных средств:")

@router.message(states.Policy.count)
async def get_count(message: types.Message, state: FSMContext):
    await state.update_data(count=message.text)
    await state.set_state(states.Policy.year)
    await message.answer("Укажите год постройки дома:")

@router.message(states.Policy.year)
async def get_year(message: types.Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(states.Policy.gas)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Да', callback_data='Да'), types.InlineKeyboardButton(text='Нет', callback_data='Нет'))
    keyboard = builder.as_markup(resize_keyboard=True)
    await message.answer("Дом газифицирован:", reply_markup=keyboard)
       
@router.callback_query(states.Policy.gas)
async def get_gas(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(gas=callback_query.data)
    await state.set_state(states.Policy.time)
    await callback_query.message.answer("Укажите удобное по Мск время для звонка:")    

@router.message(states.Policy.time)
async def get_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data['offer'] != 'Продлить полис в рамках ипотеки':
        BD.insert_policy(data, message.text)
        for id in config.ADMINS:
            try:
                await bot.send_message(id,f"Новая заявка:\nСтраховой полис\nСтраховой продукт: {data['type']}\nЦель страховки: {data['offer']}\nФИО и телефон: {data['fioandphone']}\nУдобное для звонка время: {message.text}")
            except TelegramBadRequest as e:
                print(e)
                continue
        await end_phrase(message)
        await state.clear()
    else:
        BD.insert_policy_all(data, message.text)
        for id in config.ADMINS:
            try:
                await bot.send_message(id,f"Новая заявка:\nСтраховой полис\nСтраховой продукт: {data['type']}\nЦель страховки: {data['offer']}\nФИО и телефон: {data['fioandphone']}\nДолжность: {data['position']}\nРаботодатель: {data['employer']}\nВес: {data['weight']}\n Рост: {data['height']}\nХронические заболевания: {data['diseases']}\nБанк: {data['bank']}\nРазмер кредитных средств: {data['count']}\nГод постройки {data['year']}\nГазифицирован: {data['gas']}\nУдобное для звонка время: {message.text}")
            except TelegramBadRequest as e:
                print(e)
                continue
        await end_phrase(message)
        await state.clear()