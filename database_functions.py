import psycopg2
import config
import time
import datetime
import pytz
from help_func import sep_by_3 as sep3
from fuzzywuzzy import process

con = config.connect_with_database()


def get_now_time():
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    timee = now.strftime("%H:%M")
    return timee


def alarm(bot, message, error):
    bot.send_message(message.chat.id,
                     'Случилась ошибка, разработчик получил информацию')
    error_msg = str(error) + '\n\n' + str(error.__class__) + '\n' + str(error.__cause__) \
                + '\n\n' + str(message.from_user.id) + '\n@' + str(message.from_user.username) \
                + '\n\nТекст:\n"' + str(message.text) + '"\n\nЧат:\nid:' + str(message.chat.id) \
                + '\nНазвание:\n\t' + str(message.chat.title) + '\n\nВремя:\n\t' + str(get_now_time())
    bot.send_message(config.alarm, error_msg)


# class Equipment(object):
#
#     def __init__(self, hp, defense, ddg, cri, atk, exp, accu):
#         self.hp = hp
#         self.defense = defense
#         self.ddg = ddg
#         self.cri = cri
#         self.atk = atk
#         self.exp = exp
#         self.accu = accu
#
#     def parse_recipe(self):

def check_recipe(message, bot):
    try:
        # con = config.connect_with_database()
        s = str(message.text)
        # иконки в массиве: хп(0), деф(1), уворот(2), крит(3), атака(4), опыт(5), точность(6) -
        # такой порядок во всех массивах
        update_trigger = 0
        ic_arr = ['❤', '🛡', '💨', '🎯', '⚔', '🔮', '⏳']
        stat_name = ['hp', 'def', 'agi', 'cri', 'atk', 'exp', 'accu']
        icon_arr = []
        select = 'SELECT'
        for item in ic_arr:
            if item in s:
                icon_arr.append(item)
                select += f' {stat_name[ic_arr.index(item)]},'
        select = select[:len(select) - 1]
        count = len(icon_arr)
        val_arr = [0] * count
        name_v = s[s.find('рецепт'):s.find('\n')].replace('.', '')
        select += f" FROM armor WHERE name = '{name_v}'"
        cur = con.cursor()
        cur.execute(select)
        con.commit()
        bd_arr = cur.fetchone()
        # # cur.close()
        # print('*' + name_v + '*')
        str_arr = ['', '', '', '']
        if bd_arr is not None:
            for num in range(count):
                if icon_arr[num] in s:
                    str_tmp = s[s.find(icon_arr[num]):s.find('\n', s.find(icon_arr[num]))].replace('%', '')
                    val_arr[num] = str_tmp[str_tmp.find('+') + 1:]
                    # print(val_arr[num])
                    str_arr[0] = s[:s.find('\n', s.find(icon_arr[num]))]
                    str_arr[2] = s[s.find('\n', s.find(icon_arr[num])):]
                    # Artem подправил взятие текста если попадаем в конец рецепта
                    if len(s) - len(str_arr[0]) <= 2:
                        str_arr[0] = s
                        str_arr[2] = ''
                        str_tmp = s[s.find(icon_arr[num]):].replace('%', '')
                        val_arr[num] = str_tmp[str_tmp.find('+') + 1:]
                    if icon_arr[num] in ['⏳', '💨', '🔮', '🎯']:
                        if round(float(bd_arr[num]), 2) >= round(float(val_arr[num]), 2):
                            delta = round(round(float(val_arr[num]), 2) - round(float(bd_arr[num]), 2), 2)
                            str_arr[1] = ' (' + str(bd_arr[num]) + ') Δ: ' + str(delta)
                        else:
                            delta = round(round(float(val_arr[num]), 2) - round(float(bd_arr[num]), 2), 2)
                            str_arr[1] = ' (' + str(bd_arr[num]) + ') Δ: ' + str(delta) + ' ⭐'
                            cur = con.cursor()
                            update_trigger = 1
                            postgres_insert_query = ''
                            if icon_arr[num] == '💨':
                                postgres_insert_query = """ update armor SET agi = %s where name = %s"""
                            elif icon_arr[num] == '🔮':
                                postgres_insert_query = """ update armor SET exp = %s where name = %s"""
                            elif icon_arr[num] == '🎯':
                                postgres_insert_query = """ update armor SET cri = %s where name = %s"""
                            elif icon_arr[num] == '⏳':
                                postgres_insert_query = """ update armor SET accu = %s where name = %s"""
                            record_to_insert = (round(float(val_arr[num]), 2), name_v)
                            cur.execute(postgres_insert_query, record_to_insert)
                            con.commit()
                            # # cur.close()
                    else:
                        if int(bd_arr[num]) >= int(val_arr[num]):
                            delta = int(val_arr[num]) - int(bd_arr[num])
                            str_arr[1] = ' (' + str(bd_arr[num]) + ') Δ: ' + str(delta)
                        else:
                            delta = int(val_arr[num]) - int(bd_arr[num])
                            str_arr[1] = ' (' + str(bd_arr[num]) + ') Δ: ' + str(delta) + ' ⭐'
                            cur = con.cursor()
                            if icon_arr[num] == '❤':
                                postgres_insert_query = """ update armor SET hp = %s where name = %s"""
                            elif icon_arr[num] == '🛡':
                                postgres_insert_query = """ update armor SET def = %s where name = %s"""
                            elif icon_arr[num] == '⚔':
                                postgres_insert_query = """ update armor SET atk = %s where name = %s"""
                            record_to_insert = (int(val_arr[num]), name_v)
                            cur.execute(postgres_insert_query, record_to_insert)
                            con.commit()
                            # # cur.close()
                    s = str_arr[0] + str_arr[1] + str_arr[2]
            s = '@' + str(message.from_user.username) + ' прислал: \n\n' + s
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, s)
            if update_trigger == 1:
                try:
                    bot.send_message(689134160, s)
                except:
                    pass
        else:
            for num in range(len(icon_arr)):
                if s.find(icon_arr[num]) != -1:
                    str_tmp = s[s.find(icon_arr[num]):s.find('\n', s.find(icon_arr[num]))].replace('%', '')
                    val_arr[num] = str_tmp[str_tmp.find('+') + 1:]
            cur = con.cursor()
            msg = message.text
            left = msg.find('уровень:'.lower()) + len('уровень: ')
            item_lvl = 0
            if left != -1:
                item_lvl = msg[left:msg.find('\n', left)]
            else:
                item_lvl = 99

            postgres_insert_row_name_query = 'INSERT INTO armor (name, lvl'
            postgres_insert_values_query = f"VALUES ('{name_v}', {int(item_lvl)}"
            for i in range(len(icon_arr)):
                postgres_insert_row_name_query += f', {stat_name[ic_arr.index(icon_arr[i])]}'
                postgres_insert_values_query += f', {val_arr[i]}'
            postgres_insert_row_name_query += ') '
            postgres_insert_values_query += ')'

            # postgres_insert_query = """INSERT INTO armor (name, lvl, hp, def, agi, cri, atk, exp, accu) VALUES
            #  (%s,%s,%s,%s,%s,%s,%s,%s, %s)"""
            # record_to_insert = (
            #     name_v, int(item_lvl), int(val_arr[0]), int(val_arr[1]), float(val_arr[2]), float(val_arr[3]),
            #     int(val_arr[4]),
            #     float(val_arr[5]), float(val_arr[6]))
            insert_query = postgres_insert_row_name_query + postgres_insert_values_query
            cur.execute(insert_query)
            con.commit()
            # # cur.close()
            bot.reply_to(message, 'О, новенький рецепт! Схоронил')
            msg = f'Новый рецепт от @{message.from_user.username}\n\n' + msg
            bot.send_message(689134160, msg)
    except Exception as error:
        alarm(bot, message, error)


def get_recipe(message, bot, find_name):
    find_name = str(find_name).lower()
    if 'рецепт' not in find_name:
        find_name = 'рецепт ' + find_name
    # con = config.connect_with_database()
    icon_arr = ['❤', '🛡', '💨', '🎯', '⚔', '🔮', '⏳']
    cur = con.cursor()
    cur.execute('SELECT name FROM armor')
    recipes_name_arr = cur.fetchall()

    a = process.extractOne(find_name, recipes_name_arr)
    cur.execute(f"SELECT * FROM armor WHERE name = '{a[0][0]}'")
    recipes_arr = cur.fetchone()
    # # cur.close()
    return_msg = 'Максимальные статы для' + recipes_arr[0][str(recipes_arr[0]).find('Рецепт') + len('Рецепт') + 1:len(
        str(recipes_arr[0]))] + ':\n'
    if recipes_arr is not None:
        for i in range(len(icon_arr)):
            if recipes_arr[i + 2] != 0:
                return_msg = return_msg + str(icon_arr[i]) + str(recipes_arr[i + 2]) + '\n'
    bot.send_message(message.chat.id, return_msg)


def ping_command(message, bot):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(""" SELECT chat_id FROM chat_id_list WHERE chat_id = '{0}'""".format(str(message.chat.id)))
        bd_arr = cur.fetchone()
        # # cur.close()
        if bd_arr is None:
            bot.send_message(message.chat.id,
                             'Для доступа к функциям бота обратитесь к @NeverAndFear или @Ugadai_s_3_raz')
        else:
            new_msg = ''
            list_of_ping = ''
            for i in range(len('/ping_all'), len(str(message.text))):
                new_msg += str(message.text)[i]
            if new_msg.find('@Consta_bot') != -1:
                new_msg = new_msg.replace('@Consta_bot', ' ')
            cur = con.cursor()
            cur.execute(""" SELECT login FROM ping_player WHERE chat_id = '{0}'""".format(str(message.chat.id)))
            bd_arr = cur.fetchall()
            # # cur.close()
            flag_count = 0
            for num in range(len(bd_arr)):
                if list_of_ping != '':
                    list_of_ping = list_of_ping + '\n'
                list_of_ping = list_of_ping + '@' + str(bd_arr[num][0])
                flag_count = flag_count + 1
                if flag_count == 3:
                    bot.send_message(message.chat.id, new_msg + '\n' + list_of_ping, disable_notification=None)
                    flag_count = 0
                    list_of_ping = ''
            if flag_count != 0:
                bot.send_message(message.chat.id, new_msg + '\n' + list_of_ping, disable_notification=None)
    except Exception as error:
        alarm(bot, message, error)


def add_command(message, bot):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(""" SELECT chat_id FROM chat_id_list WHERE chat_id = '{0}'""".format(str(message.chat.id)))
        bd_arr = cur.fetchone()
        # # cur.close()
        if bd_arr is None and message.from_user.id != 374085219:
            bot.send_message(message.chat.id,
                             'Для доступа к функциям бота обратитесь к @NeverAndFear или @Ugadai_s_3_raz')
        else:
            cur = con.cursor()
            postgres_select_query = """ SELECT * FROM ping_player WHERE chat_id = %s and login = %s"""
            select_options = (str(message.chat.id), message.from_user.username)
            cur.execute(postgres_select_query, select_options)
            bd_arr = cur.fetchone()
            # # cur.close()
            if bd_arr is None:
                cur = con.cursor()
                postgres_insert_query = """ INSERT INTO ping_player (chat_id, login) VALUES (%s,%s)"""
                insert_options = (str(message.chat.id), message.from_user.username)
                cur.execute(postgres_insert_query, insert_options)
                con.commit()
                # # cur.close()
                bot.reply_to(message, 'Ты добавлен в список /ping_all в данном чате!')
            else:
                bot.reply_to(message, 'Ты уже есть в списке /ping_all в данном чате!')
    except Exception as error:
        alarm(bot, message, error)


def del_command(message, bot):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(""" SELECT chat_id FROM chat_id_list WHERE chat_id = '{0}'""".format(str(message.chat.id)))
        bd_arr = cur.fetchone()
        # # cur.close()
        if bd_arr is None:
            bot.send_message(message.chat.id,
                             'Для доступа к функциям бота обратитесь к @NeverAndFear или @Ugadai_s_3_raz')
        else:
            cur = con.cursor()
            postgres_select_query = """ SELECT * FROM ping_player WHERE chat_id = %s and login = %s"""
            select_options = (str(message.chat.id), message.from_user.username)
            cur.execute(postgres_select_query, select_options)
            bd_arr = cur.fetchone()
            # # cur.close()
            if bd_arr is None:
                bot.reply_to(message, 'Тебя и так нет в списке /ping_all в данном чате!')
            else:
                cur = con.cursor()
                postgres_del_query = """ DELETE FROM ping_player WHERE chat_id = %s and login = %s"""
                del_options = (str(message.chat.id), message.from_user.username)
                cur.execute(postgres_del_query, del_options)
                con.commit()
                # # cur.close()
                bot.reply_to(message, 'Ты удалён из списка /ping_all в данном чате!')
    except Exception as error:
        alarm(bot, message, error)


def add_chat_command(message, bot, chat_for_adding):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(""" SELECT chat_id FROM chat_id_list WHERE chat_id = '{0}'""".format(str(chat_for_adding)))
        bd_arr = cur.fetchone()
        # # cur.close()
        print(bd_arr)
        if bd_arr is None:
            cur = con.cursor()
            cur.execute(""" INSERT INTO chat_id_list (chat_id) VALUES ('{0}')""".format(str(chat_for_adding)))
            con.commit()
            # # cur.close()
            bot.reply_to(message, 'Чат добавлен в список разрешенных к использованию ConstaBot!')
        else:
            bot.reply_to(message, 'Чат уже давно добавлен в список разрешенных к использованию ConstaBot!')
    except Exception as error:
        alarm(bot, message, error)


def del_chat_command(message, bot, chat_id_for_delete):
    # con = config.connect_with_database()
    cur = con.cursor()
    cur.execute(""" DELETE FROM chat_id_list WHERE chat_id = '{0}'""".format(str(chat_id_for_delete)))
    con.commit()
    # # cur.close()
    bot.send_message(message.chat.id, str(chat_id_for_delete) + ' ID чата удален из списка рарешенных')


def check_is_user_in_allowed(message, bot, check_user_id):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(""" SELECT chat_id FROM chat_id_list WHERE chat_id = '{0}'""".format(str(check_user_id)))
        bd_arr = cur.fetchone()
        # # cur.close()
        if bd_arr is not None:
            return True
        else:
            bot.send_message(message.chat.id,
                             'У Вас недостаточно прав, обратитесь к @ugadai_s_3_raz'
                             ' или отправляйте сообщения в чаты где это разрешено')
            alert_msg = '@{}, рвется юзать бота {} UTC +0 в чате {} "{}" \n'.format(str(message.from_user.username),
                                                                                    time.strftime('%H:%M:%S'),
                                                                                    message.chat.id,
                                                                                    message.chat.title)
            alert_msg += '"' + str(message.text) + '"\n' + "name - " + str(
                message.from_user.first_name) + ' \nlast name - ' + str(message.from_user.last_name)
            bot.send_message(374085219, alert_msg)
            return False
    except Exception as error:
        alarm(bot, message, error)


def get_all_allowed_users():
    # con = config.connect_with_database()
    cur = con.cursor()
    cur.execute(""" SELECT * FROM chat_id_list""")
    bd_arr = cur.fetchall()
    # # cur.close()
    return bd_arr


def make_lower_recipes():
    # con = config.connect_with_database()
    cur = con.cursor()
    cur.execute(""" SELECT name FROM armor""")
    bd_arr = cur.fetchall()
    new_bd_arr = []
    # # cur.close()
    # con = config.connect_with_database()
    for i in range(len(bd_arr)):
        new_bd_arr.append(str(bd_arr[i][0].lower()))
        insert_options = (str(new_bd_arr[i]), str(bd_arr[i][0]))
        cur = con.cursor()
        postgres_insert_query = """ update armor set name = %s where name = %s"""
        cur.execute(postgres_insert_query, insert_options)
        con.commit()
    # # cur.close()


def send_totem_info(message, bot, totem_name, lvl, aden, bronze, silver, gold):
    try:
        totem_lvl = totem_name + '_lvl'
        totem_aden = totem_name + '_aden'
        totem_bronze = totem_name + '_bronze'
        totem_silver = totem_name + '_silver'
        totem_gold = totem_name + '_gold'
        user = str(message.from_user.id)
        # con = config.connect_with_database()
        cur = con.cursor()
        command = f"""SELECT {str(totem_lvl)} ,{str(totem_aden)}, {str(totem_bronze)}, {str(totem_silver)}, {str(
            totem_gold)}
         FROM players_totems WHERE user_id = '{user}';"""
        cur.execute(command)
        bd_array = cur.fetchone()
        con.commit()
        # # cur.close()
        user_id = 'user_id'

        if bd_array is None:
            # con = config.connect_with_database()
            cur = con.cursor()
            first = """INSERT INTO players_totems ({}, {}, {}, {}, {}, {})""".format(
                user_id, totem_lvl, totem_aden, totem_bronze, totem_silver, totem_gold, )
            # postgres_insert_query = str(first) +
            # values_to_record =
            second = """VALUES (%s, %s, %s, %s, %s, %s)"""
            all_part = str(first) + str(second)
            record_to_insert = (str(user), int(lvl), int(aden), int(bronze), int(silver), int(gold))
            cur.execute(all_part, record_to_insert)
            con.commit()
            # # cur.close()
        else:
            postgres_insert_query = f"""UPDATE players_totems SET {totem_lvl} = %s, {totem_aden} = %s,
             {totem_bronze} = %s, {totem_silver} = %s, {totem_gold} = %s WHERE user_id = '{user}'"""
            record_to_insert = (int(lvl), int(aden), int(bronze), int(silver), int(gold))
            # con = config.connect_with_database()
            cur = con.cursor()
            cur.execute(postgres_insert_query, record_to_insert)
            con.commit()
            # # cur.close()
        bot.reply_to(message, "Тотем обновлен, сообщение можно удалять. "
                              "Получение информации по тотемам возможно командой /totem или /totems для краткой инфы")

    except Exception as error:
        alarm(bot, message, error)


def add_totem(lvl, aden, bronze, silver, gold):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute("""SELECT * FROM required_totems WHERE totem_lvl = %s""", (str(lvl),))
        db_array = cur.fetchone()
        con.commit()
        # # cur.close()
        if db_array is not None:
            # con = config.connect_with_database()
            cur = con.cursor()
            cur.execute("""UPDATE required_totems SET totem_aden = %s, totem_bronze = %s,
             totem_silver = %s, totem_gold = %s WHERE totem_lvl = %s""", (aden, bronze, silver, gold, str(lvl),))
            con.commit()
            # # cur.close()
        else:
            # con = config.connect_with_database()
            cur = con.cursor()
            cur.execute("""INSERT INTO required_totems (totem_lvl, totem_aden, totem_bronze,
             totem_silver, totem_gold) VALUES (%s, %s, %s, %s, %s)""", (lvl, aden, bronze, silver, gold,))
            con.commit()
            # # cur.close()
    except Exception as error:
        print(error)


def totems_lvl_view(user_id):
    cur = con.cursor()

    cur.execute(
        f"""SELECT atk_lvl, def_lvl, accu_lvl, ddg_lvl, cri_lvl, hp_lvl FROM players_totems WHERE user_id = '{user_id}'""")
    db_array = cur.fetchone()
    icons = ['Тотем 🗡Ареса:', 'Тотем 🌊Посейдона:', 'Тотем ⏳Деймоса:', 'Тотем 💪🏼Гефеста:', 'Тотем ⚡️Зевса:',
             'Тотем ☄️Кроноса:']
    return_msg = ''
    if db_array is not None:
        for i in range(len(db_array)):
            return_msg += f'{icons[i]} {db_array[i]} lvl\n'
    else:
        return_msg = 'Может сначала тотемы скинешь? То совсем как-то никак...'
    return return_msg


def totems_main(bot, message):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM players_totems WHERE user_id = '{message.from_user.id}'""")
        db_array = cur.fetchone()
        con.commit()
        # # con.close()
        x = [1, 6, 11, 16, 21, 26]
        icons = ['\nТотем 🗡Ареса', '\nТотем 🌊Посейдона', '\nТотем 💪🏼Гефеста', '\nТотем ⚡️Зевса',
                 '\nТотем ☄️Кроноса', '\nТотем ⏳Деймоса']
        items = ['🏵', '🥉', '🥈', '🥇']
        if db_array is not None:
            full = [0] * len(items)
            full_msg = f'Информация по тотемам для игрока @{message.from_user.username}\n'
            for i in range(len(x)):
                if db_array[x[i]] is not None and db_array[x[i]] != 10:
                    # con = config.connect_with_database()
                    cur = con.cursor()
                    cur.execute("""SELECT * FROM required_totems WHERE totem_lvl = %s""",
                                (str(int(db_array[x[i]] + 1)),))
                    need_array = cur.fetchone()
                    con.commit()
                    # # con.close()

                    full_msg = full_msg + icons[i] + f' {db_array[x[i]]} -> {db_array[x[i]] + 1}:\n'
                    for j in range(4):
                        if need_array[j + 1] - db_array[x[i] + j + 1] >= 0:
                            count = f'{items[j]}{sep3(str(need_array[j + 1] - db_array[x[i] + j + 1]))} '
                            full[j] = full[j] + (need_array[j + 1] - db_array[x[i] + j + 1])
                            full_msg = full_msg + count
                            if j == 0 or j == 4:
                                full_msg += '\n'
                        else:
                            count = f'{items[j]} - 0 \n'
                            full_msg = full_msg + count
                    full_msg += '\n'
                elif db_array[x[i]] == 10:
                    full_msg += f'{icons[i]} - 10✨\nНичего не требуется😉\n\n'
                else:
                    full_msg += f'{icons[i]} - None\n\n'
            full_msg += '\nВсего надо:\n'
            for k in range(len(full)):
                full_msg = full_msg + f'{items[k]} {sep3(str(full[k]))}'
                if k == 0 or k == 4:
                    full_msg += '\n'
            bot.send_message(message.chat.id, full_msg)
        else:
            bot.reply_to(message, f'@{message.from_user.username}, '
                                  f'Тебе необходимо сначала переслать сообщения про свои тотемы!!!')
    except Exception as error:
        alarm(bot, message, error)


def get_update_interval(user_id):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT last_update_time FROM profiles WHERE user_id = {user_id}""")
        db = cur.fetchone()
        cur.execute("""SELECT now()::timestamp""")
        last_date = datetime.datetime(db[0].year, db[0].month, db[0].day, db[0].hour, db[0].minute, db[0].second)
        now = cur.fetchone()
        now_time = datetime.datetime(now[0].year, now[0].month, now[0].day, now[0].hour, now[0].minute, now[0].second)
        # # con.close()
        interval = (now_time - last_date)
        sec = interval.seconds
        hour = sec // 3600
        sec -= hour * 3600
        mins = sec // 60
        sec -= mins * 60
        if hour in [1, 21]:
            hour_name_ru = 'час'
        elif hour in [2, 3, 4, 22, 23, 24]:
            hour_name_ru = 'часа'
        else:
            hour_name_ru = 'часов'
        if mins in [1, 21, 31, 41, 51]:
            mins_name_ru = 'минута'
        elif mins in [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54]:
            mins_name_ru = 'минуты'
        else:
            mins_name_ru = 'минут'
        icon = ["дней ", f"{hour_name_ru} ", f"{mins_name_ru} ", "секунд "]
        a = [interval.days, hour, mins, sec]
        new_interval = '\nС последнего обновления прошло:\n'
        for i in range(len(a)):
            if a[i] != 0:
                new_interval += f'{a[i]} {icon[i]}'
        return new_interval
    except Exception as error:
        print(error)


def save_profiles(user_id: int, username: str, hp: int, lvl: int, pvp: int, exp: float, credits: int, aden: int,
                  atk: int, defense: int, cri: float, ddg: float, accu: float, prem, prem_duration, abu, abu_duration):
    try:
        # player = namedtuple('player',
        #                     'user_id, username, hp, lvl, pvp, exp, credits, aden, atk, defense, cri, ddg, accu')
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT user_id, username, hp, lvl, pvp, exp, credits, aden, atk, def,
         cri, ddg, accu FROM profiles WHERE user_id = {user_id}""")
        bd_arr = cur.fetchone()
        con.commit()
        if bd_arr is None:
            cur.execute(f"""INSERT INTO profiles
             (user_id, username, hp, lvl, pvp, exp, credits, aden, atk, def, cri, ddg, accu, prem,
              prem_duration, abu, abu_duration, last_update_time) VALUES 
             ({user_id}, '{username}', {hp},{lvl}, {pvp},{exp}, {credits}, {aden}, {atk}, {defense}, {cri}, {ddg},
                {accu}, {prem}, '{prem_duration}', {abu}, '{abu_duration}', now())""")
            msg = '\nСхоронил!'
            con.commit()
            # # cur.close()
            return msg

        # user_id[0], username[1], hp[2], lvl[3], pvp[4], exp[5], credits[6], aden[7], atk[8], def[9], cri[10], ddg[11],
        # accu[12], last_update_time[13]

        # user_id: int, username: str, hp: int, lvl: int, pvp: int, exp: float, credits: int, aden: int,
        # atk: int, defense: int, cri: float, ddg: float, accu: float
        else:
            msg = '\nПрофиль обновлен\n'
            icons = ['id', 'Ник', '❤️Здоровье', '🏅Уровень', '👊🏻PVP', '🌕Опыт', '💰Кредиты', '🏵Адена', '⚔Атака',
                     '🛡Защита', '🎯Крит', '💨Уворот', '⏳Меткость']
            stats_str = ['user_id', 'username', 'hp', 'lvl', 'pvp', 'exp', 'credits', 'aden', 'atk', 'def', 'cri',
                         'ddg', 'accu']
            stats = [user_id, username, hp, lvl, pvp, exp, credits, aden, atk, defense, cri, ddg, accu]
            updt = ''
            for i in range(len(stats)):
                if stats[i] != bd_arr[i]:
                    if bd_arr[i] is not None:
                        if i in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                            updt += f'{stats_str[i]} = {stats[i]}, '
                            if i in [10, 11, 12]:
                                if stats[i] > bd_arr[i]:
                                    msg += f'\n{icons[i]}: +{round(stats[i] - bd_arr[i], 2)}'
                                else:
                                    msg += f'\n{icons[i]}: -{round(bd_arr[i] - stats[i], 2)}'
                            else:
                                if stats[i] > bd_arr[i]:
                                    val_str = stats[i] - bd_arr[i]
                                    val_str = str(val_str)
                                    msg += f'\n{icons[i]}: +{sep3(val_str)}'
                                else:
                                    val_str = bd_arr[i] - stats[i]
                                    val_str = str(val_str)
                                    msg += f'\n{icons[i]}: -{sep3(val_str)}'
                        elif i == 1:
                            update_name = f"""UPDATE profiles SET username = '{stats[i]}' 
                                           WHERE user_id = {user_id}; """
                            cur.execute(update_name)
                            msg += f"\n{icons[i]} обновлен на: {stats[i]}"
                    else:
                        updt += f'{stats_str[i]} = {stats[i]}, '
                        if i in [10, 11, 12]:
                            msg += f"\n{icons[i]}: {round(stats[i], 3)}"
                        else:
                            msg += f"\n{icons[i]}: {sep3(stats[i])}"
            updt += f"prem = {prem}, prem_duration = '{prem_duration}', abu = {abu}, abu_duration = " \
                    f"'{abu_duration}'," \
                    f" last_update_time = now()"
            msg += get_update_interval(user_id)
            update_str = f"""UPDATE profiles SET {updt} WHERE user_id = {user_id};"""
            cur.execute(update_str)
            con.commit()
            # # cur.close()
            return msg
    except Exception as err:
        print(err)
        pass


# тотемы: Арес - atk, Посейдон - def, Гефест - ddg, Зевс - cri, Кронос - hp
# (табла:players_totems:: user_id, ***_lvl, ***_aden, ***_bronze, ***_silver, ***_gold)
# (табла:required_totems::  ***_lvl, ***_aden, ***_bronze, ***_silver, ***_gold)
# (табла: profiles:: user_id, username, hp, lvl, pvp, exp, credits, atk, def,
#                    cri, ddg, win, loose, rates, last_update_time)
# Табла mobs (
#                  mobname TEXT,
#                  hp INT,
#                  lvl INT,
#                  atk INT,
#                  def INT,
#                  cri REAL,
#                  ddg REAL,
#                  accu REAL)


def make_database(message, bot):
    command = ("""CREATE TABLE mobs (
                 mobname TEXT,
                 hp INT,
                 lvl INT,
                 atk INT,
                 def INT,
                 cri REAL,
                 ddg REAL,
                 accu REAL)
                 """)
    con = None
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(command)
        # # cur.close()
        # con.commit()
        bot.send_message(message.chat.id, 'created')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        bot.send_message(message.chat.id, error)
    finally:
        if con is not None:
            # # con.close()
            bot.send_message(message.chat.id, 'already created')


def edit_recipe(bot, message, name_res):
    try:
        pass
        # con = config.connect_with_database()
        cur = con.cursor()
        name_res = 'рецепт ' + name_res
        command = f"""SELECT * FROM armor WHERE name = '{name_res}' """
        cur.execute(command)
        bd_arr = cur.fetchone
        con.commit()
        # # cur.close()
        if bd_arr is None:
            bot.reply_to(message, 'Ошибка! Укажи другое название рецепта!')
        else:
            s = message.text
            icon_arr = ['❤', '🛡', '💨', '🎯', '⚔', '🔮']
            count = len(icon_arr)
            str_arr = ['', '', '']
            val_arr = [0] * count
            for num in range(count):
                if s.find(icon_arr[num]) != -1:
                    str_tmp = s[s.find(icon_arr[num]):s.find('\n', s.find(icon_arr[num]))].replace('%', '')
                    val_arr[num] = str_tmp[str_tmp.find('+') + 1:]
                    # print(val_arr[num])
                    str_arr[0] = s[:s.find('\n', s.find(icon_arr[num]))]
                    str_arr[2] = s[s.find('\n', s.find(icon_arr[num])):]
                    if len(s) - len(str_arr[0]) <= 2:
                        str_arr[0] = s
                        str_arr[2] = ''
                        str_tmp = s[s.find(icon_arr[num]):].replace('%', '')
                        val_arr[num] = str_tmp[str_tmp.find('+') + 1:]
                    if num == 2 or num == 3 or num == 5:
                        cur = con.cursor()
                        if num == 2:
                            postgres_insert_query = """ update armor set agi = %s where name = %s"""
                        elif num == 5:
                            postgres_insert_query = """ update armor set exp = %s where name = %s"""
                        else:
                            postgres_insert_query = """ update armor set cri = %s where name = %s"""
                        record_to_insert = (round(float(val_arr[num]), 2), name_res)
                        # con = config.connect_with_database()
                        cur = con.cursor()
                        cur.execute(postgres_insert_query, record_to_insert)
                        con.commit()
                        # # cur.close()
                    else:
                        if num == 0:
                            postgres_insert_query = """ update armor set hp = %s where name = %s"""
                        elif num == 1:
                            postgres_insert_query = """ update armor set def = %s where name = %s"""
                        else:
                            postgres_insert_query = """ update armor set atk = %s where name = %s"""
                        # con = config.connect_with_database()
                        cur = con.cursor()
                        record_to_insert = (int(val_arr[num]), name_res)
                        cur.execute(postgres_insert_query, record_to_insert)
                        con.commit()
                        # cur.close()
            users = [config.roman, config.legolas]
            for item in users:
                bot.send_message(item, f'Обновлен рецепт {name_res}, я очень надеюсь, что все ок')

    except Exception as error:
        alarm(bot, message, error)


def add_collumn(bot, message):
    command = ("""CREATE TABLE profiles (
                 user_id SMALLINT,
                 username TEXT,
                 hp REAL,
                 lvl REAL,
                 pvp INT,
                 exp REAL,
                 credits INT,
                 atk SMALLINT,
                 def SMALLINT,
                 cri REAL,
                 ddg REAL,
                 win INT,
                 loose INT,
                 rates SMALLINT,
                 last_update_time TIME,
                 last_update_day DATE,
                )""")
    con = None
    second = ["""ALTER COLUMN atk_lvl DROP NOT NULL;""",
              """ALTER COLUMN atk_aden DROP NOT NULL;""",
              """ALTER COLUMN atk_bronze DROP NOT NULL;""",
              """ALTER COLUMN atk_silver DROP NOT NULL;""",
              """ALTER COLUMN atk_gold DROP NOT NULL;""",
              """ALTER COLUMN def_lvl DROP NOT NULL;""",
              """ALTER COLUMN def_aden DROP NOT NULL;""",
              """ALTER COLUMN def_bronze DROP NOT NULL;""",
              """ALTER COLUMN def_silver DROP NOT NULL;""",
              """ALTER COLUMN def_gold DROP NOT NULL;""",
              """ALTER COLUMN ddg_lvl DROP NOT NULL;""",
              """ALTER COLUMN ddg_aden DROP NOT NULL;""",
              """ALTER COLUMN ddg_bronze DROP NOT NULL;""",
              """ALTER COLUMN ddg_silver DROP NOT NULL;""",
              """ALTER COLUMN ddg_gold DROP NOT NULL;""",
              """ALTER COLUMN cri_lvl DROP NOT NULL;""",
              """ALTER COLUMN cri_aden DROP NOT NULL;""",
              """ALTER COLUMN cri_bronze DROP NOT NULL;""",
              """ALTER COLUMN cri_silver DROP NOT NULL;""",
              """ALTER COLUMN cri_gold DROP NOT NULL;""",
              """ALTER COLUMN hp_lvl DROP NOT NULL;""",
              """ALTER COLUMN hp_aden DROP NOT NULL;""",
              """ALTER COLUMN hp_bronze DROP NOT NULL;""",
              """ALTER COLUMN hp_silver DROP NOT NULL;""",
              """ALTER COLUMN hp_gold DROP NOT NULL;"""]
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(command)
        con.commit()
        # # cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        bot.send_message(message.chat.id, error)


def get_names(id1, id2):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT username FROM profiles WHERE user_id = {id1}""")
        name1 = cur.fetchone()
        cur.execute(f"""SELECT username FROM profiles WHERE user_id = {id2}""")
        name2 = cur.fetchone()
        # # cur.close()
        return name1, name2
    except:
        pass


def get_prof(username):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(
            f"""SELECT username, hp, atk, def, cri, ddg, lvl, win, loose, accu FROM profiles WHERE username
             = '{username}'""")
        player = cur.fetchone()
        # # cur.close()
        return player
    except:
        pass


def get_name(id):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT username FROM profiles WHERE user_id = {id}""")
        name1 = cur.fetchone()
        # # cur.close()
        return name1
    except:
        pass


def get_profile_by_id(id):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT username, hp, atk, def, cri, ddg, lvl, win, loose,
                     accu FROM profiles WHERE user_id = {id}""")
        name1 = cur.fetchone()
        # cur.close()
        return name1
    except:
        pass


# (табла: profiles:: user_id, username, hp, lvl, pvp, exp, credits, atk, def,
#                    cri, ddg, win, loose, rates, last_update_time, last_update_day)


def get_mob_by_lvl(lvl, type):
    if type is None:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT mobname, hp, atk, def, cri, ddg, lvl,
                     accu FROM mobs WHERE lvl= {lvl} AND mobname NOT LIKE '%Голем%'""")
        name1 = cur.fetchone()
        # cur.close()
    else:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT mobname, hp, atk, def, cri, ddg, lvl,
                     accu FROM mobs WHERE lvl= {lvl} AND mobname LIKE '%Голем%'""")
        name1 = cur.fetchone()
        # cur.close()
        if name1 is None:
            return None
    name1 = list(name1)
    name1.insert(7, 0)
    name1.insert(8, 0)
    return name1


def get_table(bot, message):
    try:
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM mobs""")
        name1 = cur.fetchall()
        pass
        # cur.execute("""DELETE FROM armor WHERE name=''""")
        # cur.close()
        con.commit()
        bot.send_message(message.chat.id, name1)
    except Exception as error:
        alarm(bot, message, error)


def parser(bot, message):
    txt = message.text
    hp = 0
    lvl = 0
    atk = 0
    ddef = 0
    cri = 0
    ddg = 0
    accu = 0.0
    mobname = ''
    left = 0
    i = 1
    while txt.find('🏅', left, len(txt)) != -1:
        left = txt.find(f'{i}) ', left) + len("1) ")
        mobname = txt[left:txt.find('🏅', left)]
        left = txt.find('🏅', left) + len('🏅')
        lvl = int(txt[left:txt.find('|❤️', left)])
        left = txt.find('|❤️', left) + len('|❤️')
        hp = int(txt[left:txt.find('|⚔️', left)])
        left = txt.find('|⚔️', left) + len('|⚔️')
        atk = int(txt[left:txt.find('|🛡', left)])
        left = txt.find('|🛡', left) + len('|🛡')
        ddef = int(txt[left:txt.find('|💨', left)])
        left = txt.find('|💨', left) + len('|💨')
        ddg = float(txt[left:txt.find('%|🎯', left)])
        left = txt.find('|🎯', left) + len('|🎯')
        cri = float(txt[left:txt.find('%|🌕', left)])
        i += 1
        # con = config.connect_with_database()
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM mobs WHERE mobname ='{mobname}'""")
        db_array = cur.fetchone()
        if db_array is None:
            cur.execute(f"""INSERT INTO mobs (mobname, hp, lvl, atk, def, cri, ddg, accu) VALUES ('{mobname}', {hp},
                        {lvl}, {atk}, {ddef}, {cri}, {ddg}, {accu})""")
        else:
            bot.send_message(message.chat.id, "Моб уже есть в базе")
        con.commit()
        # con.close()
    bot.send_message(message.chat.id, 'Added')


def get_list_of_players_bu_nickname(players: list):
    ids = []
    # con = config.connect_with_database()
    cur = con.cursor()
    for i in range(len(players)):
        if "'" in players[i] or '🧝‍♀' in players[i] or '👩‍🚀' in players[i] or '🤖' in players[i]:
            players[i] = players[i].replace("🧝‍♀", '', 1)
            players[i] = players[i].replace("👩‍🚀", '', 1)
            players[i] = players[i].replace("🤖", '', 1)
            players[i] = players[i].replace("'", '')
        cur.execute(f"""SELECT user_id FROM profiles WHERE username LIKE '{players[i]}'""")
        now_id = cur.fetchone()
        if now_id is not None:
            ids.append(now_id[0])
    # con.close()
    return ids


# def backpack_saver(bp, user_id, username):

# def check_and_run_tasks_from_db(bot):

# CREATE TABLE caves (lider_name TEXT, entry_datatime TIMESTAMP, end_shield_time TIMESTAMP)


def add_caves(txt: str):
    try:
        cur = con.cursor()
        left = txt.find('🚠Группа ') + len('🚠Группа ')
        left = txt.find('[', left)
        right = txt.find(' поднимается')
        lider_name = txt[left:right]
        left = txt.find('пещеры(')
        group_lvl = txt[left:txt.find(').')]
        if "'" in lider_name:
            lider_name = lider_name.replace("'", '')
        entry_datatime = datetime.datetime.now(tz=pytz.utc)
        cur.execute(f"""INSERT INTO caves (lider_name, entry_datatime) VALUES ('{lider_name}', '{entry_datatime}');""")
        con.commit()
    except Exception as error:
        print(error)


def set_shield(txt: str):
    try:
        cur = con.cursor()
        if 'победила группу ' in txt:
            left = txt.find('🏆Группа ') + len('🏆Группа ')
            left = txt.find('[', left)
            right = txt.find(' победила группу ')
            first_lider = txt[left:right]
            left = right + len(' победила группу ')
            left = txt.find('[', left)
            right = txt.find(' в пещере ')
            second_lider = txt[left:right]
        elif 'сразились в равном бою' in txt:
            left = txt.find('🤝Группы ') + len('🤝Группы ')
            left = txt.find('[', left)
            right = txt.find(' и ')
            first_lider = txt[left:right]
            left = right + len(' и ')
            left = txt.find('[', left)
            right = txt.find(' сразились в равном бою ')
            second_lider = txt[left:right]
        if "'" in first_lider:
            first_lider = first_lider.replace("'", '')
        elif "'" in second_lider:
            second_lider = second_lider.replace("'", '')

        cur.execute(f"""UPDATE caves SET end_shield_time = now() WHERE lider_name = '{first_lider}'""")
        cur.execute(f"""UPDATE caves SET end_shield_time = now() WHERE lider_name = '{second_lider}'""")
        con.commit()
    except:
        pass


def del_caves(txt: str):
    try:
        cur = con.cursor()
        left = txt.find('🚠Группа ')
        left = txt.find('[', left)
        right = txt.find(' спускается на фуникулере в ген. штаб')
        lider_name = txt[left:right]
        if "'" in lider_name:
            lider_name = lider_name.replace("'", '')
        cur.execute(f"""DELETE FROM caves WHERE lider_name = '{lider_name}'""")
        con.commit()
    except:
        pass


def cave_stats():
    try:
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM caves""")
        people = cur.fetchall()
        if len(people) > 0:
            msg = ''
            now = datetime.datetime.now()
            for i in range(len(people)):
                in_caves_time = now - people[i][1]
                in_caves_time = 'ч '.join(str(in_caves_time).split(':')[:2])
                in_caves_time += 'мин'
                if 'day' in in_caves_time or 'days' in in_caves_time:
                    in_caves_time = in_caves_time.replace('days', 'дней')
                    in_caves_time = in_caves_time.replace('day', 'день')

                msg += f"""{i + 1}) {people[i][0]} 🚠 {in_caves_time}"""
                if people[i][2] is not None:
                    pvp = people[i][2] + datetime.timedelta(minutes=8)
                    shield = pvp - now
                    shield_str = str(shield)
                    left = shield_str.find(':')
                    minutes_to_check = shield_str[left + 1:left + 3]
                    minutes_to_check = int(minutes_to_check)
                    if minutes_to_check <= 8:
                        shield = 'мин '.join(str(shield).split(':')[1:3])
                        shield = shield.split('.')[0] + 'сек'
                        msg += f""", 🛡 {shield}\n"""
                    else:
                        msg += '\n'
                else:
                    msg += '\n'
        else:
            msg = '👀В пещерах пусто и только ветер гоняет пустые банки🔋, оставшиеся от последней пати'
        return msg
    except Exception as error:
        print(error)


def send_res_to_db(res, user_id):
    try:
        cur = con.cursor()
        cur.execute(f"""SELECT * FROM resources WHERE user_id = {user_id}""")
        res_old = cur.fetchall()
        if len(res_old) == 0:
            for i in range(len(res[0])):
                cur.execute(f"""INSERT INTO resources (user_id, res_name, res_count) VALUES ({user_id}, '{res[0][i]}',
                                {res[1][i]});""")
        else:
            cur.execute(f"""DELETE FROM resources WHERE user_id = {user_id}""")
            con.commit()
            for i in range(len(res[0])):
                cur.execute(f"""INSERT INTO resources (user_id, res_name, res_count) VALUES ({user_id}, '{res[0][i]}',
                                {res[1][i]});""")
        con.commit()
        return 'Ресурсы обновлены'
    except:
        return "Произошла какая-то ошибка, прошу прощения"

# CREATE TABLE actions(
# # when_do timestamp,
# # chat_id INT,
# # action TEXT);
