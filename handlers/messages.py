from aiogram import types
from aiogram.types.input_file import InputFile
from aiogram.types.input_media import InputMediaVideo, InputMediaPhoto
from aiogram.utils.exceptions import BotBlocked
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher.filters.builtin import ChatTypeFilter
from tools.logger import get_logger
from tools.database import db
from tools.bot import bot, is_url
from tools.getup import messages, default
from tools.youtube_tools import is_youtube_url, get_yid
from tools.tiktok_tools import TiktokDownloader
from keyboards.inline import Keyboard
from pytube import YouTube
from io import BytesIO
import requests

async def is_member(uid: int) -> bool:
    '''
    Check user subscription

    Get: 
        uid: telegram user id

    return: bool

    '''
    logger.debug(f'Function is_member Get: uid={uid}')
    member_info = await bot.get_chat_member(chat_id=default.get('channel_id'),
                                            user_id=uid)
    print(member_info)
    if member_info.status == 'left':
        logger.debug(f"function is_member return False: {member_info.status}")
        return False
    else:
        logger.debug(f"function is_member return True: {member_info.status}")
        return True


async def is_tiktok_url(url: str) -> bool:
    '''
    Check if link is TikTok.

    Get: 
        url: TikTok video url

    return: bool

    '''
    logger.debug(f'Function is_tiktok_url Get: url={url}')
    if 'tiktok.com' in url:
        logger.debug(f"function is_tiktok_url return True: {url}")
        return True
    else:
        logger.debug(f"function is_tiktok_url return False: {url}")
        return False


async def get_tt_video_id(url: str) -> int:
    '''
    Get TikTok video id from mobile or pc links.

    Get: 
        url: TikTok video url

    return: 
        TikTok video unique id

    '''
    logger.debug(f'Function get_tt_video_id Get: url={url}')
    # if link from mobile app
    if 'vm.tiktok.com' in url:
        splited_url = url.split('/')
        index = splited_url.index('vm.tiktok.com')
        tt_video_id = splited_url[index+1]
        logger.debug(f"function get_tt_video_id return: {tt_video_id}")
        return tt_video_id
    else:
        # if link from web
        for i in url.split('/'):
            if i == '':
                continue
            if i[0].isdigit():
                id_side = i.split('?')
                tt_video_id = id_side[0]
                logger.debug(f"function get_tt_video_id return: {tt_video_id}")
                return tt_video_id


async def get_tiktok_url(tiktok_id: str) -> str:
    '''
    Connect TikTok link pattern with tiktok id

    Get: 
        tiktok_id: TikTok video unique id

    return: 
        Mobile app or web tiktok link

    '''
    logger.debug(f'Function get_tiktok_url Get: tiktok_id={tiktok_id}')
    if len(tiktok_id) == 9:
        url = f'https://vm.tiktok.com/{tiktok_id}'
    else:
        url = f'https://www.tiktok.com/video/{tiktok_id}'
    return url


async def take_from_userbot(message: types.Message):
    '''
    Take more than 50mb video/audio downloaded from UserBot.
    Save video/audio id and send it to user

    Get: 
        message: types.Message

        Metadata in message:
            resolution: resolution of video or mp3/m4a
            yt_id: YouTube video unique id
            chat_id: Telegram chat id
            msg_id: main message id user sended with YouTube ink
            uid: Telegram user id
            msg_to_delete: messsage from bot needed to delete

    return: None

    '''
    logger.debug(f'Function take_from_userbot: Get message from UserBot: {message.caption}')

    resolution = yt_id = chat_id = msg_id = uid = msg_to_delete = None
    message_from_userbot = message.caption.split(' ')

    if len(message_from_userbot) == 6:
        resolution, yt_id, chat_id, msg_id, uid, msg_to_delete = message_from_userbot
    elif len(message_from_userbot) == 5:
        resolution, yt_id, chat_id, msg_id, uid = message_from_userbot
    

    language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})
    caption = messages.get('DOWNLOADED WITH').get(language)\
                            .format(default.get('bot_username'))


    text = messages.get('DOWNLOADED WITH').get(language)\
                        .format(default.get('bot_username'))

    type_ = '.mp4' if resolution in ('720p', '360p', '144p') else '.mp3'
    if type_ == '.mp4':
        doc_id_video = message.video.file_id

        if resolution == '720p':
            ins_items = {'tg_id': uid,
                         'youtube_id': yt_id,
                         'doc_id_720p': doc_id_video,
                         'doc_id_360p': None,
                         'doc_id_144p': None,
                         'doc_id_mp3': None,
                         'doc_id_m4a': None,}
            upd_items = {'doc_id_720p': doc_id_video} 

        elif resolution == '360p':
            ins_items = {'tg_id': uid,
                         'youtube_id': yt_id,
                         'doc_id_720p': None,
                         'doc_id_360p': doc_id_video,
                         'doc_id_144p': None,
                         'doc_id_mp3': None,
                         'doc_id_m4a': None,}
            upd_items = {'doc_id_360p': doc_id_video}

        elif resolution == '144p':
            ins_items = {'tg_id': uid,
                         'youtube_id': yt_id,
                         'doc_id_720p': None,
                         'doc_id_360p': None,
                         'doc_id_144p': doc_id_video,
                         'doc_id_mp3': None,
                         'doc_id_m4a': None,}
            upd_items = {'doc_id_144p': doc_id_video}

    elif type_ == '.mp3':
        doc_id_audio = message.audio.file_id
        ins_items = {'tg_id': uid,
                     'youtube_id': yt_id,
                     'doc_id_720p': None,
                     'doc_id_360p': None,
                     'doc_id_144p': None,
                     'doc_id_mp3': doc_id_audio,
                     'doc_id_m4a': None,}
        upd_items = {'doc_id_mp3': doc_id_audio}

    elif type_ == '.m4a':
        doc_id_audio = message.video.file_id
        ins_items = {'tg_id': uid,
                     'youtube_id': yt_id,
                     'doc_id_720p': None,
                     'doc_id_360p': None,
                     'doc_id_144p': None,
                     'doc_id_mp3': None,
                     'doc_id_m4a': doc_id_audio,}
        upd_items = {'doc_id_m4a': doc_id_audio}

    
    if resolution in ('720p', '360p', '144p'):
        yt_obj = YouTube(f'https://youtu.be/{yt_id}')
        video = yt_obj.streams.filter(res=resolution).first()
        thumb = yt_obj.thumbnail_url

        await bot.send_video(chat_id=chat_id, thumb=InputFile(BytesIO(requests.get(thumb).content)),
                             caption=text, reply_to_message_id=msg_id, parse_mode='html', video=doc_id_video,
                             reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                 chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                 callback_data=None))

        if msg_to_delete is not None:
            await bot.delete_message(chat_id=chat_id, message_id=msg_to_delete)

        # here can be Ad message


    elif resolution == 'mp3':
        await bot.send_audio(chat_id=chat_id, audio=message.audio.file_id, parse_mode='html', caption=text, reply_to_message_id=msg_id,
                             reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                 chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                 callback_data=None))
        # here can be Ad message

    elif resolution == 'm4a':

        await bot.send_audio(chat_id=chat_id, audio=message.audio.file_id, parse_mode='html', caption=text, reply_to_message_id=msg_id,
                             reply_markup=kb.get_yt_share_button(yt_id, f'share yt{resolution}', keyboard=True,
                                                                 chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                 callback_data=None))
        # here can be Ad message

    await db.insert_or_update(tablename='youtube_files',
                                  condition=('youtube_id',),
                                  ins_items=ins_items,
                                  upd_items=upd_items)


async def message(message: types.Message):
    '''
    Handler to work with all messages
    content_types=['text']

    '''
    logger.debug(f'Function message Get: message={message}')

    # get info about user: chat_id, user id, language
    chat_id = message.chat.id
    uid = message.from_user.id
    logger.debug(f'user {uid} write message {message.text}')
    language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})

    # check url in message
    if await is_url(message):
        # if user send any link
        
        # check user subscription
        if await is_member(uid):
            # user is subscribed


            # check url is Tiktok
            if await is_tiktok_url(message.text):
                # it's Tiktok url, choose downloading type

                # get TikTok video id from link
                tiktok_id = await get_tt_video_id(message.text)

                # try to find this TikTok video id in TikTok database 
                video_id = await db.get(table_name='tiktok_files',
                                        items=('doc_id_video',),
                                        condition={'tiktok_id': tiktok_id})

                # get 'DOWNLOADED WITH' message
                text = messages.get('DOWNLOADED WITH').get(language)\
                                    .format(default.get('bot_username'))

                # if tiktok video id not in database
                if video_id is None:

                    # get full link of tiktok
                    url = await get_tiktok_url(tiktok_id)

                    # TikTok downloading starts here
                    try:
                        content = await tt.musicaldown(url, 'video')
                    except ConnectionError:
                        pass

                    # send video to user and save it in bot_video variable
                    # now we can get telegram video Id from it
                    bot_video = await message.answer_video(
                                              video=content, reply=True,
                                              parse_mode='html', caption=text,
                                              reply_markup=kb.get_tt_download_kb(tiktok_id=tiktok_id,
                                                                                 message_id=message.message_id,
                                                                                 type_='share_video'))
                    # add video Id to TikTok files database
                    await db.insert_or_update_video(uid, tiktok_id, bot_video.video.file_id)
      
                else:
                    # if tiktok video id is in database
                    # just take video Id from database and send video to user
                    await message.answer_video(
                                         video=video_id, reply=True,
                                         parse_mode='html', caption=text,
                                         reply_markup=kb.get_tt_download_kb(tiktok_id=tiktok_id,
                                                                            message_id=message.message_id,
                                                                            type_='share_video'))
  
            # check url is YouTube
            else:
                yt_object = await is_youtube_url(message)
                if yt_object is not None:
                    yt_id = yt_object.video_id

                    await message.answer(text=messages.get('DOWNLOAD NOW').get(language), reply=True,
                                         reply_markup=kb.get_yt_download_kb(yt_id=yt_id, msg_id=message.message_id,
                                                                            yt_object=yt_object, chat_id=chat_id, uid=uid))

                else:
                    # incorrect links
                    await message.answer(text=messages.get('INCORRECT TIKTOK URL').get(language))
            

        else:
            # user is not subscribed
            # bot send 'PLEASE SUBSCRIBE' message with subscribe button
            await message.reply(text=messages.get('PLEASE SUBSCRIBE').get(language),
                                parse_mode='html',
                                reply_markup=kb.get_subscribe_button())


def message_handlers(dp: Dispatcher):
    """
    Register all message handlers.
    """
    logger.info('Register message handlers.')
    dp.register_message_handler(take_from_userbot,
                                lambda message: message.from_user.id == default.get('userbot_id'),
                                content_types=['audio', 'video', 'document'])
    dp.register_message_handler(message, content_types=['text'])

logger = get_logger('handlers.messages.py')
kb = Keyboard()
tt = TiktokDownloader()