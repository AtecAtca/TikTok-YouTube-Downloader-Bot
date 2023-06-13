from aiogram.utils import executor
from tools.logger import get_logger
from tools.bot import bot, dp
from tools.database import db
from handlers.inlines import inline_handlers
from handlers.commands import command_handlers
from handlers.messages import message_handlers
from handlers.callbacks import callback_handlers
from userbot.UserBot import userbot
import os

# WEBHOOK_URL from "ngrok https http://localhost:5000
WEBHOOK_PATH = ''
WEBHOOK_URL = ''
WEBAPP_HOST = ''
WEBAPP_PORT = 

async def on_startup(_) -> None:
    """
    Will be executed when the bot starts
    """

    ### await bot.set_webhook(os.environ.get('URL_APP'))
    await bot.set_webhook(WEBHOOK_URL)
    logger.info('Executor started.')

async def on_shutdown(_) -> None:
    """
    Will be executed when the bot is closed
    """
    #await bot.delete_webhook()
    await bot.delete_webhook()
    db.close_on_shutdown()
    logger.info('Executor finished.')

def run(webhook:bool=False) -> None:
    """
    :param webhook: default False. If True, func will start with long polling method
    """
    if webhook:
        executor.start_webhook(dispatcher=dp,
                               webhook_path=WEBHOOK_PATH,
                               on_startup=on_startup,
                               on_shutdown=on_shutdown,
                               skip_updates=True,
                               host=WEBAPP_HOST,
                               port=WEBAPP_PORT)
    else:
        executor.start_polling(dispatcher=dp,
                               skip_updates=True)

logger = get_logger('main.py')

inline_handlers(dp)
command_handlers(dp)
callback_handlers(dp)
message_handlers(dp)


if __name__ == '__main__':
    run(webhook=True)