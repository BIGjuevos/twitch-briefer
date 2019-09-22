import logging

import pymysql
from pymysqlpool.pool import Pool

pool = Pool(host="maria.ryannull.com", port=3306, user="otc", password="otc", db="otc", min_size=1, max_size=2)
pool.init()


def just_end_it_all():
    pool.destroy()


def set_data(thing, value):
    connection = pool.get_conn()
    cursor = connection.cursor()
    try:
        connection.begin()

        cursor.execute('UPDATE databits SET val=%s WHERE nam=%s', (value, thing))

        if thing == "og" and value == "1" and get_data('og') == '0':
            cursor.execute('REPLACE INTO databits (nam,val) VALUES(%s,%s)', ("touchdown_vs", get_data('vs'), ))

        connection.commit()
    except Exception as e:
        logging.getLogger().error(e)
        connection.rollback()
    finally:
        cursor.close()
        pool.release(connection)


def guess(username, speed):
    connection = pool.get_conn()
    cursor = connection.cursor()
    try:
        connection.begin()

        cursor.execute('REPLACE INTO guesses(username,speed) VALUES(%s,%s)', (username, speed))

        connection.commit()
    except Exception as e:
        logging.getLogger().error(e)
    finally:
        cursor.close()
        pool.release(connection)


def get_data(thing):
    connection = pool.get_conn()
    cursor = connection.cursor()
    ret = ""

    try:
        connection.begin()
        if thing == "map":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("lat",))
            lat = cursor.fetchone()["val"]

            cursor.execute("SELECT * from databits WHERE nam=%s", ("lng",))
            lng = cursor.fetchone()["val"]

            cursor.execute("SELECT * from databits WHERE nam=%s", ("hdg",))
            hdg = cursor.fetchone()["val"]

            cursor.execute("SELECT * from databits WHERE nam=%s", ("gs",))
            gs = cursor.fetchone()["val"]

            ret = {
                'lat': lat,
                'lng': lng,
                'hdg': hdg,
                'gs': gs
            }
        elif thing == "hdg":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("hdg",))
            ret = cursor.fetchone()["val"]
        elif thing == "gs":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("gs",))
            ret = cursor.fetchone()["val"]
        elif thing == "vs":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("vs",))
            ret = cursor.fetchone()["val"]
        elif thing == "og":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("og",))
            ret = cursor.fetchone()["val"]
        elif thing == "tas":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("tas",))
            ret = cursor.fetchone()["val"]
        elif thing == "alt":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("alt",))
            ret = cursor.fetchone()["val"]
        elif thing == "rte":
            cursor.execute("SELECT * from databits WHERE nam=%s", ("dep",))
            dep = cursor.fetchone()["val"]

            cursor.execute("SELECT * from databits WHERE nam=%s", ("arr",))
            arr = cursor.fetchone()["val"]

            cursor.execute("SELECT * from databits WHERE nam=%s", ("rte",))
            rte = cursor.fetchone()["val"]

            ret = dep + " " + rte + " " + arr

    except Exception as e:
        logging.getLogger().error(e)
    finally:
        connection.rollback()
        cursor.close()
        pool.release(connection)
        return ret
