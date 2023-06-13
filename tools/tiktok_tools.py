import requests
import bs4
from tools.logger import get_logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class TiktokDownloader:
    '''
    TikTok downloader use requests method to 'https://musicaldown.com/' website.

    '''
    def __init__(self):
        self.download_link = None
        pass

    async def musicaldown(self, url, output_name):
        """url: tiktok video url
        output_name: output video (.mp4). Example : video.mp4
        """
        # init session
        session = requests.Session()

        # setup adapter
        # it helps in situations with some errors
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # setup url and headers
        server_url = 'https://musicaldown.com/'
        headers = {
            "Host": "musicaldown.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "TE": "trailers"
        }
        
        # update headers to session
        session.headers.update(headers)

        # try to request and get response
        req = session.get(server_url) 
        data = {}

        # get full html page
        parse = bs4.BeautifulSoup(req.text, 'html.parser') 

        # find buttons with videofiles data 
        get_all_input = parse.findAll('input')
        for i in get_all_input:
            if i.get("id") == "link_url":
                data[i.get("name")] = url
            else:
                data[i.get("name")] = i.get("value")
        post_url = server_url + "id/download"


        req_post = session.post(post_url, data=data, allow_redirects=True)
        if req_post.status_code == 302 or 'This video is currently not available' in req_post.text or 'Video is private or removed!' in req_post.text:
            print('- video private or remove')
            return 'private/remove'
        elif 'Submitted Url is Invalid, Try Again' in req_post.text:
            print('- url is invalid')
            return 'url-invalid'

        # send request to get videofile
        match output_name:
            case 'video' | 'audio':
                self.download_link = self.get_nowatermark(req_post)
                get_content = requests.get(self.download_link)

                #get binnary code of file
                #now it can be sended via Telegram
                content = get_content.content
                #logger.debug(f'method tt.musicaldown return: {content}')
                return get_content.content

    # not worked yet            
    #def get_watermark(self, req_post):
    #    result = bs4.BeautifulSoup(req_post.text, 'html.parser').findAll('i', text='arrow_downward')
    #    for r in result:
    #        if r.parent.text == 'arrow_downwardUnduh MP4 [Watermark]':
    #            logger.debug(f"method tt.get_watermark return: {r.parent.get('href')}")
    #            return r.parent.get('href') #download link

    def get_nowatermark(self, req_post):
        '''
        From all downloading links get just one to download video without wotermark.
        '''
        get_all_blank = bs4.BeautifulSoup(req_post.text, 'html.parser').findAll(
            'a', attrs={'target': '_blank'})
        link = get_all_blank[0].get('href')
        logger.debug(f'method tt.get_nowatermarkk return: {link}')
        return link

logger = get_logger('tools.tiktok_tools.py')