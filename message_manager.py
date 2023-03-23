from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode, MessageEntityType

import re
import time
    
from config import DESIGNER_ID, VACANCY_CHAT, userbot, bot, conn, cur, logger
logger.info('Модуль message_manager подключён')


@userbot.on_message(~filters.private & ~filters.bot)
async def new_message(client, message):
    # Запускаем таймер для подсчета времени на выполнение скрипта
    start_time = time.time()
    
    # Определяем текст сообщения в зависимости от типа сообщения, если текста нет, то пропускаем
    # Причина: у сообщений содержащих картинки нет параметра text, вместо него caption
    if not message.text:
        if message.photo and message.caption:
            message_text = message.caption
        else:
            return
    else:
        message_text = message.text
        
    # Проверяем, есть ли чат в базе данных и получаем его статус on_air (True/Flase)
    cur.execute("""SELECT on_air FROM chats WHERE chat_id = ?""",(message.chat.id,))
    result_chat = cur.fetchone()
    
    # Если чата нет в базе данных, то отправляем чат на обработку
    if not result_chat:
        await chats_manager(message)
        return
    
    # Если у чата статус False, то прекращаем операцию
    if not result_chat[0]:
        return
        
    # Проверяем, есть ли отправитель сообщения в базе данных по бану
    if message.from_user:
        cur.execute("""SELECT user FROM ban_users WHERE user = ?""",(message.from_user.id,))
        if cur.fetchone():
            return
    
    # Если все проверки прошли успешно, то начинаем обработку сообщения
    await send_vacancy_message(message, message_text, start_time)


async def send_vacancy_message(message, message_text, start_time):    
    # Get white and black lists from the database
    cur.execute("""SELECT word FROM white_list""")
    white_result = cur.fetchall()
    white_list = [word for tuple in white_result for word in tuple]
    
    cur.execute("""SELECT word FROM black_list""")
    black_result = cur.fetchall()
    black_list = [word for tuple in black_result for word in tuple]
    
    
    text_lower = message_text.lower()
    
    for white_word in white_list:
        if white_word in text_lower:
            word = white_word
            break
        return
        
    for black_word in black_list:
        if black_word in text_lower:
            return
            
    # # Если в сообщении содержатся слова из белого списка, и нет слов из черного, то отправляем сообщение в чат
    # if any(white_dict.values()) and not any(black_dict.values()):        
    #     # End the timer
    
    button_list = []
    
    open_button = InlineKeyboardButton('📄', url=message.link)
    button_list.append(open_button)
    
    mention_status = False
    if message.entities:
        for entities in message.entities:
            if entities.type == MessageEntityType.MENTION:
                matches = re.findall('@\S*', message.text)
                user = matches[0]
                mention_status = True
                break
    
    if message.from_user and mention_status:
        callback_data = f'answer:{user}:{message.from_user.id}:{message.chat.id}:{message.id}'
        answer_button = InlineKeyboardButton(f'✉️ {user}', callback_data=callback_data)
        button_list.append(answer_button)
    elif mention_status:
        callback_data = f'answer:{user}:{user}:{message.chat.id}:{message.id}'
        answer_button = InlineKeyboardButton(f'✉️ {user}', callback_data=callback_data)
        button_list.append(answer_button)
    elif message.from_user:
        callback_data = f'answer:{message.from_user.id}:{message.from_user.id}:{message.chat.id}:{message.id}'
        answer_button = InlineKeyboardButton('✉️', callback_data=callback_data)
        button_list.append(answer_button)
    
    if message.from_user:
        ban_button = InlineKeyboardButton('🚫', callback_data=f'b:{message.from_user.id}')
        button_list.append(ban_button)

    reply_markup = InlineKeyboardMarkup([button_list])
    
    # End the timer
    end_time = time.time()
    
    text = (
        f'Сообщение из чата «{message.chat.title}»\n'
        f'__{end_time - start_time}__ | [{word}]\n\n'
        f'{message_text}'
        )
    
    await bot.send_message(chat_id=VACANCY_CHAT, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


async def chats_manager(message):
    chat = message.chat
    
    text = (
        f'Появился новый чат:\n'
        f'«{chat.title}»\n\n'
        f'Получать вакансии из этого чата?'
        )
    
    keyboard = [
        [
            InlineKeyboardButton('Да 📥', callback_data=f'y:{chat.id}'),
            InlineKeyboardButton('Нет 🗑', callback_data=f'n:{chat.id}')
            ],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    sends = await bot.send_message(chat_id=DESIGNER_ID, text=text, reply_markup=reply_markup)
    
    sql_update = """INSERT OR IGNORE INTO chats (chat_id, title, on_air, type) VALUES (?, ?, ?, ?)"""
    data = (chat.id, chat.title, 0, 'single')
    cur.execute(sql_update, data)
    conn.commit()
    
    
@bot.on_callback_query(filters.regex('^b:'))
async def user_ban_list(client, callback_query):
    user_id = callback_query.data[2:]
    message_id = callback_query.message.id
    chat_id = callback_query.message.chat.id
        
    sql_update = """INSERT OR IGNORE INTO ban_users (user) VALUES (?)"""
    cur.execute(sql_update, (user_id,))
    conn.commit()
    
    await bot.delete_messages(chat_id=chat_id, message_ids=message_id)
    text = f'Пользователь «{user_id}» добавлен в черный список'
    await bot.send_message(chat_id=callback_query.message.chat.id, text=text)
    
    
@bot.on_callback_query(filters.regex('^[y,n]:'))
async def chats_white_list(client, callback_query):
    answer = callback_query.data[0]
    chat_id = callback_query.data[2:]

    if answer == 'y':
        on_air = True
    elif answer == 'n':
        on_air = False
        
    sql_update = """UPDATE chats SET on_air = ? WHERE chat_id = ?"""
    data = (on_air, chat_id)
    cur.execute(sql_update, data)
    conn.commit()
    
    result = f'Чат {chat_id} обработан по тегу {on_air}'
    logger.info(result)
    
    await bot.delete_messages(chat_id=callback_query.message.chat.id, message_ids=callback_query.message.id)
    
    
@bot.on_message(filters.regex('^white:') | filters.regex('^black:'))
async def word_list(client, message):
    type_list = message.text[0:5] + '_list'
    word = message.text[7:].lower()
    
    cur.execute("""SELECT word FROM {} WHERE word = ?""".format(type_list),(word,))
    result = cur.fetchone()

    if not result:
        sql_update = """INSERT OR IGNORE INTO {} (word) VALUES (?)""".format(type_list)
        cur.execute(sql_update, (word,))
        conn.commit()
        
        text = f'Слово «{word}» добавлено в {type_list}'
        await bot.send_message(chat_id=DESIGNER_ID, text=text)
    else:
        text = f'Слово «{word}» уже есть в {type_list}'
        await bot.send_message(chat_id=DESIGNER_ID, text=text)