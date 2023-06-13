from psycopg2.errors import UniqueViolation
import requests
from requests.exceptions import ConnectionError
from aiogram import types
from aiogram.types.input_file import InputFile
from aiogram.types.input_media import InputMedia, InputMediaAudio
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import (BotBlocked, InvalidQueryID,
                                      NetworkError, MessageNotModified)
from keyboards.inline import Keyboard
from tools.tiktok_tools import TiktokDownloader
from tools.youtube_tools import download_content, get_download_path
from tools.getup import messages, default
from tools.logger import get_logger
from tools.database import db
from tools.bot import bot
from io import BytesIO
from os import remove
import os.path
from http.client import IncompleteRead
from urllib.error import HTTPError
from pytube import YouTube
from string import punctuation

async def get_tiktok_url(tiktok_id):
    '''
    Get: 
        tiktok_id - tiktok video unique id
    Return
        url - full format url with video id
    '''
    logger.debug(f'Function get_tiktok_url Get: tiktok_id={tiktok_id}')
    if len(tiktok_id) == 9:
        url = f'https://vm.tiktok.com/{tiktok_id}'
    else:
        url = f'https://www.tiktok.com/video/{tiktok_id}'
    logger.debug(f'Function get_tiktok_url return url={url}')    
    return url


def get_youtube_url(youtube_id):
    '''
    Get: 
        youtube_id - tiktok video unique id
    Return
        full format url with video id
    '''
    logger.debug(f'Function get_youtube_url Get: youtube_id={youtube_id}')
    logger.debug(f'Function get_youtube_url return: https://youtu.be/{youtube_id}')
    return f'https://youtu.be/{youtube_id}'


def delete_file(path):
    '''
    Get:
        path - path to file
    '''
    logger.debug(f'Function delete_file Get: path={path}')
    logger.info(f'start delete: {path}')
    remove(path)
    logger.info(f'finish delete: {path}')


async def language(callback: types.CallbackQuery):
    '''
    Save user language after he pressed to language button
    '''

    # get info about user: chat_id, user id, language
    chat_id = callback.message.chat.id
    uid = callback.from_user.id
    logger.debug(f'Get language callback from user {uid}: {callback}')

    # split callbackdata and get language
    # example lang_EN -> EN
    language = callback.data.split('_')[1]

    try:
        await callback.answer()
    except InvalidQueryID as e:
        logger.exception(e)
    else:
        pass

    # save language to user 
    await db.update(table_name='users',
                    items={'language': language},
                    condition={'tg_id': uid})
    try:
        # inform user if language selected
        await bot.edit_message_text(chat_id=chat_id,
                                    message_id=callback.message.message_id,
                                    text=messages.get('LANGUAGE SELECTED').get(language))
    except MessageNotModified:
        pass

    # sending welcome message
    await bot.send_message(chat_id=chat_id,
                           text=messages.get('WELCOME').get(language).format(callback.from_user.first_name),
                           reply_markup=kb.get_add_to_chat_button(),
                           parse_mode='html')
    await callback.answer()


async def tt_download(callback: types.CallbackQuery):
    # get info about user: chat_id, user id, language
    chat_id = callback.message.chat.id
    uid = callback.from_user.id
    logger.debug(f'Get tiktok_download callback from user {uid}: {callback}')
    language = await db.get(table_name='users',
                                items=('language',),
                                condition={'tg_id': uid})

    #split callback data to variables
    down_type, tiktok_id, main_message_id = callback.data.split('_')[1:]

    # full format url
    url = await get_tiktok_url(tiktok_id)

    
    text = messages.get('DOWNLOADED WITH').get(language)\
                        .format(default.get('bot_username'))

    match down_type:
        case 'video':
            # try to find video on database
            video_id = await db.get(table_name='tiktok_files',
                                    items=('doc_id_video',),
                                    condition={'tiktok_id': tiktok_id})

            if video_id is None:

                # take video by bytes
                try:
                    content = await tt.musicaldown(url, 'video')
                except ConnectionError:
                    pass

                # send video to user and save it to database
                bot_video = await bot.send_video(
                                 chat_id=chat_id, video=content,
                                 parse_mode='html', caption=text,
                                 reply_to_message_id=main_message_id,
                                 reply_markup=kb.get_tt_download_kb(tiktok_id=tiktok_id,
                                                                    message_id=main_message_id,
                                                                    type_=f'share_{down_type}'))
                await db.insert_or_update_video(uid, tiktok_id, bot_video.video.file_id)
  
            else:
                await bot.send_video(chat_id=chat_id, video=video_id,
                                     parse_mode='html', caption=text,
                                     reply_to_message_id=main_message_id,
                                     reply_markup=kb.get_tt_download_kb(tiktok_id=tiktok_id,
                                                                    message_id=main_message_id,
                                                                    type_=f'share_{down_type}'))

        case 'audio':
            # try to find video on database
            audio_id = await db.get(table_name='tiktok_files',
                                    items=('doc_id_audio',),
                                    condition={'tiktok_id': tiktok_id})

            if audio_id is None:

                # take video by bytes
                try:
                    content = await tt.musicaldown(url, 'audio')
                except ConnectionError:
                    pass

                # send video converting to mp3
                bot_audio = await bot.send_audio(
                                 chat_id=chat_id, audio=content, title='audio.mp3',
                                 parse_mode='html', caption=text,
                                 reply_to_message_id=main_message_id,
                                 reply_markup=kb.get_tt_download_kb(tiktok_id=tiktok_id,
                                                                    message_id=main_message_id,
                                                                    type_=f'share_{down_type}'))
                await db.insert_or_update_audio(uid, tiktok_id, bot_audio.audio.file_id)

            else:
                await bot.send_audio(chat_id=chat_id, audio=audio_id,
                                     parse_mode='html', caption=text,
                                     reply_to_message_id=main_message_id,
                                     reply_markup=kb.get_tt_download_kb(tiktok_id=tiktok_id,
                                                                    message_id=main_message_id,
                                                                    type_=f'share_{down_type}'))            
    await callback.answer()



# not used
async def mp3_m4a_swapper(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    uid = callback.from_user.id
    logger.debug(f'Get yt_video_menu callback from user {uid}: {callback}')
    _, resolution, yt_id, chat_id, msg_id = callback.data.split(' ')

    language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})
    query_item = 'm4a' if resolution == 'mp3' else 'mp3'
    doc_id = await db.get(table_name='youtube_files',
                          items=(f'doc_id_{query_item}',),
                          condition={'youtube_id': yt_id})
    text = messages.get('DOWNLOADED WITH').get(language).format(default.get('bot_username'))

    m4a = True if resolution == 'mp3' else False
    if doc_id is None:
        
        #doc_id = await bot.send_audio()
        yt_obj = YouTube(f'https://youtu.be/{yt_id}')
        audio = yt_obj.streams.get_audio_only()
        

        await callback.message.edit_media(media=InputMediaAudio(audio.url, caption=text),
                                          reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                              chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=m4a))
        
    else:
        
        await callback.message.edit_media(media=InputMediaAudio(doc_id, caption=text),
                                          reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                              chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=m4a))



async def yt_video_menu(callback: types.CallbackQuery):
    '''
    Send keyboard to choose video quality

    '''
    # get info about user: chat_id, user id, language
    chat_id = callback.message.chat.id
    uid = callback.from_user.id
    logger.debug(f'Get yt_video_menu callback from user {uid}: {callback}')
    language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})
    # split callback data to variables 
    # _ is empty, not used
    _, _, yt_id, msg_id = callback.data.split(' ')[:]

    yt_object = YouTube(f'https://youtu.be/{yt_id}')

    # sending keyboard by editing main message
    await callback.message.edit_text(text=messages.get('VIDEO QUALITY').get(language),
                                     reply_markup=kb.get_youtube_keyboard(chat_id=callback.message.chat.id,
                                                     yt_object=yt_object, yt_id=yt_id,
                                                     uid=uid, msg_id=msg_id))
    try:
        await callback.answer()
    except InvalidQueryID as e:
        logger.exception(e)
    else:
        pass

# not used
async def yt_audio_mp3(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    uid = callback.from_user.id
    logger.debug(f'Get yt_audio_mp3 callback from user {uid}: {callback}')
    _, _, yt_id, msg_id = callback.data.split(' ')[:]
    language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})
    yt_obj = YouTube(f'https://youtu.be/{yt_id}')






async def userbot_sender(callback: types.CallbackQuery):

    # get info about user: chat_id, user id, language
    chat_id = callback.message.chat.id
    uid = callback.from_user.id
    logger.debug(f'Get userbot_sender callback from user {uid}: {callback}')
    language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})

    # split callback data to variables
    _, resolution, yt_id, chat_id, msg_id = callback.data.split(' ')[:]

    
    # try to find file in database
    doc_id = await db.get(table_name='youtube_files',
                            items=(f'doc_id_{resolution}',),
                            condition={'youtube_id': yt_id})

    text = messages.get('DOWNLOADED WITH').get(language).format(default.get('bot_username'))
    if doc_id is None:
        

        yt_obj = YouTube(f'https://youtu.be/{yt_id}')
        # get youtube video name. replace all wronk symbols and spaces to _
        yt_title = yt_obj.title.translate(str.maketrans(' ', '_', punctuation))

        type_ = ''

        # create message to userbot
        if resolution in ('720p', '360p', '144p'):
            text = messages.get('PLEASE WAIT VIDEO').get(language)
            type_ = '.mp4'
            message_to_userbot = f'/v {resolution} {yt_id} {chat_id} {msg_id} {uid}'
        elif resolution == 'mp3':
            text = messages.get('PLEASE WAIT AUDIO').get(language)
            type_ = '.mp3'
            message_to_userbot = f'/a {resolution} {yt_id} {chat_id} {msg_id} {uid}'
        elif resolution == 'm4a':
            text = messages.get('PLEASE WAIT AUDIO').get(language)
            type_ = '.m4a'
            message_to_userbot = f'/a {resolution} {yt_id} {chat_id} {msg_id} {uid}'

        path = f'C:\\Bot\\Data\\{uid}\\{resolution}\\{yt_title}{type_}'

        if not os.path.isfile(path):

            #video more than 50mb. Send: command to UserBot to start downloading.
            if callback.message.text is not None:
                
                message_to_delete = callback.message.message_id
                message_to_userbot += f' {message_to_delete}'
                
                logger.debug(f'Send to UserBot: {message_to_userbot}')
                await bot.send_message(chat_id=default.get('userbot_id'), text=message_to_userbot)
                await callback.message.edit_text(text=text)
            else:
                print('point2')

                await bot.send_message(chat_id=default.get('userbot_id'), text=message_to_userbot)
                await bot.send_message(chat_id=chat_id, reply_to_message_id=msg_id,
                                       text=messages.get('PLEASE WAIT AUDIO').get(language))
        else:
            await bot.edit_message_text(message_id=callback.message.message_id,
                                        text=messages.get('ALREADY DOWNLOADING VIDEO').get(language),
                                        chat_id=chat_id)
    else:
        text = messages.get('DOWNLOADED WITH').get(language).format(default.get('bot_username'))
        if resolution in ('720p', '360p', '144p'):
            await bot.send_video(chat_id=chat_id, caption=text, reply_to_message_id=msg_id, parse_mode='html', video=doc_id,
                                 reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                     chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                     callback_data=None))
            # here can be Ad message

        elif resolution == 'mp3':
            await bot.send_audio(chat_id=chat_id, audio=doc_id, parse_mode='html', caption=text, reply_to_message_id=msg_id,
                                 reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                     chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                     callback_data=None))
            # here can be Ad message
            

        elif resolution == 'm4a':
            await bot.send_audio(chat_id=chat_id, audio=doc_id, parse_mode='html', caption=text, reply_to_message_id=msg_id,
                                 reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                     chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                     callback_data=None))
            # here can be Ad message

        if callback.message.video is None:
                await callback.message.delete()


async def bot_sender(callback: types.CallbackQuery):
    '''
    Callback handler to save, send and download files < 50 mb
    '''
    logger.debug(f'Get language callback from user {callback.from_user.id}: {callback}')

    # get info about user: chat_id, user id, language
    uid = callback.from_user.id
    language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})

    # split callback data to variables
    _, resolution, yt_id, chat_id, msg_id = callback.data.split(' ')[:]

    # try to findd 
    doc_id = await db.get(table_name='youtube_files',
                          items=(f'doc_id_{resolution}',),
                          condition={'youtube_id': yt_id})
    try:
        await callback.answer()
    except InvalidQueryID as e:
        logger.exception(e)
    else:
        pass
      
    text = messages.get('DOWNLOADED WITH').get(language).format(default.get('bot_username'))

    if doc_id is None:

        yt_obj = YouTube(f'https://youtu.be/{yt_id}')
        # get youtube video name. replace all wronk symbols and spaces to _
        yt_title = yt_obj.title.translate(str.maketrans(' ', '_', punctuation))

        type_ = ''
        if resolution in ('720p', '360p', '144p'):
            type_ = '.mp4'
        elif resolution == 'mp3':
            type_ = '.mp3'
        elif resolution == 'm4a':
            type_ = '.m4a'

        # create full path to file
        path = f'C:\\Bot\\Data\\{uid}\\{resolution}\\{yt_title}{type_}'

        if not os.path.isfile(path):
            
            if type_ == '.mp4':
                bot_msg = await callback.message.edit_text(text=messages.get('PLEASE WAIT VIDEO').get(language))
                # get video object by resolution 720p or 360p or 144p
                video = yt_obj.streams.filter(res=resolution).first()
                thumb = yt_obj.thumbnail_url
                video.download(output_path=f'C:\\Bot\\Data\\{uid}\\{resolution}\\', filename=f'{yt_title}{type_}')

                # send video with thubmnail image
                bot_document = await bot.send_video(chat_id=chat_id, thumb=InputFile(BytesIO(requests.get(thumb).content)),
                                                    caption=text, reply_to_message_id=msg_id, parse_mode='html', video=open(path, 'rb'),
                                                    reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                                        chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                                        callback_data=None))
                await callback.message.delete() 

                # here can be Ad message

            elif type_ == '.mp3':
                bot_msg = None
                if callback.message.text is not None:
                    bot_msg = await callback.message.edit_text(text=messages.get('PLEASE WAIT AUDIO').get(language))

                # get audio mp3 object
                audio = yt_obj.streams.filter(only_audio=True).desc().first()
                audio.download(output_path=f'C:\\Bot\\Data\\{uid}\\{resolution}\\', filename=f'{yt_title}{type_}')
                
                # send audio 
                bot_document = await bot.send_audio(chat_id=chat_id, caption=text, reply_to_message_id=msg_id, title=f'{yt_title}{type_}',
                                                    reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True, 
                                                                                        chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                                        callback_data=None),
                                                    parse_mode='html', audio=open(path, 'rb'))
                if bot_msg:
                    await bot.delete_message(chat_id=chat_id, message_id=bot_msg.message_id)

                # here can be Ad mesage


            # not worked 
            elif type_ == '.m4a':

                bot_msg = await callback.message.edit_text(text=messages.get('PLEASE WAIT AUDIO').get(language))
                audio = yt_obj.streams.get_audio_only()
                audio.download(output_path=f'C:\\Bot\\Data\\{uid}\\{resolution}\\', filename=f'{yt_title}{type_}')
                
                bot_document = await bot.send_audio(chat_id=chat_id, caption=text, reply_to_message_id=msg_id, title=f'{yt_title}{type_}',
                                                    reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True),
                                                    parse_mode='html', audio=audio.url)

                # here can be Ad mesage

            
            # create queries will be used for database saving
            if type_ == '.mp4':
                doc_id_video = bot_document.video.file_id

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
                doc_id_audio = bot_document.audio.file_id
                ins_items = {'tg_id': uid,
                             'youtube_id': yt_id,
                             'doc_id_720p': None,
                             'doc_id_360p': None,
                             'doc_id_144p': None,
                             'doc_id_mp3': doc_id_audio,
                             'doc_id_m4a': None,}
                upd_items = {'doc_id_mp3': doc_id_audio}

            elif type_ == '.m4a':
                doc_id_audio = bot_document.audio.file_id
                ins_items = {'tg_id': uid,
                             'youtube_id': yt_id,
                             'doc_id_720p': None,
                             'doc_id_360p': None,
                             'doc_id_144p': None,
                             'doc_id_mp3': None,
                             'doc_id_m4a': doc_id_audio,}
                upd_items = {'doc_id_m4a': doc_id_audio}

            await db.insert_or_update(tablename='youtube_files',
                                      condition=('youtube_id',),
                                      ins_items=ins_items,
                                      upd_items=upd_items)
            remove(path)
        else:
            await bot.edit_message_text(message_id=callback.message.message_id,
                                        text=messages.get('ALREADY DOWNLOADING VIDEO').get(language),
                                        chat_id=chat_id)
    else:
        if resolution in ('720p', '360p', '144p'):
            logger.debug(f'''Bot send audio m4a: chat_id={chat_id}, video={doc_id}, caption={text}, reply_to_message_id={msg_id}\
                            yt_id={yt_id}, callback_data=None, keyboard=True, uid={uid}, msg_id={msg_id}, m4a=False, share=share yt {resolution}''')

            await bot.send_video(chat_id=chat_id, parse_mode='html', video=doc_id,
                                 caption=text, reply_to_message_id=msg_id,
                                 reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                    chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                    callback_data=None))
            await callback.message.delete()

            # here can be Ad mesage
            
        elif resolution == 'mp3':

            logger.debug(f'''Bot send audio mp3: chat_id={chat_id}, audio={doc_id}, caption={text}, reply_to_message_id={msg_id}\
                            yt_id={yt_id}, callback_data=None, keyboard=True, uid={uid}, msg_id={msg_id}, m4a=False''')

            await bot.send_audio(chat_id=chat_id, audio=doc_id, parse_mode='html', caption=text, reply_to_message_id=msg_id,
                                 reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                     chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False,
                                                                     callback_data=None))
            if callback.message.video is None:
                await callback.message.delete()

            # here can be Ad mesage

        elif resolution == 'm4a':
            logger.debug(f'''Bot send audio m4a: chat_id={chat_id}, audio={doc_id}, caption={text}, reply_to_message_id={msg_id}\
                            yt_id={yt_id}, callback_data=None, keyboard=True, uid={uid}, msg_id={msg_id}, m4a=False, share=share yt {resolution}''')

            await bot.send_audio(chat_id=chat_id, audio=doc_id, parse_mode='html', caption=text, reply_to_message_id=msg_id,
                                 reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=True,
                                                                     chat_id=chat_id, uid=uid, msg_id=msg_id, m4a=False))

            # here can be Ad mesage
        
  
def callback_handlers(dp: Dispatcher):
    """
    Register all callback handlers.
    """
    logger.info('Register callback handlers.')
    dp.register_callback_query_handler(language, lambda callback: callback.data.startswith('lang'))
    dp.register_callback_query_handler(tt_download, lambda callback: callback.data.startswith('tt'))
    dp.register_callback_query_handler(yt_video_menu, lambda callback: callback.data.startswith('yt video'))
    dp.register_callback_query_handler(yt_audio_mp3, lambda callback: callback.data.startswith('yt mp3'))
    dp.register_callback_query_handler(mp3_m4a_swapper, lambda callback: callback.data.startswith('from'))
    dp.register_callback_query_handler(bot_sender, lambda callback: callback.data.startswith('bot'))
    dp.register_callback_query_handler(userbot_sender, lambda callback: callback.data.startswith('userbot'))


logger = get_logger('handlers.callbacks.py')
kb = Keyboard()
tt = TiktokDownloader()