import time

import psycopg2
from django.conf import settings

host = settings.DATABASES["default"]["HOST"]
user = settings.DATABASES["default"]["USER"]
password = settings.DATABASES["default"]["PASSWORD"]
port = int(settings.DATABASES["default"]["PORT"])
db = settings.DATABASES["default"]["NAME"]

message = f"""
    ################################
    database connect:
    host = {host}
    user = {user}
    port = {port}
    db = {db}
    ################################
"""

print(message)

conn = None

while True:
    try:
        conn = psycopg2.connect(host=host, user=user, password=password, port=port, dbname=db)
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
        if conn:
            cursor.close()
            conn.close()
            break

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
        time.sleep(1)
        continue
