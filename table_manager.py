from config import conn, cur, logger
logger.info('Модуль table_manager подключён')

# На всякий случай при каждом запуске проверяем, созданы ли таблицы
# Заодно держим визуализацию их колонок
try:
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chats(
        chat_id INT PRIMARY KEY,
        title TEXT,
        on_air INT,
        type TEXT);
        """
        )
    conn.commit()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS white_list(
        word TEXT PRIMARY KEY);
        """
        )
    conn.commit()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS black_list(
        word TEXT PRIMARY KEY);
        """
        )
    conn.commit()
    
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ban_users(
        user INT PRIMARY KEY);
        """
        )
    conn.commit()
except:
    pass


# # Создание базового набора слов для белого и черного листа

# white_start_list = ["дизайн", "tilda", "лендинг"]
# black_start_list = ["#помогу", "#резюме", "запись на консультацию"]

# sql_update = """INSERT OR IGNORE INTO white_list (word) VALUES (?)"""
# cur.executemany(sql_update, [(word,) for word in white_start_list])
# conn.commit()

# sql_update = """INSERT OR IGNORE INTO black_list (word) VALUES (?)"""
# cur.executemany(sql_update, [(word,) for word in black_start_list])
# conn.commit()



# # # Базовые функции sqllite

# # Добавление строки
# sql_update = """INSERT OR IGNORE INTO chats (chat_id, title, on_air) VALUES (?, ?, ?)"""
# data = (chat.id, chat.title, 0)
# cur.execute(sql_update, data)
# conn.commit()

# # Поиск строки
# cur.execute("""SELECT chat_id, on_air FROM chats""")
# result = cur.fetchall()

# # Обновление строки
# sql_update = """UPDATE chats SET on_air = ? WHERE chat_id = ?"""
# data = ('0', chat[0])
# cur.execute(sql_update, data)
# conn.commit()

# # Удаление строки
# cur.execute("""DELETE from white_list where word = ?""",(word,))
# conn.commit()

# # Удаление колонки
# cur.execute("""ALTER TABLE chats DROP COLUMN setting_message""")
# conn.commit()

# Добавление колонки
# cur.execute("""ALTER TABLE chats ADD COLUMN type TEXT""")
# conn.commit()