import logging
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from os import getenv, remove, listdir
from pytube import YouTube
from string import punctuation
from io import BytesIO
import requests

PATH = listdir('C:\\Bot')
BOT_ID = 
API_ID = 
API_HASH = ''
SESSION = ''
PHONE = ''

def check_session() -> bool:
    '''
    Check if session is available.

    Return: bool
    '''
    if f'{SESSION}.session' and f'{SESSION}.session-journal' in PATH:
        logger.debug(f'function check_session return True')
        return True    
    else:
        logger.debug(f'function check_session return False')
        return False


def download_content(content: str, uid: int, resolution: str, yt_title: str, type_: str) -> None:
    '''
    Download youtube video/audio to path C:\\Bot\\Data\\...

    Get:
        content: video or audio
        uid: Telegram user id
        resolution: 720p or 360p or 144p or mp3 or m4a
        yt_title: filename. All spaces replaced to '_'
        type: .mp4 or .mp3 or .m4a

    Return: None
    '''
    logger.debug(f'Function download_content start downloading: {yt_title}{type_}')
    content.download(output_path=f'C:\\Bot\\Data\\{uid}\\{resolution}\\', filename=f'{yt_title}{type_}')
    logger.debug(f'Function download_content finish downloading: {yt_title}{type_}')


async def check_video(app, message) -> None:
    '''
    Get message from Bot started with /v

    Return: None

    '''
    logger.debug(f'Get from Bot: {message.text}')

    # init variables
    cmd = resolution = yt_id = chat_id = msg_id = uid = msg_to_delete = None

    # split message data from Bot
    # with message to delete when len = 7
    message_from_bot = message.text.split(' ')
    if len(message_from_bot) == 7:
        cmd, resolution, yt_id, chat_id, msg_id, uid, msg_to_delete = message_from_bot
    elif len(message_from_bot) == 6:
        cmd, resolution, yt_id, chat_id, msg_id, uid = message_from_bot

    # get yt_title for filename
    yt_obj = YouTube(f'https://youtu.be/{yt_id}')
    yt_title = yt_obj.title.translate(str.maketrans(' ', '_', punctuation))
    
    # create filepath for downloading
    type_ = '.mp4'
    path = f'C:\\Bot\\Data\\{uid}\\{resolution}\\{yt_title}{type_}'

    # get thumb from video
    video = yt_obj.streams.filter(res=resolution).first()
    thumb = yt_obj.thumbnail_url

    # downloading starts here
    download_content(video, uid, resolution, yt_title, type_)

    # create message data to send to Bot with videofile
    if msg_to_delete is not None:
        message_to_bot = f'{resolution} {yt_id} {chat_id} {msg_id} {uid} {msg_to_delete}'
    else:
        message_to_bot = f'{resolution} {yt_id} {chat_id} {msg_id} {uid}'

    # sending video to Bot with message data 
    await app.send_video(chat_id=BOT_ID, video=path, caption=message_to_bot,
                         thumb=BytesIO(requests.get(thumb).content),
                         parse_mode=ParseMode.HTML)
    # delete file from path
    try:
        delete_file(path)
    except (FileNotFoundError, PermissionError) as e:
        logger.exception(e)
    else:
        pass


async def check_audio(app, message) -> None:
    '''
    Get message from Bot started with /a

    Return: None

    '''
    logger.debug(f'Get from Bot: {message.text}')
    # init variables 
    cmd = resolution = yt_id = chat_id = msg_id = uid = msg_to_delete = None

    # split message data from Bot
    # with message to delete when len = 7
    message_from_bot = message.text.split(' ')
    if len(message_from_bot) == 7:
        cmd, resolution, yt_id, chat_id, msg_id, uid, msg_to_delete = message_from_bot
    elif len(message_from_bot) == 6:
        cmd, resolution, yt_id, chat_id, msg_id, uid = message_from_bot

    # get yt_title for filename
    yt_obj = YouTube(f'https://youtu.be/{yt_id}')
    yt_title = yt_obj.title.translate(str.maketrans(' ', '_', punctuation))

    # create message data to send to Bot with audiofile
    if msg_to_delete is not None:
        message_to_bot = f'{resolution} {yt_id} {chat_id} {msg_id} {uid} {msg_to_delete}'
    else:
        message_to_bot = f'{resolution} {yt_id} {chat_id} {msg_id} {uid}'


    if resolution == 'mp3':
        # create path for downloading
        type_ = '.mp3'
        path = f'C:\\Bot\\Data\\{uid}\\{resolution}\\{yt_title}{type_}'
        
        # get audio mp3 object
        audio = yt_obj.streams.filter(only_audio=True).desc().first()

        # downloading starts here
        download_content(audio, uid, resolution, yt_title, type_)

        # send audio to Bot with message data
        await app.send_audio(chat_id=BOT_ID, audio=path, caption=message_to_bot, parse_mode=ParseMode.HTML,
                             title=f'{yt_title}{type_}')

    elif resolution == 'm4a':
        # create path for downloading
        type_ = '.m4a'
        path = f'C:\\Bot\\Data\\{uid}\\{resolution}\\{yt_title}{type_}'

        # get audio m4a object
        audio = yt_obj.streams.get_audio_only()

        # downloading starts here
        download_content(audio, uid, resolution, yt_title, type_)
        
        # send audio to Bot with message data
        await app.send_audio(chat_id=BOT_ID, audio=path, caption=message_to_bot, parse_mode=ParseMode.HTML,
                             title=f'{yt_title}{type_}')

    # delete audiofile from path
    try:
        delete_file(path)
    except (FileNotFoundError, PermissionError) as e:
        logger.exception(e)
    else:
        pass


def get_logger(logger_name: str) -> logging.Logger:
    """

    Get logger with all logging levels

    :param logger_name: same as python filename
    :return: Logger object
    """
    logger = logging.getLogger(logger_name)
    FORMAT = '%(levelname)s | %(name)s:%(lineno)s | %(message)s'
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    #logger_name = logger_name.replace('.py', '.log')
    #handler = logging.FileHandler(filename=f'C:\\Bot\\Logs\\{logger_name}')
    handler.setFormatter(logging.Formatter(FORMAT))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


def delete_file(path: str) -> None:
    '''
    Delete file from path

    Return: None
    '''
    logger.info(f'start delete_file: {path}')
    remove(path)
    logger.info(f'finish delete_file: {path}')


def userbot() -> None:
    '''
    Init UserBot with session name, API ID, API HASH
    '''
    app = Client(SESSION, api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

    # create handlers
    handler_video = MessageHandler(check_video, filters=filters.private & filters.regex('/v'))
    handler_audio = MessageHandler(check_audio, filters=filters.private & filters.regex('/a'))

    # add handlers
    app.add_handler(handler_video)
    app.add_handler(handler_audio)

    # start loop
    app.run()


if __name__ == '__main__':
    # start UserBot
    logger = get_logger('UserBot.py')
    userbot()