from pyrogram import filters
from pyrogram.types import InputMediaPhoto

from config import DESIGNER_ID, VACANCY_CHAT, userbot, bot, conn, cur, logger
logger.info('Модуль answer_manager подключён')


@bot.on_callback_query(filters.regex('^answer:'))
async def send_photo(client, callback_query):
    callback_data = callback_query.data.split(':')
    user = callback_data[1]
    user_id = callback_data[2]
    chat_id = callback_data[3]
    message_id = callback_data[4]
    
    text = (
        f'Здравствуйте, я графический и веб дизайнер :)\n\n'
        f'Выше работы по одному из последних проектов. Работаю в Figma, Tilda, Photoshop, '
        f'Illustrator, After Effects, PowerPoint. Могу сделать почти весь спектр дизайн-направлений, '
        f'включая motion. Имею большой опыт в монтаже видео и создании телеграм-ботов с нуля'
    )
    
    try:
        await userbot.send_media_group(
            chat_id = user,
            media = [
                InputMediaPhoto('last_portfolio_1.jpg'),
                InputMediaPhoto('last_portfolio_2.jpg'),
                InputMediaPhoto('last_portfolio_3.jpg'),
                InputMediaPhoto('last_portfolio_4.jpg'),
                InputMediaPhoto('last_portfolio_5.jpg'),
                InputMediaPhoto('last_portfolio_6.jpg'),
                InputMediaPhoto('last_portfolio_7.jpg'),
                InputMediaPhoto('last_portfolio_8.jpg'),
                InputMediaPhoto('last_portfolio_9.jpg'),
                InputMediaPhoto('last_portfolio_10.jpg', caption=text),
                ]
            )
        text_answer = f'Сообщение отправлено: {callback_query.message.link}'
    except:
        try:
            await userbot.forward_messages(
                chat_id='me',
                from_chat_id=chat_id,
                message_ids=message_id
                )
            await userbot.send_media_group(
                chat_id = user,
                media = [
                    InputMediaPhoto('last_portfolio_1.jpg'),
                    InputMediaPhoto('last_portfolio_2.jpg'),
                    InputMediaPhoto('last_portfolio_3.jpg'),
                    InputMediaPhoto('last_portfolio_4.jpg'),
                    InputMediaPhoto('last_portfolio_5.jpg'),
                    InputMediaPhoto('last_portfolio_6.jpg'),
                    InputMediaPhoto('last_portfolio_7.jpg'),
                    InputMediaPhoto('last_portfolio_8.jpg'),
                    InputMediaPhoto('last_portfolio_9.jpg'),
                    InputMediaPhoto('last_portfolio_10.jpg', caption=text),
                    ]
                )
            text_answer = f'Сообщение отправлено после форварда в личку: {callback_query.message.link}'
        except:
            text_answer = f'Сообщение не отправлено: {callback_query.message.link}'
    finally:
        await bot.send_message(chat_id=callback_query.message.chat.id, text=text_answer)
    
    
@userbot.on_message(filters.me & filters.regex('^Здравствуйте$'))
async def send_photo_from_text(client, message):
    text = (
        f'Я графический и веб дизайнер :)\n\n'
        f'Выше работы по одному из последних проектов. Работаю в Figma, Tilda, Photoshop, '
        f'Illustrator, After Effects, PowerPoint. Могу сделать почти весь спектр дизайн-направлений, '
        f'включая motion. Имею большой опыт в монтаже видео и создании телеграм-ботов с нуля'
    )
    await userbot.send_media_group(
        chat_id = message.chat.id,
        media = [
            InputMediaPhoto('last_portfolio_1.jpg'),
            InputMediaPhoto('last_portfolio_2.jpg'),
            InputMediaPhoto('last_portfolio_3.jpg'),
            InputMediaPhoto('last_portfolio_4.jpg'),
            InputMediaPhoto('last_portfolio_5.jpg'),
            InputMediaPhoto('last_portfolio_6.jpg'),
            InputMediaPhoto('last_portfolio_7.jpg'),
            InputMediaPhoto('last_portfolio_8.jpg'),
            InputMediaPhoto('last_portfolio_9.jpg'),
            InputMediaPhoto('last_portfolio_10.jpg', caption=text),
            ]
        )