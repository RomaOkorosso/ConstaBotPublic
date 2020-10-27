import telebot
import config
import datetime
import pytz
import database_functions

con = config.connect_with_database()


# CREATE table main_profiles(user_id INT, username TEXT, first_last_names TEXT, acc_type TEXT, coins INT,
# start_prem TIMESTAMP, end_prem TIMESTAMP, used_trail BOOL, admin_type TEXT);


def create_profile(user_id, username, first_last_names):
    cur = con.cursor()
    cur.execute(f"""SELECT * FROM main_profiles WHERE user_id = {user_id}""")
    db = cur.fetchone()
    if db is not None:
        cur.execute(f"""INSERT INTO main_profiles (user_id, username, first_lsat_names, acc_type, coins, used_trail)
                        VALUES ({user_id}, {username}, {first_last_names}, "basic", 0, True)""")
        con.commit()
    return "Аккаунт создан"


def try_start_trail(user_id):
    cur = con.cursor()
    cur.execute(f"""SELECT used_trail FROM main_profiles WHERE user_id = {user_id}""")
    trail = cur.fetchone()
    if trail is True:
        result = start_trail(user_id)
    else:
        result = "Вы уже использовали пробный период"
    return result


def start_trail(user_id):
    try:
        trail_prem_day = 3
        start_date = datetime.datetime.now(tz=pytz.utc)
        end_prem = start_date + datetime.timedelta(days=trail_prem_day)
        cur = con.cursor()
        cur.execute(
            f"""UPDATE main_profiles SET start_prem = {start_date}, end_prem = {end_prem}, used_trail = {False} WHERE user_id = {user_id}""")
        con.commit()
        return f'Премиум на {trail_prem_day} дня'
    except:
        return "Произошла какая-то ошибка, обратитесь к разработчику"


def check_admin_properties(user_id):
    cur = con.cursor()
    cur.execute(f"""SELECT admin_type FROM main_profiles WHERE user_id = {user_id}""")
    prop = cur.fetchone()
    return prop


def add_permission(user_id, add_perm):
    try:
        cur = con.cursor()
        prop = check_admin_properties(user_id)
        if add_perm not in prop:
            new_perm = prop + add_perm
            cur.execute(f"""UPDATE main_profiles SET admin_type = {new_perm} WHERE user_id = {user_id}""")
            con.commit()
            return 'done'
        else:
            return 'that perm in user permission'
    except Exception as err:
        return str(err)


def del_permission(user_id, del_perm):
    try:
        cur = con.cursor()
        prop = check_admin_properties(user_id=user_id)
        if del_perm in prop:
            new_perm = prop.replace(del_perm, '')
            cur.execute(f"""UPDATE main_profiles SET admin_type = {new_perm} WHERE user_id = {user_id}""")
            con.commit()
            return 'done'
        else:
            return 'User has no such permission'
    except Exception as err:
        return str(err)
