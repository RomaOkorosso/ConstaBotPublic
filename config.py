import psycopg2

# need tokens for test and main bots, databases connection data
# and some const IDs

test = ""
main = ""

database = ""
user = ""
password = ""
host = ""
port = "5432"


def connect_with_database():
    con = psycopg2.connect(
        database=database, user=user, password=password, host=host, port=port
    )
    return con


roman = 111
artem = 222
legolas = 333
alarm = -10001111
