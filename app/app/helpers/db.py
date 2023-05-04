import logging

from pymysql.cursors import DictCursor
from pymysqlpool.pool import Pool

pool = Pool(host="10.0.10.4", port=3306, user="otc", password="otc", db="otc", min_size=1, max_size=2)
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


def get_airport_data(airport) -> dict:
    connection = pool.get_conn()
    cursor = connection.cursor()
    ret = {}

    try:
        connection.begin()
        cursor.execute(f"SELECT * from airports WHERE ident=\"{airport}\" LIMIT 1")
        ret = cursor.fetchone()
    except Exception as e:
        logging.getLogger().error(e)
    finally:
        cursor.close()
        pool.release(connection)

    return ret


def get_data():
    connection = pool.get_conn()
    cursor = connection.cursor(DictCursor)
    ret = {}

    try:
        connection.begin()
        cursor.execute("SELECT * from databits")
        for bit in cursor.fetchall():
            ret[bit["nam"]] = bit["val"]

            if bit["nam"] == "alt":
                ret[bit["nam"]] = int(float(bit["val"]))
            elif bit["nam"] == "vs":
                if bit["val"] == "-0":
                    ret[bit["nam"]] = "0"

        # dep info
        cursor.execute(f"SELECT ident, lonx, laty, name from airports WHERE ident=\"{ret['dep']}\" LIMIT 1")
        dep = dict(cursor.fetchone())
        dep['lonx'] = float(dep['lonx'])
        dep['laty'] = float(dep['laty'])
        ret['dep'] = dep

        # arr info
        cursor.execute(f"SELECT ident, lonx, laty, name from airports WHERE ident=\"{ret['arr']}\" LIMIT 1")
        arr = dict(cursor.fetchone())
        arr['lonx'] = float(arr['lonx'])
        arr['laty'] = float(arr['laty'])
        ret['arr'] = arr
    except Exception as e:
        logging.getLogger().error(e)
        raise e
    finally:
        connection.rollback()
        cursor.close()
        pool.release(connection)
        return ret
