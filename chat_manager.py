from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import bot, conn, cur, logger
logger.info('Модуль chat_manager подключён')


@bot.on_message(filters.command('chat_list'))
async def chat_list(client, message):
    '''
    Отправляет список чатов сохраненных в базе данных
    
    В этом меню можно включать и отключать получение сообщений из конкретных чатов,
    а так же настраивать для чатов некоторые параметры и удалять их
    '''
    
    # Задаём число, с которого идёт отсчёт пагинации меню
    default_pagination = 0
    
    # Получаем стартовый список кнопок для сообщения
    keyboard = await get_chat_list_keyboard(default_pagination)
    
    # Отправляем сообщение с клавиатурой
    await bot.send_message(
        chat_id=message.chat.id, 
        text='Список чатов в базе данных:', 
        reply_markup=InlineKeyboardMarkup(keyboard)
        )


@bot.on_callback_query(filters.regex('^chat_list_pagination:'))
async def chat_list_pagination(client, callback_query): 
    ''' Редактирует сообщение со списком чатов отправляя новые результаты '''
    
    # Пустой ответ на нажатие кнопки. Снимает иконку часов
    await callback_query.answer()
    
    # Делим callback_data на составляющие части и определяем type и step
    callback_data = callback_query.data.split(':')

    # Определяем новое значение pagination
    if len(callback_data) != 3:
        # Корректная callback_data должна состоять ровно из трёх элементов
        # Например: 'chat_list_pagination:back:{pagination}'
        # Если состав отличен от этого, значит функция вызвана не кнопками 'next' или 'back'
        # Поэтому мы задаём число пагинации равным 0, чтобы отобразить первую страницу результатов
        # Это так же значит, что никакая другая callbacl_data в chat_manager не может состоять из трёх элементов
        pagination = 0
    else:
        # Получив корректную callback_data определяем type/step и считаем следующий шаг пагинации
        
        # type_pagination — имеет значение 'next' или 'back'
        # step_pagination — предыдущий шаг пагинации, всегда кратен 10
        _, type_pagination, step_pagination = callback_data
        
        if type_pagination == 'next':
            # Если нажата кнопка next, то к текущему шагу пагинации прибавляем 10
            # Благодаря этому отобразится 10 следующих результатов
            pagination = int(step_pagination) + 10
        elif type_pagination == 'back':
            # Если нажата кнопка back, то от текущего шага пагинации отнимаем 10
            # Благодаря этому отобразится 10 предыдущих результатов
            pagination = int(step_pagination) - 10
    
    # Получаем новый список кнопок для сообщения
    keyboard = await get_chat_list_keyboard(pagination)
    
    # Редактируем уже отправленное сообщение с клавиатурой
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id, 
        message_id=callback_query.message.id, 
        reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    
async def get_chat_list_keyboard(pagination):
    ''' Получает список чатов из базы данных и генерирует из них клавиатуру '''
    
    # Получаем из базы данных список чатов
    # 'LIMIT 11' определяет количество строк. Нам нужно на одну строку больше 10, чтобы назначить кнопки
    # 'OFFSET ?' определяет сколько строк будет пропущено. Это значение равно шагу пагинации
    cur.execute("""SELECT chat_id, on_air, title FROM chats LIMIT 11 OFFSET ?""",(pagination,))
    result = cur.fetchall()
    
    # Создаём пустой список, в который будем добавлять кнопки клавиатуры
    keyboard = []
    
    # С помощью цикла генерируем 10 кнопок клавиатуры, каждая из которых равна строке чата
    for chat in result:
        # Распаковываем кортеж в отдельные переменные
        # select_chat_status — имеет значение True или False
        select_chat_id, select_chat_status, select_chat_title = chat
        
        # Определяем иконку статуса
        # Если статус True, то '🟢'. Если False, то '🔴'
        on_air = get_on_air_icon(select_chat_status)
        
        # Создаём объект кнопки
        button_chat = InlineKeyboardButton(
            text=f'{on_air} {select_chat_title}', 
            callback_data=f'edit_select_chat:{select_chat_id}'
            )
        
        # Добавляем кнопку в список клавиатуры
        keyboard.append([button_chat])
        
        # Нам нужно ровно 10 или меньше кнопок для выдачи
        # Поэтому заканчиваем обработку когда список кнопок полон
        if len(keyboard) == 10:
            break
    
    # Создаём объекты кнопок next и back
    next_button = InlineKeyboardButton('Дальше ▶️', callback_data=f'chat_list_pagination:next:{pagination}')
    back_button = InlineKeyboardButton('◀️ Назад', callback_data=f'chat_list_pagination:back:{pagination}')
    
    # Определяем какие кнопки навигации нужно добавить в клавиатуру
    
    # Если количество строк, полученных из базы данных меньше 11
    # значит для следующей страницы не будет результатов, кнопка next_button не нужна
    if len(result) < 11 and pagination == 0:
        # Если pagination=0, значит это первая страница, кнопка back_button тоже не нужна
        pass
    elif len(result) < 11:
        # Если строк меньше 11, скорее всего это последняя страница списка, нужна только back_button
        keyboard.append([back_button])
    elif pagination >= 10:
        # Если строк больше 10, значит мы можем показать следующую страницу
        keyboard.append([back_button, next_button])
    elif pagination == 0:
        # Если pagination=0, значит это первая страница
        keyboard.append([next_button])
        
    return keyboard

    
@bot.on_callback_query(filters.regex('^edit_select_chat:'))
async def edit_select_chat(client, callback_query):
    ''' По нажатию на кнопку чата открывает меню для работы с ним '''
    
    # Пустой ответ на нажатие кнопки. Снимает иконку часов
    await callback_query.answer()
    
    # Делим callback_data на составляющие части и определяем select_chat_id
    callback_data = callback_query.data.split(':')
    _, select_chat_id = callback_data
    
    # Получаем из базы данных полную информацию о чате
    cur.execute("""SELECT on_air, title, type FROM chats WHERE chat_id = ?""",(select_chat_id,))
    result = cur.fetchone()
    
    # Распаковываем кортеж в отдельные переменные
    # select_chat_status — имеет значение True или False
    # select_chat_type — имеет значение 'single' или 'multi'
    select_chat_status, select_chat_title, select_chat_type = result
    
    # Определяем иконку статуса
    # Если статус True, то '🟢'. Если False, то '🔴'
    on_air = get_on_air_icon(select_chat_status)
    
    # Собираем объект клавиатуры для сообщения
    
    keyboard = [
        # Нажатие на первую кнопку меняет статус чата True/False
        [InlineKeyboardButton(
            text=f'{on_air} {select_chat_title}', 
            callback_data=f'change_status_select_chat:{select_chat_id}'
            )],
        # Нажатие на вторую кнопку меняет тип чата single/multi
        [InlineKeyboardButton(
            text=f'Типа чата: {select_chat_type}', 
            callback_data=f'change_type_select_chat:{select_chat_id}'
            )],
        # Нажатие на третью кнопку мгновенно удаляет чат из базы данных
        [InlineKeyboardButton(
            text='Удалить чат из базы данных', 
            callback_data=f'delete_chat_db:{select_chat_id}'
            )],
        # Нажатие на четвертую кнопку возвращает на первую страницу списка чатов
        [InlineKeyboardButton(
            text='Вернуться назад', 
            callback_data='chat_list_pagination:'
            )]
        ]
    
    # Редактируем уже отправленное сообщение с клавиатурой
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id, 
        message_id=callback_query.message.id, 
        reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    
def get_on_air_icon(select_chat_status):
    ''' Просто определяет иконку для статуса '''
    if select_chat_status:
        return '🟢'
    elif not select_chat_status:
        return '🔴'
    
    
@bot.on_callback_query(filters.regex('^change_type_select_chat:'))
async def change_type_select_chat(client, callback_query):
    ''' Меняет тип чата в базе данных '''
    
    # Пустой ответ на нажатие кнопки. Снимает иконку часов
    await callback_query.answer()
    
    # Делим callback_data на составляющие части и определяем select_chat_id
    callback_data = callback_query.data.split(':')
    _, select_chat_id = callback_data
    
    # Получаем из базы данных полную информацию о чате
    cur.execute("""SELECT on_air, title, type FROM chats WHERE chat_id = ?""",(select_chat_id,))
    result = cur.fetchone()
    
    # Распаковываем кортеж в отдельные переменные
    # select_chat_status — имеет значение True или False
    # select_chat_type — имеет значение 'single' или 'multi'
    select_chat_status, select_chat_title, select_chat_type = result
    
    # Меняем тип чата в зависимости от текущего
    if select_chat_type == 'single':
        select_chat_type = 'multi'
    elif select_chat_type == 'multi':
        select_chat_type = 'single'
    
    # Обновляем информацию о чате в базе данных
    sql_update = """UPDATE chats SET type = ? WHERE chat_id = ?"""
    data = (select_chat_type, select_chat_id)
    cur.execute(sql_update, data)
    conn.commit()
    
    # Повторно вызываем страницу меню конкретного чата для обновления клавиатуры
    await edit_select_chat(client, callback_query)
    
    
@bot.on_callback_query(filters.regex('^change_status_select_chat:'))
async def change_status_select_chat(client, callback_query):
    ''' Меняет статус чата в базе данных '''
    
    # Пустой ответ на нажатие кнопки. Снимает иконку часов
    await callback_query.answer() 
    
    # Делим callback_data на составляющие части и определяем select_chat_id
    callback_data = callback_query.data.split(':')
    _, select_chat_id = callback_data
    
    # Получаем из базы данных полную информацию о чате
    cur.execute("""SELECT on_air, title, type FROM chats WHERE chat_id = ?""",(select_chat_id,))
    result = cur.fetchone()
    
    # Распаковываем кортеж в отдельные переменные
    # select_chat_status — имеет значение True или False
    # select_chat_type — имеет значение 'single' или 'multi'
    select_chat_status, select_chat_title, select_chat_type = result
    
    # Меняем статус чата в зависимости от текущего
    select_chat_status = not select_chat_status
    
    # Обновляем информацию о чате в базе данных
    sql_update = """UPDATE chats SET on_air = ? WHERE chat_id = ?"""
    data = (select_chat_status, select_chat_id)
    cur.execute(sql_update, data)
    conn.commit()
    
    # Повторно вызываем страницу меню конкретного чата для обновления клавиатуры
    await edit_select_chat(client, callback_query)
    
    
@bot.on_callback_query(filters.regex('^delete_chat_db:'))
async def chat_update(client, callback_query):
    ''' Удаляет чат из базы данных '''
    
    # Пустой ответ на нажатие кнопки. Снимает иконку часов
    await callback_query.answer()
    
    # Делим callback_data на составляющие части и определяем select_chat_id
    callback_data = callback_query.data.split(':')
    _, select_chat_id = callback_data
    
    # Удаляем строку чата из базы данных
    cur.execute("""DELETE FROM chats WHERE chat_id = ?""",(select_chat_id,))
    result = cur.fetchone()
    
    # Повторно вызываем страницу списка чатов
    await chat_list_pagination(client, callback_query)