from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp, ChatTypeFilter, Command
from aiogram.utils.exceptions import BotBlocked
from keyboards.inline import Keyboard
from tools.logger import get_logger
from tools.getup import messages, default
from tools.database import db
from tools.bot import bot

# There is place to create new command handler 
# async def cmd_ ... (message: types.Message):

async def cmd_start(message: types.Message):
    '''
    main handler to work with /start commands
    Simple logic: 

        if user is new, bot will add him to db table users
        if user is already in database and press /start, bot will send 'WELCOME' message
    '''

    # get info about user: chat_id, first name and user id
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    uid = message.from_user.id

    logger.debug(f'User {uid} pressed command /start')

    # try to find user by user id in table users
    uid_status = await db.get(table_name='users',
                              items=('user_state',),
                              condition={'tg_id': uid})

    match uid_status:
        # user is new
        case None:

            # insert user to db table users
            await db.insert(table_name='users',
                            items={'tg_id': uid,
                                   'tg_name': first_name,
                                   'tg_username': message.from_user.username,
                                   # use default language
                                   'language': default.get('language'),
                                   # user state now will be 'user'
                                   'user_state': 'user',
                                   # for future features
                                   'is_banned': False})
            # after inserting user to db bot send language keyboard
            await message.answer(text=messages.get('SELECT LANGUAGE'),
                                 reply_markup=kb.get_language_keyboard())

        # user isn't new
        case _:
            # check user's language
            language = await db.get(table_name='users',
                                    items=('language',),
                                    condition={'tg_id': uid})
            # sending 'WELCOME' message with a button for adding bot to chats
            await message.answer(text=messages.get('WELCOME').get(language).format(first_name),
                                 reply_markup=kb.get_add_to_chat_button(), parse_mode='html')


async def cmd_lang(message: types.Message):
    '''
    handler to work with /lang commands
    Send language keyboard to user
    '''
    # get info about user: user id
    uid = message.from_user.id

    logger.debug(f'User {uid} pressed command /language')
    # bot send language keyboard
    await message.answer(text=messages.get('SELECT LANGUAGE'),
                         reply_markup=kb.get_language_keyboard(),
                         parse_mode='html') 


async def cmd_help(message: types.Message):
    '''
    handler to work with /help commands
    Send 'FAQ' message with FAQ button
    '''

    # get info about user: user id
    uid = message.from_user.id

    logger.debug(f'User {uid} pressed command /help')
    # bot send 'FAQ' message with FAQ button
    await message.answer(text=messages.get('FAQ'),
                         reply_markup=kb.get_faq_button(),
                         parse_mode='html')     


def command_handlers(dp: Dispatcher):
    """
    Register all command handlers.
    """
    # register your handler here
    # dp.register_message_handler(cmd_ ..., commands=['...'])
    
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(cmd_help, commands=['help'])
    dp.register_message_handler(cmd_lang, commands=['lang'])


logger = get_logger('handlers.commands.py')
kb = Keyboard()