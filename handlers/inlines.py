from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InputTextMessageContent, InlineQueryResultVideo
from tools.logger import get_logger
from tools.getup import default, messages
from tools.tiktok_tools import TiktokDownloader
from tools.database import db
from keyboards.inline import Keyboard

async def inline_handler(query: types.InlineQuery):
    '''
    Inline handler for sharing TikTok/YouTube audio/video files
    '''
    logger.debug(f'Get inline_handler from user: {query}')

    # init variables for TikTok sharing
    if query.query.startswith('share_audio') or query.query.startswith('share_video'):
        uid = query.from_user.id
        query_data = query.query
        type_, tiktok_id = query_data.split(' ')
        language = await db.get(table_name='users',
                            items=('language',),
                            condition={'tg_id': uid})
        text = messages.get('DOWNLOADED WITH').get(language)\
                            .format(default.get('bot_username'))


    # init variables for YouTube sharing
    elif query.query.startswith('share yt'):
        uid = query.from_user.id
        query_data = query.query

        # split query data 
        splitted = query_data.split(' ')

        type_ = 'share yt'
        resolution, yt_id = query_data.split(' ')[2:]
        language = await db.get(table_name='users',
                                items=('language',),
                                condition={'tg_id': uid})
        text = messages.get('DOWNLOADED WITH').get(language)\
                            .format(default.get('bot_username'))

    else:
        type_ = None

    
    match type_:
        # share TikTok video
        case 'share_video': 
            video_id = await db.get(table_name='tiktok_files',
                                    items=('doc_id_video',),
                                    condition={'tiktok_id': tiktok_id})
            articles = [types.InlineQueryResultCachedVideo(
                        id='1',
                        title=default.get('bot_name'),
                        description='Share video',
                        caption=text,
                        video_file_id=video_id,
                        reply_markup=kb.get_tt_share_button(tiktok_id, 'share_video', keyboard=True))]
            await query.answer(articles, cache_time=60, is_personal=True)

        # share TikTok audio
        case 'share_audio':
            audio_id = await db.get(table_name='tiktok_files',
                                    items=('doc_id_audio',),
                                    condition={'tiktok_id': tiktok_id})
            articles = [types.InlineQueryResultCachedAudio(
                        id='2',
                        caption=text,
                        audio_file_id=audio_id,
                        reply_markup=kb.get_tt_share_button(tiktok_id, 'share_audio', keyboard=True))]
            await query.answer(articles, cache_time=60, is_personal=True)
        case 'share yt':
            doc_id = await db.get(table_name='youtube_files',
                                  items={f'doc_id_{resolution}'},
                                  condition={'youtube_id': yt_id})
            
            if resolution in ('720p', '360p', '144p'):
                articles = [types.InlineQueryResultCachedVideo(
                        id='3',
                        title=default.get('bot_name'),
                        description='Share yt',
                        caption=text,
                        video_file_id=doc_id,
                        reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=False,
                                                            uid=uid, m4a=False, callback_data=None,
                                                            chat_id=None, msg_id=None))]

            else:
                articles = [types.InlineQueryResultCachedAudio(
                            id='4',
                            caption=text,
                            audio_file_id=doc_id,
                            reply_markup=kb.get_yt_share_button(yt_id, f'share yt {resolution}', keyboard=False,
                                                                chat_id=None, uid=None, msg_id=None, m4a=False,
                                                                callback_data=None))]
            await query.answer(articles, cache_time=60, is_personal=True)




        case None:
            pass





def inline_handlers(dp: Dispatcher):
    """
    Register all inline handlers.
    """
    dp.register_inline_handler(inline_handler)

logger = get_logger('handlers.inlines.py')
tt = TiktokDownloader()
kb = Keyboard()