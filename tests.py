def delete_file(path):
    logger.info(f'start delete: {path}')
    remove(path)
    logger.info(f'finish delete: {path}')

doc_id = await db.get(table_name='youtube_files',
                      items=(f'doc_id_{down_type}',),
                      condition={'youtube_id': youtube_id})
if doc_id is None:
    text = messages.get("PLEASE WAIT").get(language).format(down_type)
    bot_message = await bot.send_message(
                            chat_id=chat_id, 
                            reply_to_message_id=main_message_id,
                            text=messages.get("PLEASE WAIT")\
                                 .get(language).format(down_type))                                     
    path, filename = await get_download_path(uid=uid, content=down_type,
                                             youtube_id=youtube_id)
    fullpath = f'{path}{filename}'
    try:
        #download starts here
        await download_content(uid=uid, youtube_id=youtube_id,
                               path=path, filename=filename)
    except IncompleteRead as e:
        logger.exception(e)
        await bot.send_message(
                  chat_id=chat_id, parse_mode="html",
                  reply_to_message_id=main_message_id,
                  text=messages.get('INCOMPLETE READ')\
                       .get(language).format(down_type))
        delete_file(fullpath)
    else:
        text = messages.get('DOWNLOADED WITH').get(language)\
                        .format(default.get('bot_username'))
        try:
            # bot try to send document
            match down_type:
                case 'video':
                    bot_video = await bot.send_video(
                                         chat_id=chat_id,
                                         caption=text, reply_to_message_id=main_message_id,
                                         reply_markup=kb.get_share_button(youtube_id, f'share_{down_type}'),
                                         parse_mode='html', video=open(fullpath, 'rb'))
                    doc_id_video = bot_video.video.file_id
                    ins_items = {'tg_id': uid,
                                 'youtube_id': youtube_id,
                                 'doc_id_video': doc_id_video,
                                 'doc_id_audio': None}
                    upd_items = {'doc_id_video': doc_id_video}

                case 'audio':
                    bot_audio = await bot.send_audio(
                                         chat_id=chat_id,
                                         caption=text, reply_to_message_id=main_message_id,
                                         reply_markup=kb.get_share_button(youtube_id, f'share_{down_type}'),
                                         parse_mode='html', audio=open(fullpath, 'rb'))
                    doc_id_audio = bot_audio.audio.file_id
                    ins_items = {'tg_id': uid,
                                 'youtube_id': youtube_id,
                                 'doc_id_video': None,
                                 'doc_id_audio': doc_id_audio}
                    upd_items = {'doc_id_audio': doc_id_audio}





        # when documents >50mb -> send command to userbot
        except NetworkError as e:
            logger.exception(e)
            command = '/v' if down_type == 'video' else '/a'
            text = f'{command} {bot_message.message_id} {main_message_id} {youtube_id} {uid} {fullpath}'
            await bot.send_message(text=text, chat_id=default.get('userbot_id'))
        else:
            # when document was sent      
            await bot.delete_message(chat_id=chat_id, message_id=bot_message.message_id)
            delete_file(fullpath)
            await db.insert_or_update(tablename='youtube_files',
                                      condition=('youtube_id',),
                                      ins_items=ins_items,
                                      upd_items=upd_items)
else:
    match down_type:
        case 'video':
            await bot.send_video(chat_id=chat_id, video=doc_id,
                                 parse_mode='html', caption=text,
                                 reply_to_message_id=main_message_id,
                                 reply_markup=kb.get_share_button(youtube_id, f'share_{down_type}'))
        case 'audio':
            await bot.send_audio(chat_id=chat_id, audio=doc_id,
                                 parse_mode='html', caption=text,
                                 reply_to_message_id=main_message_id,
                                 reply_markup=kb.get_share_button(youtube_id, f'share_{down_type}'))


match down_type:
        case 'video':
            video_id = await db.get(table_name='youtube_files',
                                    items=(f'doc_id_{down_type}',),
                                    condition={'youtube_id': youtube_id})

            if video_id is None:
                text = messages.get("PLEASE WAIT VIDEO").get(language)
                bot_message = await bot.send_message(chat_id=chat_id, text=text,
                                                     reply_to_message_id=main_message_id)
                path, filename = await get_download_path(uid=uid, youtube_id=youtube_id, content=down_type)
                fullpath = f'{path}{filename}'
                try:
                    # download starts here
                    await download_content(uid=uid, youtube_id=youtube_id,
                                           path=path, filename=filename)


                except IncompleteRead as e:
                    logger.exception(e)
                    await bot.send_message(chat_id=chat_id, parse_mode="html",
                                           reply_to_message_id=main_message_id,
                                           text=messages.get('VIDEO INCOMPLETE READ').get(language))                
                    logger.info(f'start delete: {fullpath}')
                    remove(fullpath)
                    logger.info(f'finish delete: {fullpath}')

                else:
                    text = messages.get('DOWNLOADED WITH').get(language)\
                                        .format(default.get('bot_username'))
                    try:
                        # bot try to send document
                        bot_video = await bot.send_video(chat_id=chat_id, video=open(fullpath, 'rb'),
                                                         caption=text, reply_to_message_id=main_message_id,
                                                         parse_mode='html',
                                                         reply_markup=kb.get_share_button(youtube_id,
                                                                                         'share_video'))
                    # when documents >50mb -> send command to userbot
                    except NetworkError as e:
                        logger.exception(e)
                        text = f'/v {bot_message.message_id} {main_message_id} {youtube_id} {uid} {fullpath}'
                        await bot.send_message(chat_id=default.get('userbot_id'), text=text)
                    else:
                        # when document was sent
                        await bot.delete_message(chat_id=chat_id, message_id=bot_message.message_id)

                        logger.info(f'start delete: {fullpath}')
                        remove(fullpath)
                        logger.info(f'finish delete: {fullpath}')

                        await db.insert_or_update(tablename='youtube_files',
                                                  ins_items={'tg_id': uid,
                                                            'youtube_id': youtube_id,
                                                            'doc_id_video': bot_video.video.file_id,
                                                            'doc_id_audio': None},
                                                  upd_items={'doc_id_video': bot_video.video.file_id},
                                                  condition=('youtube_id',))
            else:
                await bot.send_video(chat_id=chat_id, video=video_id,
                                     parse_mode='html', caption=text,
                                     reply_to_message_id=main_message_id,
                                     reply_markup=kb.get_share_button(youtube_id, 'share_video'))

        case 'audio':
            audio_id = await db.get(table_name='youtube_files',
                                    items=('doc_id_audio',),
                                    condition={'youtube_id': youtube_id})
            if audio_id is None:
                text = messages.get("PLEASE WAIT AUDIO").get(language)
                bot_message = await bot.send_message(chat_id=chat_id, text=text,
                                                     reply_to_message_id=main_message_id)
                path, filename = await get_download_path(uid=uid, youtube_id=youtube_id, content=down_type)
                fullpath = f'{path}{filename}'
                try:
                    # download starts here
                    await download_content(uid=uid, youtube_id=youtube_id,
                                           path=path, filename=filename)


                except IncompleteRead as e:
                    logger.exception(e)
                    await bot.send_message(chat_id=chat_id, parse_mode="html",
                                           reply_to_message_id=main_message_id,
                                           text=messages.get('AUDIO INCOMPLETE READ').get(language))                
                    logger.info(f'start delete: {fullpath}')
                    remove(fullpath)
                    logger.info(f'finish delete: {fullpath}')

                else:
                    text = messages.get('DOWNLOADED WITH').get(language)\
                                        .format(default.get('bot_username'))
                    try:
                        # bot try to send document
                        bot_audio = await bot.send_audio(chat_id=chat_id, audio=open(fullpath, 'rb'),
                                                         caption=text, reply_to_message_id=main_message_id,
                                                         parse_mode='html',
                                                         reply_markup=kb.get_share_button(youtube_id,
                                                                                         'share_audio'))
                    # when documents >50mb -> send command to userbot
                    except NetworkError as e:
                        logger.exception(e)
                        text = f'/a {bot_message.message_id} {main_message_id} {youtube_id} {uid} {fullpath}'
                        await bot.send_message(chat_id=default.get('userbot_id'), text=text)
                    else:
                        # when document was sent
                        await bot.delete_message(chat_id=chat_id, message_id=bot_message.message_id)

                        logger.info(f'start delete: {fullpath}')
                        remove(fullpath)
                        logger.info(f'finish delete: {fullpath}')
                        await db.insert_or_update(ins_items={'tg_id': uid, 'youtube_id': youtube_id,
                                                             'doc_id_video': None,
                                                             'doc_id_audio': bot_audio.audio.file_id},
                                                  upd_items={'doc_id_audio': bot_audio.audio.file_id},
                                                  condition=('youtube_id',), tablename='youtube_files')
                        
            else:
                await bot.send_audio(chat_id=chat_id, audio=audio_id,
                                     parse_mode='html', caption=text,
                                     reply_to_message_id=main_message_id,
                                     reply_markup=kb.get_share_button(youtube_id, 'share_audio'))
