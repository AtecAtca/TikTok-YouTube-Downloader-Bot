import psycopg2 as pg
from tools.logger import get_logger

class dataBase():
    """
    Using heroku-postgresql.
    """
    def __init__(self):
        try:
            self.conn = pg.connect(user="",
                                   password="",
                                   host="",
                                   port="",
                                   database="")
        except Exception as e:          
            logger.exception(e)
        else:
            logger.info('Database connected successfully')

    def close_on_shutdown(self) -> None:
        """
        Close connection while bot turned off.
        """
        self.conn.close()

    async def get(self,
                  items: tuple,
                  table_name: str,
                  condition: dict,
                  order_by: dict = None,
                  fetchall=False, ):
        key, value = tuple(condition.items())[0]
        query = f'SELECT {", ".join(items)} FROM {table_name} WHERE {key} = %s'
        with self.conn:
            with self.conn.cursor() as cur:
                if order_by is not None:
                    query += ' ORDER BY {} {}'.format(*tuple(order_by.items())[0])
                cur.execute(query, (value,))
                result = cur.fetchall() if fetchall else cur.fetchone()
                if result is None:
                    logger.debug(f'method db.get: return result=None')
                    return None
                else:
                    if len(items) == 1:
                        logger.debug(f'method db.get: return result={result[0]}')
                        return result[0]
                    else:
                        logger.debug(f'method db.get: return result={result}')
                        return result

    async def insert(self, items: dict, table_name: str):
        keys = [key for key in items.keys()]
        values = [value for value in items.values()]
        columns = (", ".join(keys)).replace("'", '')
        columns_values = "%s, " * len(keys)
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({columns_values[:-2]});'
        with self.conn:
            with self.conn.cursor() as cur:
                logger.debug(f'method db.insert: {query}, {values}')
                cur.execute(query, values)

    async def update(self,
                     items: dict,
                     table_name: str,
                     condition: dict,
                     array_func: str=None):

        item_key, item_value = tuple(items.items())[0]
        condition_key, condition_value = tuple(condition.items())[0]

        if array_func is None:
            query = f'UPDATE {table_name} SET {item_key} = %s WHERE {condition_key} = %s;'
        else:
            query = f'UPDATE {table_name} SET {item_key} = {array_func}({item_key}, %s) WHERE {condition_key} = %s;'

        with self.conn:
            with self.conn.cursor() as cur:
                logger.debug(f'method db.update: {query}, {item_value, condition_value}')
                cur.execute(query, (item_value, condition_value))

    async def insert_or_update_video(self, tg_id, tiktok_id, doc_id_video):
        query = "INSERT INTO tiktok_files (tg_id, tiktok_id, doc_id_video, doc_id_audio) "\
                "VALUES (%s, %s, %s, %s) "\
                "ON CONFLICT (tiktok_id) "\
                "DO UPDATE SET doc_id_video = %s "
        with self.conn:
            with self.conn.cursor() as cur:
                logger.debug(f'method db.insert_or_update_video: {query}')
                cur.execute(query, [tg_id, tiktok_id, doc_id_video, None, doc_id_video])

    async def insert_or_update_audio(self, tg_id, tiktok_id, doc_id_audio):
        query = "INSERT INTO tiktok_files (tg_id, tiktok_id, doc_id_video, doc_id_audio) "\
                "VALUES (%s, %s, %s, %s) "\
                "ON CONFLICT (tiktok_id) "\
                "DO UPDATE SET doc_id_audio = %s "
        with self.conn:
            with self.conn.cursor() as cur:
                logger.debug(f'method db.insert_or_update_video: {query}')
                cur.execute(query, [tg_id, tiktok_id, None, doc_id_audio, doc_id_audio])

        



    async def insert_or_update(self,
                               tablename: str,
                               ins_items: dict,
                               condition: tuple,
                               upd_items: dict,
                               set_pool='SET ',
                               upd_list=None):
        if upd_list is None:
            upd_list = []

        keys = [key for key in ins_items.keys()]
        values = [value for value in ins_items.values()]
        columns = (", ".join(keys)).replace("'", '')
        columns_values = "%s, " * len(keys)
        query = f"INSERT INTO {tablename} ({columns}) VALUES ({columns_values[:-2]})"

        for key, value in upd_items.items():
            upd_list.append(value)
            set_pool += f'{key} = %s, '

        query = query + f"ON CONFLICT ({', '.join(condition)}) " + f"DO UPDATE {set_pool[:-2]};"
    
        with self.conn:
            with self.conn.cursor() as cur:
                logger.debug(f'method db.insert_or_update: {query}, {tuple(values + upd_list)}')
                cur.execute(query, tuple(values + upd_list))


logger = get_logger('tools.database.py')
db = dataBase()