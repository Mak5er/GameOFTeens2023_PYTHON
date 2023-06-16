import asyncio

from collections import deque
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json

stack = deque()

bot = Bot(token="6141417763:AAE8EH-x1TLaGh_MCrK4aIXzrvvSV3PQFGc")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def save_language_choice(user_id, language):
    data = {}

    try:
        with open('language_data.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if str(user_id) in data:
        data[str(user_id)] = language
    else:
        data[str(user_id)] = language

    with open('language_data.json', 'w') as file:
        json.dump(data, file)


def check_user_exists(user_id):
    try:
        with open('language_data.json', 'r') as file:
            data = json.load(file)
            return str(user_id) in data
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def get_user_language(user_id):
    try:
        with open('language_data.json', 'r') as file:
            data = json.load(file)
            return data.get(str(user_id))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    name = message.from_user.full_name
    user_id = message.from_user.id
    await bot.send_chat_action(user_id, 'typing')
    await asyncio.sleep(0.5)

    lang_keyboard = types.InlineKeyboardMarkup()
    lang_keyboard.add(types.InlineKeyboardButton(text="Українська🇺🇦", callback_data="lang_ua"),
                      types.InlineKeyboardButton(text="English🇬🇧", callback_data="lang_en"))

    if check_user_exists(user_id):
        await start_taryf(message)
    else:
        await message.reply(f"""Привіт *{name}*, будьласка обери мову!  
Hi *{name}*, please choose your language!""",
                            reply_markup=lang_keyboard, parse_mode="Markdown")


@dp.message_handler(commands=['language'])
async def change_lang(message: types.Message):
    user_id = message.from_user.id
    await bot.send_chat_action(user_id, 'typing')
    await asyncio.sleep(0.5)
    lang_keyboard = types.InlineKeyboardMarkup()
    lang_keyboard.add(types.InlineKeyboardButton(text="Українська🇺🇦", callback_data="lang_ua"),
                      types.InlineKeyboardButton(text="English🇬🇧", callback_data="lang_en"))

    await message.reply(f"""Будьласка обери мову!  
Please choose your language!""",
                        reply_markup=lang_keyboard, parse_mode="Markdown")


async def start_taryf(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name
    user_language = get_user_language(user_id)

    if user_language == "ua":
        start_keyboard_ua = types.InlineKeyboardMarkup()
        start_keyboard_ua.add(types.InlineKeyboardButton(text="🔎Почати підбір", callback_data="age_survey"))
        await bot.send_message(user_id, f"Привіт *{name}*! Я допоможу тобі знайти найкращий для тебе тариф Lifecell!",
                               reply_markup=start_keyboard_ua, parse_mode="Markdown")

    elif user_language == "en":
        start_keyboard_en = types.InlineKeyboardMarkup()
        start_keyboard_en.add(types.InlineKeyboardButton(text="🔎Start selection", callback_data="age_survey"))
        await bot.send_message(user_id, f"Hello *{name}*! I will help you to find the best Lifecell tariff!",
                               reply_markup=start_keyboard_en, parse_mode="Markdown")


@dp.callback_query_handler(lambda call: call.data == 'age_survey')
async def age_select(call: types.CallbackQuery):
    name = call.from_user.full_name
    user_id = call.from_user.id
    user_language = get_user_language(user_id)

    if user_language == "ua":
        understood_keyboard_ua = types.InlineKeyboardMarkup()
        understood_keyboard_ua.add(types.InlineKeyboardButton(text="✅Зрозуміло", callback_data="understood"))

        await call.message.edit_text(
            text=f"*{name}*, щоб підібрати найкращий тариф вам потрібно відповісти на декілька запитань.",
            reply_markup=understood_keyboard_ua, parse_mode="Markdown")

    elif user_language == "en":
        understood_keyboard_en = types.InlineKeyboardMarkup()
        understood_keyboard_en.add(types.InlineKeyboardButton(text="✅Understood", callback_data="understood"))

        await call.message.edit_text(
            text=f"*{name}*, to choose the best tariff, you need to answer a few simple questions.",
            reply_markup=understood_keyboard_en, parse_mode="Markdown")

    # Додаємо поточну функцію до стеку
    stack.append(age_select)


@dp.callback_query_handler(lambda call: call.data == 'understood')
async def undersood_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_language = get_user_language(user_id)

    if user_language == "ua":
        less_than_eighteen = types.InlineKeyboardButton(text="Менше 18", callback_data="less_than_eighteen")
        more_than_eighteen = types.InlineKeyboardButton(text="Більше 18", callback_data="more_than_eighteen")
        back_button = types.InlineKeyboardButton(text="⬅ Назад", callback_data="back")

        age_keyboard = types.InlineKeyboardMarkup()
        age_keyboard.row(less_than_eighteen, more_than_eighteen)
        age_keyboard.row(back_button)

        await call.message.edit_text(text="""*Перше запитання*:
Будьласка оберіть ваш вік.""", reply_markup=age_keyboard, parse_mode="Markdown")
    elif user_language == "en":
        less_than_eighteen = types.InlineKeyboardButton(text="Less than 18", callback_data="less_than_eighteen")
        more_than_eighteen = types.InlineKeyboardButton(text="More than 18", callback_data="more_than_eighteen")
        back_button = types.InlineKeyboardButton(text="⬅ Back", callback_data="back")

        age_keyboard = types.InlineKeyboardMarkup()
        age_keyboard.row(less_than_eighteen, more_than_eighteen)
        age_keyboard.row(back_button)

        await call.message.edit_text(text="""*First question*:
Please select your age.""", reply_markup=age_keyboard, parse_mode="Markdown")

    # Додаємо поточну функцію до стеку
    stack.append(undersood_handler)

@dp.callback_query_handler(lambda call: call.data == 'less_than_eighteen')
async def less_than_eighteen(call: types.CallbackQuery):
    name = call.from_user.full_name
    user_id = call.from_user.id
    user_language = get_user_language(user_id)

    if user_language == "ua":
        school_life = types.InlineKeyboardButton(text="📲Підключити", url="https://www.lifecell.ua/uk/mobilnij-zvyazok/taryfy/shkilniy/")
        not_interest = types.InlineKeyboardButton(text="❌Не цікаво", callback_data="more_than_eighteen")
        back_button = types.InlineKeyboardButton(text="⬅ Назад", callback_data="back")


        school_life_keyboard = types.InlineKeyboardMarkup()
        school_life_keyboard.row(school_life)
        school_life_keyboard.row(not_interest)
        school_life_keyboard.row(back_button)

        await call.message.edit_text(text=f"*{name}*, ми помітили, що вам менше 18-ти. Тому пропонуємо вам тариф '*Шкільний Лайф*', який зроблений спеціально для школярів.", parse_mode="Markdown", reply_markup=school_life_keyboard)

    if user_language == "en":
            school_life = types.InlineKeyboardButton(text="📲Connect", url="https://www.lifecell.ua/uk/mobilnij-zvyazok/taryfy/shkilniy/")
            not_interest = types.InlineKeyboardButton(text="❌Not interested", callback_data="more_than_eighteen")
            back_button = types.InlineKeyboardButton(text="⬅ Back", callback_data="back")


            school_life_keyboard = types.InlineKeyboardMarkup()
            school_life_keyboard.row(school_life)
            school_life_keyboard.row(not_interest)
            school_life_keyboard.row(back_button)

            await call.message.edit_text(text=f"*{name}*, we noticed that you are under 18. That's why we offer you the '*School Life*' tariff, which is specially designed for schoolchildren.", parse_mode="Markdown", reply_markup=school_life_keyboard)

    stack.append(less_than_eighteen)


@dp.callback_query_handler(lambda call: call.data == 'more_than_eighteen')
async def more_than_eighteen(call: types.CallbackQuery):
    name = call.from_user.full_name
    user_id = call.from_user.id
    user_language = get_user_language(user_id)

    if user_language == "ua":
        own_button = types.InlineKeyboardButton(text="🙋‍♂️Для себе", callback_data="back")
        family_button = types.InlineKeyboardButton(text="👨‍👩‍👧‍👦Для сім'ї", callback_data="back")
        for_gadget_button = types.InlineKeyboardButton(text="💻Для Ґаджета", callback_data="back")
        back_button = types.InlineKeyboardButton(text="⬅ Назад", callback_data="back")

        usage_select = types.InlineKeyboardMarkup()
        usage_select.row(own_button)
        usage_select.row(family_button, for_gadget_button )
        usage_select.row(back_button)

        await call.message.edit_text(
            text=f"*{name}*, для якого типу використання вам потрібен тариф?", parse_mode="Markdown", reply_markup=usage_select)

    stack.append(more_than_eighteen)


@dp.callback_query_handler(lambda call: call.data == 'back')
async def back_handler(call: types.CallbackQuery):
    if len(stack) > 1:
        # Видаляємо поточну функцію зі стеку
        stack.pop()
        # Отримуємо попередню функцію зі стеку
        previous_function = stack[-1]
        # Викликаємо попередню функцію
        await previous_function(call)
    else:
        # Якщо стек порожній, виконуємо дії для випадку, коли немає попередньої функції
        await call.message.edit_reply_markup(reply_markup=None)

@dp.callback_query_handler()
async def language_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    language = call.data.split('_')[1]
    await bot.send_chat_action(user_id, 'typing')
    await asyncio.sleep(0.5)

    if language == "ua":
        await call.message.edit_text(text="""Ви обрали українську мову🇺🇦!
Ви завжди можете змінити мову написавши /language
Тепер ще раз напишіть /start!
""")
        save_language_choice(user_id, language)
        await start_taryf(call.message)


    elif language == "en":
        await call.message.edit_text(text="""You have successfully selected English🇬🇧!
You can always change the language by writing /language
Now type /start again!
""")
        save_language_choice(user_id, language)


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
