from aiogram import types
from pytube import YouTube
from pytube.exceptions import LiveStreamError, RegexMatchError, VideoUnavailable
from string import punctuation
from io import BytesIO
from tools.logger import get_logger
import time


async def is_youtube_url(message: types.Message):
	try:
		yt = YouTube(message.text)
		yt.check_availability()
	except (LiveStreamError, RegexMatchError, VideoUnavailable) as e:
		logger.exception(e)
		return None
	else:
		logger.debug(f'function is_youtube_url return True: {yt}')
		return yt


async def get_yid(message: types.Message):
	youtube_id = YouTube(message.text).video_id
	logger.debug(f'function get_yid return: {youtube_id}')
	return youtube_id


async def get_download_path(uid, youtube_id, content):
    yt_object = YouTube(f'https://youtu.be/{youtube_id}')
    title = yt_object.title.translate(str.maketrans(' ', '_', punctuation))
    path = f'C:\\Bot\\Data\\{uid}\\{content}'
    filename = f'{title}.mp4' if content == 'video' else f'{title}.mp3'

    logger.debug(f'function get_download_path return: {path, filename, yt_object}')
    return path, filename, yt_object


async def download_content(uid, youtube_id, path, filename):
	yt = YouTube(f'https://youtu.be/{youtube_id}')
	video = yt.streams.filter(progressive=True).desc().first()
	title = yt.title.translate(str.maketrans(' ', '_', punctuation))

	logger.info(f'function download_content start downloading: {path}{filename}')
	t1 = time.perf_counter()
	video.download(output_path=path, filename=filename)
	t2 = time.perf_counter()
	logger.info(f'function download_content finish downloading: {path}{filename} Spent time: {t2-t1}')
	

logger = get_logger('tools.youtube_tools.py')

