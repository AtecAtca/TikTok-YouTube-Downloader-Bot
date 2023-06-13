import psycopg2 as pg


def check_connect():
	'''
	Simple check connection status of database
	'''
	conn = pg.connect(user="",
					  password="",
	                  host="",
	                  port="",
	                  database="")
	with conn:
		with conn.cursor() as cur:
			print(conn.get_dsn_parameters(), "\n")    
			cur.execute("SELECT version();")
			record = cur.fetchone()
			print("You're connected - ", record, "\n")


def create_table_users():
	'''
	Create main table of users
	The user is added to this table as soon as the bot is launched
	'''
	conn = pg.connect(user="",
					  password="",
	                  host="",
	                  port="",
	                  database="")
	with conn:
		with conn.cursor() as cur:
			cur.execute('''CREATE TABLE IF NOT EXISTS users(
						   id SERIAL PRIMARY KEY,
						   tg_id BIGINT UNIQUE NOT NULL,
						   tg_name VARCHAR,
						   tg_username VARCHAR,
						   language VARCHAR(2) NOT NULL,
						   user_state VARCHAR, #state used for refferal, admin-panel or AD menu
						   is_banned BOOL)''')


def create_table_tiktok_files():
	'''
	Create table of tiktok video/audio ID 
	As soon as the bot sends a file to the user, its ID is immediately written to the table.
	The next time the bot doesn't need to download such a file, it will just use the ID and send the file instantly.
	'''
	conn = pg.connect(user="",
					  password="",
	                  host="",
	                  port="",
	                  database="")
	with conn:
		with conn.cursor() as cur:
			cur.execute('''CREATE TABLE IF NOT EXISTS tiktok_files(
						   id SERIAL PRIMARY KEY,
						   tg_id BIGINT NOT NULL,
						   tiktok_id VARCHAR UNIQUE NOT NULL,
						   doc_id_video VARCHAR,
						   doc_id_audio VARCHAR)''')


def create_table_youtube_files():
	'''
	Create table of youtube video/audio ID 
	As soon as the bot sends a file to the user, its ID is immediately written to the table.
	The next time the bot doesn't need to download such a file, it will just use the ID and send the file instantly.
	'''
	conn = pg.connect(user="",
					  password="",
	                  host="",
	                  port="",
	                  database="")
	with conn:
		with conn.cursor() as cur:
			cur.execute('''CREATE TABLE IF NOT EXISTS youtube_files(
						   id SERIAL PRIMARY KEY,
						   tg_id BIGINT NOT NULL,
						   youtube_id VARCHAR UNIQUE NOT NULL,
						   doc_id_720p VARCHAR,
						   doc_id_360p VARCHAR,
						   doc_id_144p VARCHAR,
						   doc_id_mp3 VARCHAR,
						   doc_id_m4a VARCHAR)''')


check_connect()

# uncomment the desired functions below:

#create_table_users()
#create_table_tiktok_files()
#create_table_youtube_files()

input()