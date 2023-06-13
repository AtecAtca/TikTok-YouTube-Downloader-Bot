




====================================================================================
============================= CONFIG AND MAIN SETTINGS =============================
====================================================================================
? AWS Lightsail:

  Go to https://lightsail.aws.amazon.com/ls/webapp/home/instances
  Select instance Windows_Server -> Networking
  Set IPv4 Firewall and IPv6 Firewall rules if doesn't exist:

	Application - Protocol - Port - Restricted to
	Ping (ICMP) - ICMP     -      - Any IPv4 address
	SSH	    - TCP      -   22 - Any IPv4 address, Lightsail browser SSH/RDP
	HTTP        - TCP      -   80 - Any IPv4 address
	HTTPS       - TCP      -  443 - Any IPv4 address
	RDP 	    - TCP      - 3389 - Any IPv4 address, Lightsail browser SSH/RDP
	Custom 	    - TCP      - 5000 - Any IPv4 address
	PostgreSQL  - TCP      - 5432 - Any IPv4 address
====================================================================================				
? System: Recycle bin autocleaning

  Control Panel -> System and Security -> Administrative Tools ->Schedule tasks:
	task name: Clear Recyclebin
	trigger: Daily: at 12:00:00 AM every day
	action: Start a Program: PowerShell.exe
	details: Clear-RecycleBin -force -ErrorAction:Ignore
====================================================================================
? DataBase PostgreSQL:

  Database settings:

         Download PostgreSQL 
	 https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
	 PostgreSQL Version: 12.13
         Windows x86-32

      user: postgres
      password: atecatca
      host: 127.0.0.1
      port: 5432
      database: db_main

      pgAdmin4 password: atecatca

  C:\Bot\requester.py contains functions to create tables
====================================================================================
? Webserver:

  Run ngrok.exe as administrator.
	Set token with command: ./ngrok authtoken TOKEN
			    or: ngrok config add-authtoken TOKEN
			    or: Go to C:\Users\Administrator\AppData\Local\ngrok\ngrok.yml
				if .yml file is exists edit it with your TOKEN:
				authtoken: TOKEN
====================================================================================
? Telegram BOT confing:

  Go to C:\Bot\tools\bot.py -> open with any editor:
  Go to 7 line: TOKEN: = 'YOUR-TOKEN'
	example: '5774805853:AAFlHU8aTR6FvBfsd5gUkBHRidsjnzK-iH8'


  Go to C:\Bot\tools\getup.py -> open with any editor:
  Go to 1 line: default: 

      1)'language': main language for bot's Interface. 'EN' by default.
              available languages: 
	      'EN' - English, 'RU' - Russian, 'TU' - Turkish,    'SP' - Spanish, 
	      'HI' - Hindi,   'UR' - Urdu,    'IN' - Indonesian, 'PH' - Filipino        
      2)'channel_id': the channel to which the user should subscribe
              example: '@upwork_mytest_bot'
      3)'bot_username': just the username of the Bot
              example: '@upwork_mytest_bot'
      4)'bot_name': just the name of the Bot
              example: 'RedownloadBot'
      5)'inline_logo': skip. It's no longer in use.
              example: ...
      6)'help_photo_id': skip. It's no longer in use.
              example: ...
      7)'userbot_id': you can find using @my_id_bot
              example: 5275396121
      8)'bot_id': you can find using @my_id_bot or from Bot's TOKEN 5773205853:AAF.....
              example: 5774805853
====================================================================================	
? Telegram USERBOT confing:

  Go to C:\Bot\tools\userbot.py -> open with any editor:
  Go to 11 line:

	1)PATH: path to main folder of project
              example: 'C:\\Bot'
	2)BOT_ID: just the Bot id (not UserBot!) 
                  you can find using @my_id_bot or from Bot's TOKEN 5773205853:AAF.....
	      example: '5774805853:AAFlHU8aTR6FvBfsd5gUkBHRidsjnzK-iH8'
	3)API_ID: you can find it here https://my.telegram.org/auth?to=apps
	      example: '12385241'
	4)API_HASH: you can find it here https://my.telegram.org/auth?to=apps
	      example: '1c04e60a56b1234539d000ed6fb07dbd'
	5)SESSION: just a session unique name. Important: 1 session for 1 account
	      example: 'my_session'
	6)PHONE: for auth when userbot starts by the first time.
		 You need write a phone number, than press 'y'
		 Next step is verification code you taked on Telegram.
		 Next step is confirm password if two-steps verification exists
====================================================================================	     





====================================================================================
=================================== HOW IT WORKS ===================================
====================================================================================

There are 3 programs that must be run without errors for the project to work.

1) Ngrok

   This is a connector between the main Telegram server and our bot running locally.
   How to run correctly:
      1) run ngrok.exe
      2) write: ngrok http http:/localhost:5000
      3) if its done you'll see your ngrok admin panel
	 Session Status must be online!
      4) Copy a long url from forwarding:
	 https://4e13-2a05-d014-91-9f00-d2d4-f2c-f0a1-42b8.eu.ngrok.io
      5) Open main.py and paste url to WEBHOOK_URL

   Just remember that each restart of the webserver will create a new link that will need to    be substituted into the main.py file

2) UserBot

   First of all, it is needed in order to download files larger than 50 mb
   Downloading limits: 2gb each file or 4gb if UserBot have premium account
   Secondly, the userbot reduces the load on the bot and downloads files one by one.

   How to run correctly:
      1) run_userbot.bat
         You will need to log in by phone number, enter the code that you receive from the            telegram. Then enter the password. If authorization is successful, you will see a            message in the console.

3) Bot

   The main program that interacts with everything.
   A little more will be written about this below.

   How to run correctly:
      1) local_start.bat
         The Bot works perfectly if you see these messages in terminal:

         INFO | tools.bot.py:28 | Telegram bot connected successfully.
         INFO | tools.database.py:18 | Database connected successfully
         INFO | handlers.callbacks.py:499 | Register callback handlers.
         INFO | handlers.messages.py:332 | Register message handlers.
         Updates were skipped successfully.
         INFO | main.py:26 | Executor started.
         ======== Running on http://127.0.0.1:5000 ========
         (Press CTRL+C to quit)

====================================================================================

Okay, now let's go through the program structure in order:

1. The bot init by Telegram Bot API TOKEN here: C:\Bot\tools\bot.py
2. Point of entry is here:  C:\Bot\main.py: 

      if __name__ == '__main__':
          run(webhook=True)

3. You can also change Webhook or Polling settings with True/False parameter
   but we are only interested in the Webhook

4. Function run()...

   All basic bot and webhook settings are passed to the executor.
   When the bot is launched, a webhook is created.
   Shutting down the bot removes the webhook and disables the database

5. You can also notice the handlers:
   They are imported from their respective modules. More on that below.

    inline_handlers(dp)
    command_handlers(dp)
    callback_handlers(dp)
    message_handlers(dp)
====================================================================================

6. When the user use bot for the first time, he send command /start:

   in commands.py: in cmd_start() handler:
	if user is new - add him to database

   now we have all the information about user: 
	user id, first name, username, etc.
		

7. When the user send command /lang:

   in commands.py: in cmd_lang() handler:
	bot send language keyboard and user can selected one language

8. When the user send command /help:

   in commands.py: in cmd_help() handler:
	bot send FAQ mesage with FAQ button linked to information

====================================================================================

9. When the user send any message, Bot try to find an url in message

   in messages.py: in message() handler: 

   	...
   	if await is_url(message): 
	...

	
10. If any url in message, Bot check subcsribtion to the channel:

   in messages.py: in message() handler: 

     	...
   	if await is_member(uid):
	...

11. If user is not subscribed, Bot send 'PLEASE SUBSCRIBE' message with subscribe button

    in messages.py: in message() handler: 

	...
     	else:
            # user is not subscribed
            # bot send 'PLEASE SUBSCRIBE' message with subscribe button
            await message.reply(text=messages.get('PLEASE SUBSCRIBE')...
	    ...

====================================================================================


12. How TikTok Downloading works:
	
	Video .mp4:
	in tools\tiktok_tools.py: in class TiktokDownloader: in musicaldown() function

	Using requests to https://musicaldown.com
        get videofile by bytes. It's impossible to sent bytes via Telegram

	Video .mp3:
	Just the same tactic to get videofile bytes. But send it via Telegram as audio.
	It will automatically convert .mp4 to .mp3 file
	
	
13. How YouTube Downloading works

	1. Using pytube library
	2. Using UserBot to send files more than 50mb
	
	The bot download file to C:\Bot\Data\*userid\**format\filename...
	* telegram user id. Folder will create automatically
        ** 720p or 360p or 144p or mp3 or m4a. Folder will create automatically

	If size of file < 50mb, bot send it to user
	Than bot save file id and put into database
	
	If size of file > 50 bm 
	Bot send command /a or /v with user id, chat id, message id and other metadata
	Userbot get commant from bot and starts downloading to C:\Bot\Data\*userid\**format\filename...
	Than userbot send file to bot with some metadata as user id, chat id, message id, etc
	Bot get file and save its file id
	Than bot send file to user by id

	After succesfully downloading and sending the file will delete.



	
	
=========================================================================================
=================================== PROJECT FOLDERS AND FILES ===========================
=========================================================================================

1) DATA 
	For every user create folder with userid
	example:
	C:\Bot\Data\526381988\mp3\filename.mp3

2) handlers

	callbacks.py
	Every button on bot have own callback_data
	All callbacks are handled here
	
	commands.py
	Here is the processing of commands that the user sends
	example: /start, /help, etc

	inlines.py
	Here is a function that is responsible for file sharing
	It works where inline mode enable in BotFather's settings
	
	messages.py
	Handler for incoming messages in a bot or chat.

3) keyboards
	
	inline.py
	Here are keyboards and buttons functions
	
4) tools

	bot.py
	Here is init of bot by TOKEN

	database.py
	Just a tools for making queries to database PostgreSQL

	getup.py
	All texts for messages and buttons here
	Also default settings 

	logger.py
	Just a simple logger, writting to terminal

	tiktok_tools.py
	Here are main functions for tiktok downloading

	youtube_tools.
	Here are main functions for youtube downloading

5) userbot

	UserBot.py
	Here is main code for userbot
	After login userbot will create .session and .session-journal files

6) local_start.bat - run bot.

7) main.py - here is main file with webhook settings and run loop
	
8) ngrok.exe - run webserver

9) requester.py - functions to create tables. 

10) run_userbot.bat - run userbot.