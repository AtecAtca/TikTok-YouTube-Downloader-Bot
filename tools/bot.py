from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from tools.logger import get_logger
import os

# Get Telegram Bot API Token when bot started on web or locally
TOKEN = ''
logger = get_logger('tools.bot.py')

async def is_url(message: types.Message) -> bool:
    '''
    Check if url is exist in message

    Get: 
        message: types.Message
    Return: bool
    '''
    try:
        message['entities'][0]['type']
    except IndexError as e:
        logger.exception(e)
        return False
    else:
        logger.debug(f"function is_url return True: {message['entities'][0]['type']}")
        return True

try:
    # init bot with API Token
    bot = Bot(TOKEN)
except Exception as e:
    logger.exception(e)
else:
    # init dispatcher with bot object
    dp = Dispatcher(bot)
    logger.info('Telegram bot connected successfully.')

__all__ = ['bot']