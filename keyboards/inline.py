from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton as Button
from tools.getup import keyboards
from tools.logger import get_logger
from pytube import YouTube

logger = get_logger('keyboards.inline.py')

class Keyboard():
	def __init__(self):
		pass

	def get_faq_button(self):
		'''
		Return: Button for /help command
		'''
		logger.info('Method kb.get_faq_button called.')
		keyboard = InlineKeyboardMarkup(row_width=1)
		keyboard.add(Button(keyboards.get('FAQ BUTTON').get('NAME'),
							url=keyboards.get('FAQ BUTTON').get('URL')))
		logger.debug(f'method kb.faq_button: return keyboard={keyboard}')
		return keyboard


	def get_subscribe_button(self):
		'''
		Return: Button with channel to subscribe.
		'''
		logger.info('Method kb.get_subscribe_button called.')
		keyboard = InlineKeyboardMarkup(row_width=1)
		keyboard.add(Button(keyboards.get('SUBSCRIBE BUTTON').get('NAME'),
							url=keyboards.get('SUBSCRIBE BUTTON').get('URL')))
		logger.debug(f'method kb.get_subscribe_button: return keyboard={keyboard}')
		return keyboard

	def get_add_to_chat_button(self):
		'''
		Return: Button for adding bot to groups/supergroups.
		'''
		logger.info('Method kb.get_add_to_chat_button called.')
		keyboard = InlineKeyboardMarkup(row_width=1)
		keyboard.add(Button(keyboards.get('ADD BOT TO CHAT').get('NAME'),
							url=keyboards.get('ADD BOT TO CHAT').get('URL')))
		logger.debug(f'method kb.get_add_to_chat_button: return keyboard={keyboard}')
		return keyboard

	def get_language_keyboard(self):
		'''
		Return: Language keyboard for /lang command.
		'''
		logger.info('Method kb.get_language_keyboard called.')
		keyboard = InlineKeyboardMarkup(row_width=1)
		
		for button_data in keyboards.get('LANGUAGE KEYBOARD').values():
			keyboard.add(Button(button_data.get('NAME'),
								callback_data=button_data.get('CALLBACK DATA')))
		logger.debug(f'method kb.get_language_keyboard: return keyboard={keyboard}')
		return keyboard


	def get_tt_download_kb(self, tiktok_id, message_id, type_=None):
		'''
		Get:
			tiktok_id: tiktok video unique id.
			message_id: main message user sended with tiktok link
			type_: pointer -> 'share_video' or 'share_audio' or None
		Return: Downloading Keyboard or Share Button if type_=None
		'''
		logger.debug(f'Method kb.get_tt_download_kb Get: tiktok_id={tiktok_id}, message_id={message_id}, type_={type_}')
		if type_ == 'share_video':
			download_button = self.get_tt_audio_button(tiktok_id=tiktok_id, message_id=message_id)
		elif type_ == 'share_audio':
			download_button = self.get_tt_video_button(tiktok_id=tiktok_id, message_id=message_id)

		share_button = self.get_tt_share_button(content_id=tiktok_id, type_=type_)

		keyboard = InlineKeyboardMarkup(row_width=1).add(download_button).add(share_button)
		logger.debug(f'method kb.get_tt_download_kb: return keyboard={keyboard}')
		return keyboard






	def get_tt_audio_button(self,
							tiktok_id: str,
							message_id: int):
		'''
		Get:
			tiktok_id: tiktok video unique id.
			message_id: main message user sended with tiktok link
		Return: TikTok audio button.
		'''
		logger.debug(f'Method kb.get_tt_audio_button Get: tiktok_id={tiktok_id}, message_id={message_id}')
		button = Button(keyboards.get('TT AUDIO BUTTON').get('NAME'),
						callback_data=keyboards.get('TT AUDIO BUTTON').get('CALLBACK').format(tiktok_id, message_id))
		logger.debug(f'method kb.get_tt_audio_button: return button={button}')
		return button

	def get_tt_video_button(self,
							tiktok_id: str,
							message_id: int):
		'''
		Get:
			tiktok_id: tiktok video unique id.
			message_id: main message user sended with tiktok link
		Return: TikTok video button.
		'''
		logger.debug(f'Method kb.get_tt_audio_button Get: tiktok_id={tiktok_id}, message_id={message_id}')
		button = Button(keyboards.get('TT VIDEO BUTTON').get('NAME'),
						callback_data=keyboards.get('TT VIDEO BUTTON').get('CALLBACK').format(tiktok_id, message_id))
		logger.debug(f'method kb.get_tt_video_button: return button={button}')
		return button

	def get_tt_share_button(self,
							content_id: str,
							type_: str,
							keyboard=False):
		'''
		Get:
			content_id: tiktok video unique id.
			type_: sharing type
			keyboard: if True -> return keyboard, if False -> return Button
		Return: TikTok video button or keyboard.
		'''
		logger.debug(f'Method kb.get_tt_share_button Get: content_id={content_id}, type_={type_}, keyboard={keyboard}')
		share_button = Button(keyboards.get('SHARE BUTTON').get('NAME'),
			   		  		  switch_inline_query=f'{type_} {content_id}')
		if keyboard:
			keyboard = InlineKeyboardMarkup(row_width=1).add(share_button)
			logger.debug(f'method kb.get_tt_share_button: return keyboard={keyboard}')
			return keyboard
		logger.debug(f'method kb.get_tt_share_button: return button={share_button}')
		return share_button


	def get_yt_share_button(self,
							content_id: str,
							type_: str,
							chat_id,
							uid,
							msg_id,
							m4a,
							callback_data,
							keyboard=False):
		'''
		Get: 
			content_id: YouTube video unique id.
			type_: sharing type
			chat_id: user's chat id
			uid: user id
			msg_id: main message id
			m4a:
			callback_data:
			keyboard:
		Return: YouTube share button or keyboard
		'''
		if callback_data is not None:
			callback_data = f'from {resolution} {content_id} {chat_id} {msg_id}'

		share_button = Button(keyboards.get('SHARE BUTTON').get('NAME'),
			   		  		  switch_inline_query=f'{type_} {content_id}')
		
		if keyboard:
			kb = InlineKeyboardMarkup(row_width=1)
			yt_obj = YouTube(f'https://youtu.be/{content_id}')
			print(type_)
			resolution = type_.split(' ')[2]
			audio_button = self.get_yt_audio_button(yt_id=content_id, msg_id=msg_id, m4a=m4a, 
												    yt_object=yt_obj, chat_id=chat_id, uid=uid,
												    callback_data=callback_data)

			return InlineKeyboardMarkup(row_width=1).add(audio_button).add(share_button)

		return InlineKeyboardMarkup(row_width=1).add(share_button)




	def get_youtube_download_kb(self, youtube_id, main_message_id):
		keyboard = InlineKeyboardMarkup(row_width=1)
		for button_data in keyboards.get('YOUTUBE DOWNLOAD KEYBOARD').values():
			callback_data = button_data.get('CALLBACK DATA')
			keyboard.add(Button(button_data.get('NAME'),
								callback_data=callback_data.format(youtube_id, main_message_id)))
		logger.debug(f'method kb.get_youtube_download_kb: return keyboard={keyboard}')
		return keyboard


	def get_sender(self, filesize):
		if filesize > 2e+9:
			logger.debug(f'method kb.get_sender: return None')
			return None
		elif 5e+7 < filesize < 2e+9:
			logger.debug(f'method kb.get_sender: return userbot')
			return 'userbot'
		elif filesize < 5e+7:
			logger.debug(f'method kb.get_sender: return bot')
			return 'bot'



	def get_youtube_keyboard(self,
	                         yt_object,
	                         yt_id,
	                         msg_id,
	                         chat_id,
	                         uid,
	                         resolutions=None):

		if resolutions is None:
			resolutions = {'720p': 'High', '360p': 'Medium', '144p': 'Low'}

		keyboard = InlineKeyboardMarkup(row_width=1)
		for res_key, res_val in resolutions.items():
			sender = ''
			video = yt_object.streams.filter(res=res_key)
			if video:
				itag = tuple(video.itag_index)[0]
				videosize = video.get_by_itag(itag).filesize
				sender = self.get_sender(videosize)
				if sender is not None:
					keyboard.add(Button(res_val, callback_data=f'{sender} {res_key} {yt_id} {chat_id} {msg_id}'))
		logger.debug(f'method kb.get_youtube_keyboard: return keyboard={keyboard}')
		return keyboard


	def get_yt_video_button(self, yt_id, msg_id, keyboard=False):
		return Button(keyboards.get('YT VIDEO BUTTON').get('NAME'),
				   	  callback_data=keyboards.get('YT VIDEO BUTTON').get('CALLBACK')\
				   	  						  .format(yt_id, msg_id))



	def get_yt_audio_button(self, yt_id, msg_id, m4a=False,
							yt_object=None, chat_id=None, uid=None,
							callback_data=None):

		

		resolution = 'mp3' if m4a is False else 'm4a'
		if yt_object is not None:
			sender = ''
			audio = yt_object.streams.filter(only_audio=True).desc().first()
			if audio:
				audiosize = audio.filesize
				sender = self.get_sender(audiosize)
				if sender is not None:
					if callback_data is None:
						callback_data = keyboards.get('YT AUDIO BUTTON').get('CALLBACK')\
							   	  					.format(sender, resolution, yt_id, chat_id, msg_id)
					return Button(keyboards.get('YT AUDIO BUTTON').get('NAME').format(resolution),
				   	  			  callback_data=callback_data)









		return Button(keyboards.get('YT MP3 BUTTON').get('NAME'),
				   	  callback_data=keyboards.get('YT MP3 BUTTON').get('CALLBACK')\
				   	  						  .format(yt_id, msg_id))

	


	def get_yt_download_kb(self, yt_id, msg_id, yt_object=None, chat_id=None, uid=None):

		vid_button = self.get_yt_video_button(yt_id=yt_id, msg_id=msg_id)
		aud_button = self.get_yt_audio_button(yt_object=yt_object, yt_id=yt_id,
											  msg_id=msg_id, chat_id=chat_id, uid=uid)


		keyboard = InlineKeyboardMarkup(row_width=1).add(vid_button).add(aud_button)
		logger.debug(f'method kb.get_yt_download_kb: return keyboard={keyboard}')
		return keyboard

