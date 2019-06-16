import pymysql

connection = pymysql.connect(host='maria.ryannull.com',
                             user='otc',
                             password='otc',
                             db='otc',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)


def set_data(thing, value):
    with connection.cursor() as cursor:
        cursor.execute('REPLACE INTO databits (nam,val) VALUES(%s,%s)', (thing, value))
    connection.commit()


def get_data(thing):
    with connection.cursor() as cursor:
        if thing == "map":
            cursor.execute("SELECT * from databits WHERE nam=%s", ('lat',))
            lat = cursor.fetchone()['val']

            cursor.execute("SELECT * from databits WHERE nam=%s", ('lng',))
            lng = cursor.fetchone()['val']

            cursor.execute("SELECT * from databits WHERE nam=%s", ('hdg',))
            hdg = cursor.fetchone()['val']

            cursor.execute("SELECT * from databits WHERE nam=%s", ('gs',))
            gs = cursor.fetchone()['val']

            return {
                'lat': lat,
                'lng': lng,
                'hdg': hdg,
                'gs': gs
            }
        elif thing == "hdg":
            cursor.execute("SELECT * from databits WHERE nam=%s", ('hdg',))
            return cursor.fetchone()['val']
        elif thing == "gs":
            cursor.execute("SELECT * from databits WHERE nam=%s", ('gs',))
            return cursor.fetchone()['val']
        elif thing == "tas":
            cursor.execute("SELECT * from databits WHERE nam=%s", ('tas',))
            return cursor.fetchone()['val']
        elif thing == "alt":
            cursor.execute("SELECT * from databits WHERE nam=%s", ('alt',))
            return cursor.fetchone()['val']
        elif thing == "rte":
            cursor.execute("SELECT * from databits WHERE nam=%s", ('dep',))
            dep = cursor.fetchone()['val']

            cursor.execute("SELECT * from databits WHERE nam=%s", ('arr',))
            arr = cursor.fetchone()['val']

            cursor.execute("SELECT * from databits WHERE nam=%s", ('rte',))
            rte = cursor.fetchone()['val']

            return dep + " " + rte + " " + arr
