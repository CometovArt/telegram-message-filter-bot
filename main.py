from pyrogram import Client, filters, compose
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ReplyKeyboardMarkup
from pyrogram.enums import ParseMode, MessageEntityType

import re
import time
from datetime import datetime, timedelta

# текст для проверки синхронизации 2

# https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/asyncio.html
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import DESIGNER_ID, VACANCY_CHAT, userbot, bot, conn, cur, logger
import table_manager
import chat_manager
import message_manager
import answer_manager


@bot.on_message(filters.regex('/test'))
async def test(client, message):    
    user_1 = await userbot.get_users("me")
    user_2 = await bot.get_users("me")
    logger.info(user_1)
    logger.info(user_2)
    # cur.execute("""SELECT chat_id FROM chats""")
    # result = cur.fetchall()
    # # logger.info(result)
    
    # for chat in result:
    #     sql_update = """UPDATE chats SET type = ? WHERE chat_id = ?"""
    #     data = ('single', chat[0])
    #     cur.execute(sql_update, data)
    #     conn.commit()
        
    # cur.execute("""SELECT * FROM chats""")
    # result = cur.fetchone()
    # logger.info(result)
    

async def start():
    info_userbot = await userbot.get_users("me")
    await bot.send_message(chat_id=info_userbot.id, text='Приложение autodesignfindworkbot запущено')


async def main():
    # await compose([userbot,bot])
    
    logger.info('Приложение main запущено')
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=start, 
        trigger="date", run_date=datetime.now()+timedelta(seconds=1)
        )
    scheduler.start()
    
    await compose([userbot,bot])
    

if __name__ == '__main__':
    userbot.run(main())
