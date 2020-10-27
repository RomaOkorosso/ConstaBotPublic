import telebot
import threading
from telebot import types
from random import randint
import datetime
import config
import database_functions
from help_func import sep_by_3
import pytz
import help_func
import duel_func
import bosses
from castle import generate_main_castle_msg, edit_castle_pin, fight_editor
import recipes_and_equip
import donate_func

roman = config.roman
artem = config.artem

# test
# bot = telebot.TeleBot(str(config.test), threaded=False, num_threads=3)

# main
bot = telebot.TeleBot(config.main, threaded=True, num_threads=2)

print('bot started')
con = config.connect_with_database()


# initialization ticker for actions from db table FOR NEXT UPDATES
# one_tick = int(0.5 * 60)
# cur = con.cursor()
# cur.execute(f"""SELECT * FROM actions WHERE when_do > now()- interval '5 D' AND when_do < current_date + integer '8'""")
# actions = cur.fetchall()


# CREATE TABLE actions(
# when_do timestamp,
# chat_id INT,
# action TEXT);


# def actions_seeker():
#     i = 0
#     pass
#     while datetime.datetime.now(tz=pytz.utc).replace(tzinfo=None) > actions[i][0]:
#         print('yes')
#         if i < len(actions):
#             i += 1
#     ticker = threading.Timer(one_tick, actions_seeker).start()
#     print(type(actions))
# actions_seeker()


def edit_pinned_message_id(mes_id):
    pinned_message_idi = mes_id
    return pinned_message_idi


def_chats = -1001412560727
pinned_message_id = 0


def find_message_id(pined_message):
    idi = str()
    i = 39
    while pined_message[i] != ',':
        idi = idi + pined_message[i]
        i += 1
    return idi


def get_now_time():
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    now_time = now.strftime("%H:%M")
    return now_time


bot.send_message(roman, f'bot started at {get_now_time()} OK)')

command_trigger_auction = 'Список выставленных предметов на аукцион'
command_trigger_pin_low_case = '.пин '
command_trigger_pin_up_case = '.Пин '
command_trigger_exp_to_lvl = "Раса:"
grace_trigger = '🎉🎉🎉Ты получил '
command_trigger_recipe = "📜 Рецепт "
send_pin_messages_trigger = '/send_pin_message_'


def set_chat_permissions(bott, chat_id, can_send_messages=True, can_send_media_messages=True, can_send_polls=True,
                         can_send_other_messages=True, can_add_web_page_previews=True, can_change_info=False,
                         can_invite_users=False, can_pin_messages=False):
    try:
        method_url = 'setChatPermissions'
        payload = {'chat_id': chat_id, 'permissions': {}}

        payload['permissions']['can_send_messages'] = can_send_messages

        if can_send_messages:
            payload['permissions']['can_send_media_messages'] = can_send_media_messages
            payload['permissions']['can_send_polls'] = can_send_polls
            payload['permissions']['can_send_other_messages'] = can_send_other_messages
            payload['permissions']['can_add_web_page_previews'] = can_add_web_page_previews
            payload['permissions']['can_change_info'] = can_change_info
            payload['permissions']['can_invite_users'] = can_invite_users
            payload['permissions']['can_pin_messages'] = can_pin_messages

        payload['permissions'] = telebot.apihelper.json.dumps(payload['permissions'])
        return telebot.apihelper._make_request(bott.token, method_url, params=payload, method='post')
    except:
        pass


# adding_in_list(user_list)
@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    bot.reply_to(message, "pls, use /help to get more info about me")


@bot.message_handler(commands=['pin_castle'])
def castle_pin(message):
    if message.chat.id != message.from_user.id and \
            database_functions.check_is_user_in_allowed(message, bot, message.from_user.id) is True:
        castle = ''
        txt = message.text
        if '🕌' in txt or '🏯' in txt or '🏰' in txt:
            castle = txt[len('/pin_castle ')::]
            # castle = txt[txt.find('в замок 🕌 ')+len('в замок 🕌 '):txt.find('🐾, прибудешь')]
        else:
            castle = str(txt[len('/pin_castle ')::])
            castle = castle[0].upper() + castle[1::]
            first_tier = '🕌 Нова 🕌 Мира 🕌 Антарес 🕌 Арэс 🕌 Фобос 🕌 Торн 🕌 Кастор 🕌 Алькор 🕌 Гром 🕌 Конкорд'
            second_tier = '🏯 Беллатрикс 🏯 Иерихон 🏯 Цефея 🏯 Супер нова'
            third_tier = '🏰 Альдебаран 🏰 Бетельгейзе'
            icon = None
            if castle in first_tier:
                icon = '🕌 '
            elif castle in second_tier:
                icon = '🏯 '
            elif castle in third_tier:
                icon = '🏰 '
            str(castle[0]).upper()
            castle = icon + castle
        bot.send_message(message.chat.id, castle)
        generate_main_castle_msg(bot, message, castle)


@bot.message_handler(commands=['info'])
def send_msg_info(message):
    bot.send_message(roman, message)
    if message.reply_to_message is not None:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(roman, message.reply_to_message.from_user.id)


@bot.message_handler(commands=['get_db'])
def send_msg_info(message):
    database_functions.get_table(bot, message)


@bot.message_handler(commands=['get_user'])
def send_msg(message):
    if message.from_user.id == roman:
        try:
            bot.send_message(roman, f'{message.from_user.id} {message.from_user.username}')
        except:
            pass


@bot.message_handler(commands=['com'])
def com(message):
    if message.from_user.id == roman:
        command = message.text[message.text.find('/com ') + len('/com '):]
        try:
            cur = con.cursor()
            cur.execute(f"""{command}""")
            con.commit()
            db_array = cur.fetchall()
            if db_array is not None:
                bot.send_message(roman, f'{db_array}')
            else:
                bot.send_message(roman, 'all ok')
        except Exception as err:
            bot.send_message(roman, f'{err}')


@bot.message_handler(commands=['fight', 'duel'])
def req_duel(message):
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if timedelta_between_realtime_and_msg_datetime < standard:
        try:
            if message.chat.id == -1001233128724 or message.from_user.id == roman or message.chat.id == -297144480 or \
                    message.chat.id == -1001210026441 or message.chat.id == -1001449649860 or \
                    message.chat.id == -1001442661069 or message.chat.id == -1001453883488:
                s = message.text
                count = 1
                if ' @' in s and '@@' in s:
                    count = int(s[s.find(' @') + len(' @'):s.find('@@')])
                    if count > 5 and message.from_user.id != roman:
                        count = 1

                duel_func.request_battle(bot, message, count)
        except:
            pass


@bot.message_handler(commands=['big_fight', 'big_duel'])
def req_duel(message):
    try:
        if message.chat.id == -1001233128724 or message.from_user.id == roman or message.chat.id == -297144480 or \
                message.chat.id == -1001210026441 or message.chat.id == -1001449649860 or \
                message.chat.id == -1001442661069:
            s = message.text
            count = 6
            if len(s) > len('/big_fight 0'):
                count = int(s[s.find(' ') + 1:])
                if count > 10000 and message.from_user.id != roman:
                    count = 100

            duel_func.request_battle(bot, message, count)
    except:
        pass


@bot.message_handler(commands=['donate'])
def donate(message):
    try:
        usr = message.from_user.id
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton('ЯндексДенюшки', url=f'https://money.yandex.ru/to/410019603804361?comment='
                                                              f'Пожертвование на развите бота от {usr}')
        markup.add(btn)
        bot.send_message(message.chat.id,
                         f'<b>Поддержать штаны и избавить от голодной смерти разработчика можно по этим'
                         f' ссылкам:\nИли напишите в лс, если другой способ предпочтительнее</b>',
                         parse_mode='HTML', disable_notification=True, disable_web_page_preview=True,
                         reply_markup=markup)
    except:
        pass


@bot.message_handler(commands=['mobf'])
def req_duel(message):
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if timedelta_between_realtime_and_msg_datetime < standard:
        try:
            if message.chat.id == -1001233128724 or message.from_user.id == roman or message.chat.id == -297144480 or \
                    message.chat.id == -1001210026441 or message.chat.id == message.from_user.id \
                    or message.chat.id == -1001449649860:
                txt = str(message.text)
                txt = txt.lower()
                count = 1
                left = txt.find(' ') + len(' ')
                if 'e' in txt or 'е' in txt:
                    mob_type = 'Голем'
                    if 'e' in txt:
                        mob_lvl = int(txt[left:txt.find('e')])  # EN
                        if len(txt) >= left + 7:
                            count = int(txt[txt.find('e') + len('e')::])
                    else:
                        mob_lvl = int(txt[left:txt.find('е')])  # RU
                        if len(txt) >= left + 7:
                            count = int(txt[txt.find('е') + len('е')::])
                else:
                    mob_type = None
                    mob_lvl = int(txt[left:left + 3])
                    if (mob_lvl > 55 or mob_lvl < 2) and mob_lvl != 60:
                        mob_lvl = 2
                    if len(txt) >= left + 5:
                        count = int(txt[left + 3::])
                if (count < 1 or count > 10000) and message.from_user.id != roman:
                    count = 1
                if count == 1:
                    bosses.mob_fight(bot, message, mob_lvl, message.from_user.id, mob_type)
                else:
                    bosses.mob_fight_more_1(bot, message, mob_lvl, message.from_user.id, mob_type, count)
        except:
            bot.send_message(message.chat.id, 'А теперь отправь нормальный запрос в форме\n'
                                              '"/mobf <лвл> <e> <кол-во симуляий>"\n'
                                              'Без <>, е - необходимо для этеровских мобовб,'
                                              'если кол-во симуляций не введено, то по умолчанию = 1,'
                                              'максимум симуляций 10 000; 2 ≤ лвл ≤ 55')


@bot.message_handler(commands=['mobf_n'])
def mob_non_stop(message):
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if timedelta_between_realtime_and_msg_datetime < standard:
        try:
            txt = message.text
            left = txt.find('mobf_n') + len('mobf_n')
            if 'e' in txt or 'е' in txt:
                mob_type = 'Голем'
                if 'e' in txt:
                    mob_lvl = int(txt[left:txt.find('e')])  # EN
                else:
                    mob_lvl = int(txt[left:txt.find('е')])  # RU
            else:
                mob_type = None
                mob_lvl = int(txt[left:left + 3])
                if mob_lvl > 55 or mob_lvl < 2:
                    mob_lvl = 2
            count = 10000
            bosses.mob_fight_more_1_without_heal(bot, message, mob_lvl, message.from_user.id, mob_type, count)
        except:
            pass


@bot.message_handler(commands=['send_sticker'])
def send_sticker(message):
    stiker_id = ''
    right = len('send_st') + len('send_st')
    if message.text.find('ConstaBot'.lower()) != -1:
        right = message.text.find(" ", right)
    for i in range(right, len(message.text)):
        stiker_id += message.text[i]
    try:
        bot.send_sticker(message.chat.id, stiker_id)
    except:
        bot.send_message(message.chat.id, 'Отправь нормальный ID стикера!!!')


@bot.message_handler(commands=['add_totem'])
def databse(message):
    if message.from_user.id == roman:
        count = ['lvl', 'aden', 'bronze', 'silver', 'gold']
        nums = [0] * len(count)
        msg = str(message.text)
        for i in range(len(count)):
            left = msg.find('@') + 1
            right = msg.find('@', left, len(msg))
            nums[i] = int(str(msg)[left:right])
            msg = msg[right:len(msg)]
        database_functions.add_totem(nums[0], nums[1], nums[2], nums[3], nums[4])
        bot.send_message(message.from_user.id, 'added')


@bot.message_handler(commands=['edit_recipe'])
def totem_main(message):
    if database_functions.check_is_user_in_allowed(message, bot, message.chat.id):
        if message.from_user.id == roman or message.from_user.id == config.legolas:
            s = message.text
            res_name = s[s.find('@') + 1:s.find('@@')]
            database_functions.edit_recipe(bot, message, res_name)


@bot.message_handler(commands=['ro', 'ro_chat', 'go_away', 'unro', 'unro_chat'])
def admin_commands(message):
    msg = message.text
    admins = bot.get_chat_administrators(message.chat.id)
    admins_list = ''
    for i in range(len(admins)):
        admins_list += str(admins[i].user.id)
        admins_list += ' '
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if (str(message.from_user.id) in admins_list or message.from_user.id == roman) and \
            timedelta_between_realtime_and_msg_datetime < standard:
        if '/ro ' in msg and message.reply_to_message is not None:
            if message.reply_to_message.from_user.id != roman:
                tme = randint(10, 666)
                tme = msg[msg.find('/ro ') + len('/ro '):]
                try:
                    tme = int(tme)
                except:
                    bot.send_message(message.chat.id, 'Надо указать время в минутах без буковак дальше',
                                     reply_to_message_id=message.message_id)
                user_to_ro = message.reply_to_message.from_user.id
                bot.restrict_chat_member(message.chat.id, user_to_ro, until_date=60 * tme, can_send_messages=False,
                                         can_send_media_messages=False, can_send_other_messages=False)
                bot.send_message(message.chat.id, f'на ближайшие {tme} минут этот пользователь вас не потревожит')
            else:
                bot.send_message(message.chat.id, 'Эх, а вот против создателя я не могу пойти =)')
        elif message.reply_to_message is None and '/ro ' in msg:
            bot.send_message(message.chat.id, 'Давай так, ты реплаем повторишь, а я сделаю вид, что ничего не видел😉',
                             reply_to_message_id=message.message_id)
        if '/unro' in msg and message.reply_to_message is not None:
            user_to_ro = message.reply_to_message.from_user.id
            bot.restrict_chat_member(message.chat.id, user_to_ro, can_send_messages=True,
                                     can_send_media_messages=True, can_send_other_messages=True)
            bot.send_message(message.chat.id, reply_to_message_id=message.reply_to_message.message_id,
                             text="Ты сваабоооден, словно птыца в небесах!")
            bot.send_message(message.chat.id, reply_to_message_id=message.message_id,
                             text='Он свободен, словно птыца в небесах!🌚')
        elif message.reply_to_message is None and '/unro ' in msg:
            bot.send_message(message.chat.id, 'Давай так, ты реплаем повторишь, а я сделаю вид, что ничего не видел😉',
                             reply_to_message_id=message.message_id)
        if '/ro_chat' in msg:
            action = 1
            if action == 1:
                frase = ['Захожу я в чат, а тут армяне в нарды играют, так давайте помолчим и не будем им мешать🤫',
                         '🤫Тссс, эфир!🤫', 'Шел воробей...ах, да простите...цыц!🤫']
                bot.send_message(message.chat.id, frase[randint(0, 2)])
                set_chat_permissions(bot, message.chat.id, can_send_messages=False, can_send_media_messages=False,
                                     can_send_polls=False, can_send_other_messages=False,
                                     can_add_web_page_previews=False,
                                     can_change_info=False, can_invite_users=False, can_pin_messages=False)
        if '/unro_chat' in msg:
            frase = ['Да будет срач!💁‍♂️', 'Если б мишки были пчелами, то они никогда и нипочем не сняли бы отсюда'
                                            ' ро!🐝',
                     'Ойфон или ондроид?🌚', 'Творог или творог?🌚'
                     ]
            bot.send_message(message.chat.id, frase[randint(0, len(frase) - 1)])
            set_chat_permissions(bot, message.chat.id)
        if '/go_away' in msg and message.reply_to_message is not None:
            user_to_ban = message.reply_to_message.from_user.id
            bot.send_message(message.chat.id, reply_to_message_id=message.reply_to_message.message_id,
                             text='Гуд бай, противный кожанный мешок!')
            bot.kick_chat_member(message.chat.id, user_to_ban)
            bot.send_message(message.chat.id, reply_to_message_id=message.message_id,
                             text='Я его кикинул, отпинал и унизил, можно захватить человечество?')


@bot.message_handler(commands=['totem', 'totems'])
def totem_main(message):
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if timedelta_between_realtime_and_msg_datetime < standard:
        if database_functions.check_is_user_in_allowed(message, bot, message.chat.id) and \
                '/totem@Consta_bot' == message.text or '/totem' == message.text:
            database_functions.totems_main(bot, message)
        elif '/totems' == message.text or '/totems@Consta_bot' == message.text:
            msg = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>\n'
            msg += database_functions.totems_lvl_view(message.from_user.id)
            bot.send_message(message.chat.id, msg, parse_mode="HTML")


@bot.message_handler(commands=['get_recipe'])
def add_chat(message):
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if timedelta_between_realtime_and_msg_datetime < standard and \
            database_functions.check_is_user_in_allowed(message, bot, message.chat.id):
        recipe_name = ''
        new_msg_text = message.text
        if str(new_msg_text).find('@Consta_bot') != -1:
            new_msg_text = message.text.replace('@Consta_bot', '')
        if str(new_msg_text).find('Рецепт') == -1:
            recipe_name = recipe_name + 'Рецепт '
        try:
            for i in range(new_msg_text.find('get_recipe') + len('get_recipe '), len(new_msg_text)):
                recipe_name += new_msg_text[i]
            # print(recipe_name)
            database_functions.get_recipe(message, bot, recipe_name)
        except:
            bot.send_message(message.chat.id,
                             'Необходимо задать название рецепта СТРОГО как в названии рецепта в игре!!!')


@bot.message_handler(commands=['get_set'])
def send_set(message):
    pass


@bot.message_handler(commands=['get_chat'])
def send_chat_info(message):
    if message.from_user.id == roman or message.from_user.id == artem:
        x = bot.get_chat(message.chat.id)
        bot.send_message(roman, x)


@bot.message_handler(commands=['add_collumn'])
def send_chat_info(message):
    if message.from_user.id == roman or message.from_user.id == artem:
        database_functions.add_collumn(bot, message)


@bot.message_handler(commands=['ping_all'])
def ping_all(message):
    x = bot.get_chat_member(message.chat.id, message.from_user.id)
    if (
            x.status == 'administrator' or x.status == 'creator' or message.from_user.id == roman or
            message.from_user.id == 395969254) and \
            database_functions.check_is_user_in_allowed(message, bot, message.chat.id):
        database_functions.ping_command(message, bot)


@bot.message_handler(commands=['send_all'])
def send_message_for_all(message):
    if message.from_user.id == roman or message.from_user.id == artem:
        text = message.text
        new_msg = text[text.find(' ') + 1:len(message.text)]
        all_users = database_functions.get_all_allowed_users()
        alert_id = ''
        alert = 0
        for i in range(len(all_users)):
            try:
                bot.send_message(all_users[i][0], new_msg)
            except:
                alert += 1
                alert_id += str(all_users[i][0]) + '\n'
                pass
        bot.send_message(roman, 'Отправил сообщения всем, ошибок: {}\n{}'.format(alert, alert_id))


@bot.message_handler(commands=['all_pin'])
def send_pin_for_all(message):
    if message.from_user.id == roman or message.from_user.id == artem:
        text = message.text
        new_msg = text[text.find(' ') + 1:len(message.text)]
        # new_msg[0] = str(new_msg[0]).replace(new_msg[0], new_msg[0].upper(), 1)
        all_users = database_functions.get_all_allowed_users()
        alert_id = ''
        alert = 0
        for i in range(len(all_users)):
            try:
                new_msg_json = bot.send_message(all_users[i][0], new_msg)
                new_chat = new_msg_json.chat.id
                new_msg_id = new_msg_json.message_id
                bot.pin_chat_message(new_chat, new_msg_id, False)
                # print(msg_id, new_msg_id)
            except:
                alert += 1
                alert_id += str(all_users[i][0]) + '\n'
                pass
        bot.send_message(roman, 'Отправил и закрепил сообщения всем, ошибок: {}\n{}'.format(alert, alert_id))


@bot.message_handler(commands=['add_ping'])
def add_ping(message):
    # if message.chat.id == -1001484947987:
    database_functions.add_command(message, bot)


@bot.message_handler(commands=['del_ping'])
def del_ping(message):
    # if message.chat.id == -1001484947987:
    database_functions.del_command(message, bot)


@bot.message_handler(commands=['add_chat'])
def add_chat(message):
    if message.from_user.id == artem or message.from_user.id == roman:
        if message.text == '/add_chat':
            database_functions.add_chat_command(message, bot, message.chat.id)
        else:
            chat_for_adding = message.text[str(message.text).find('add_chat') + len('add_chat '):len(message.text)]
            database_functions.add_chat_command(message, bot, chat_for_adding)


@bot.message_handler(commands=['del_chat'])
def del_chat(message):
    if message.from_user.id == roman or message.from_user.id == artem:
        if message.text == '/del_chat':
            database_functions.del_chat_command(message, bot, message.chat.id)
        else:
            chat_for_del = message.text[str(message.text).find('del_chat') + len('del_chat '):len(message.text)]
            database_functions.del_chat_command(message, bot, chat_for_del)


@bot.message_handler(commands=['add_p'])
def del_chat(message):
    if message.from_user.id == roman or message.from_user.id == artem:
        left = message.text.find('/add_p ') + len('/add_p ')
        if message.reply_to_message is not None:
            result = donate_func.add_permission(message.reply_to_message.user_id, message.text[left:len(message.text)])
        else:
            params = message.text.split(' ')
            result = donate_func.add_permission(params[1], params[2])
        bot.reply_to(message, result)


@bot.message_handler(commands=['del_p'])
def del_chat(message):
    if message.from_user.id == roman or message.from_user.id == artem:
        left = message.text.find('/del_p ') + len('/del_p ')
        if message.reply_to_message is not None:
            result = donate_func.del_permission(message.reply_to_message.user_id, message.text[left:len(message.text)])
        else:
            params = message.text.split(' ')
            result = donate_func.del_permission(params[1], params[2])
        bot.reply_to(message, result)


@bot.message_handler(commands=['help', 'p_info'])
def send_welcome_message(message):
    # print('@' + str(message.from_user.username), '/help')
    if '/help' in message.text or '/help@' in message.text:
        bot.reply_to(message, "U can find more info there: \n https://telegra.ph/Kak-polzovatsya-ConstaBot-11-03")
    if '/p_info' in message.text or 'p_info@' in message.text:
        bot.reply_to(message, "Чтобы составить полную таблицу мне надо знать граничные значения опыта, поэтому тыкай"
                              " в моего хозяина, он подскажет, если нужны какие-то значения")


@bot.message_handler(commands=['nowtime'])
def send_welcome_message(message):
    time = str(get_now_time())
    # print('@' + str(message.from_user.username), '/nowtime at', time)
    bot.reply_to(message, time)


@bot.message_handler(commands=['f', 'F'])
def send_f_message(message):
    bot.send_message(message.chat.id, '/F')


@bot.message_handler(commands=['cave_info'])
def send_caves_info(message):
    msg = database_functions.cave_stats()
    bot.send_message(message.chat.id, msg)


@bot.channel_post_handler(content_types=['text', 'post'])
def channel_post_worker(message):
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if timedelta_between_realtime_and_msg_datetime < standard:
        try:
            txt = message.text
            chat_to_check = -1001362165026
            bot.send_message(chat_to_check, message.text)
            if 'спускается на фуникулере в ген. штаб' in txt:
                database_functions.del_caves(txt)
            elif 'победила группу ' in txt or 'сразились в равном бою' in txt:
                database_functions.set_shield(txt)
            elif ' поднимается' in txt and '🚠Группа ' in txt:
                database_functions.add_caves(txt)
            return 0
        except:
            pass


@bot.message_handler(content_types=['text'])
def send_messages(message):
    now_time = datetime.datetime.now(tz=pytz.utc)
    now_time_from_msg = datetime.datetime.fromtimestamp(message.date, tz=pytz.utc)
    timedelta_between_realtime_and_msg_datetime = now_time - now_time_from_msg
    standard = datetime.timedelta(*[0, 0, 0, 0, 5, 0, 0])
    if timedelta_between_realtime_and_msg_datetime < standard:
        global chat_ida
        global pinned_user_message_id
        global message_bot_sent_id
        a = str(message.text)
        if ('+1 к энергии' in a or 'Ты направляешься в следующую пещеру🐾, прибудешь через 0 мин. 30 сек.' in a or
            'Ты направляешься в пещеры на фуникулере🐾, прибудешь через 1 мин. 0 сек.' in a) \
                and message.forward_from is not None:
            if message.forward_from.id == 577009581:
                prem_energy = 17.5 * 60
                not_prem_energy = 25 * 60
                # con = config.connect_with_database()
                cur = con.cursor()
                cur.execute(f"""SELECT prem FROM profiles WHERE user_id = {message.from_user.id}""")
                prem = cur.fetchone()
                # cur.close()
                msg = ''
                if 'Ты направляешься в следующую пещеру🐾, прибудешь через 0 мин. 30 сек.' in a or \
                        'Ты направляешься в пещеры на фуникулере🐾, прибудешь через 1 мин. 0 сек.' in a:
                    now_en = 4
                else:
                    sep_line = a.find('/')
                    now_en = a[sep_line - 1:sep_line]
                    now_en = int(now_en)
                command_str_ls = f'en_{message.from_user.id}_'
                command_str_chat = f'en_{message.chat.id}_'
                command_str = ''
                prem_energy_time = int((prem_energy - (message.date - message.forward_date)) // 60)
                not_prem_energy_time = float((not_prem_energy - (message.date - message.forward_date)) // 60)
                if prem is None and now_en != 5:
                    msg += f"Следующая энка через:\n🎗Прем{prem_energy_time} мин" \
                           f""" в 🕓{datetime.datetime.fromtimestamp(message.forward_date + prem_energy,
                                                                     tz=pytz.timezone('Europe/Moscow')).strftime(
                               "%H:%M:%S")}""" \
                           f"\nБез према {not_prem_energy_time}" \
                           f""" в 🕓{datetime.datetime.fromtimestamp(message.forward_date + not_prem_energy,
                                                                     tz=pytz.timezone('Europe/Moscow')).strftime(
                               "%H:%M:%S")}"""
                elif prem[0] is True and now_en != 5:
                    msg += f"Следующая энка через:\n{prem_energy_time} мин" \
                           f""" в 🕓{datetime.datetime.fromtimestamp(message.forward_date + prem_energy,
                                                                     tz=pytz.timezone('Europe/Moscow')).strftime(
                               "%H:%M:%S")}"""

                    energy_time = message.forward_date + prem_energy
                    command_str += f"prem_{now_en + 1}_{int(energy_time)}"
                elif prem[0] is False and now_en != 5:
                    msg += f"Следующая энка через:\n{not_prem_energy_time} мин" \
                           f""" в 🕓{datetime.datetime.fromtimestamp(message.forward_date + not_prem_energy,
                                                                     tz=pytz.timezone('Europe/Moscow')).strftime(
                               "%H:%M:%S")}"""
                    energy_time = message.forward_date + not_prem_energy
                    command_str += f"notprem_{now_en + 1}_{int(energy_time)}"
                    energy_time += prem_energy
                elif now_en == 5:
                    msg += 'У тебя полная энергия🔋'
                markup = types.InlineKeyboardMarkup()
                command_str_ls = command_str_ls + command_str
                command_str_chat = command_str_chat + command_str
                button1 = types.InlineKeyboardButton(text='Список энки в лс!', callback_data=f'{command_str_ls}')
                button2 = types.InlineKeyboardButton(text='Список энки в чат!', callback_data=f'{command_str_chat}')
                markup.add(button1, button2)
                if prem is not None:
                    bot.send_message(message.chat.id, msg, reply_to_message_id=message.message_id, reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, msg, reply_to_message_id=message.message_id)
                return 0

        # get totem info
        if message.text.find(
                'Чтобы восславить тотем этого бога - Вам нужно преподнести божеству') != 1 and \
                message.forward_from is not None:
            try:
                if message.forward_from.id == 577009581:
                    list_baff = ['Ареса', 'Посейдона', 'Гефеста', 'Зевса', 'Кроноса', 'Деймоса'], ['atk', 'def',
                                                                                                   'ddg', 'cri',
                                                                                                   'hp', 'accu']
                    for i in range(len(list_baff[0])):
                        if list_baff[0][i] in a:
                            totem_name = str(list_baff[0][i])
                    totem_name = str(list_baff[1][list_baff[0].index(totem_name)])
                    lvl, aden, bronze, silver, gold = help_func.finding_in_totem(a)
                    database_functions.send_totem_info(message, bot, totem_name, int(lvl), int(aden), int(bronze),
                                                       int(silver), int(gold))
                    return 0
            except:
                pass
        if "Ресурсы:\n" in message.text and message.forward_from is not None:
            if message.forward_from.id == 577009581:
                return_message = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>\n'
                bot.delete_message(message.chat.id, message.message_id)
                res = recipes_and_equip.send_resources(message.text)
                msg_new = database_functions.send_res_to_db(res, message.from_user.id)
                return_message = return_message + msg_new
                bot.send_message(message.chat.id, return_message, disable_web_page_preview=True, parse_mode='HTML')
                return 0

        if message.text == 'Сала Україні' or message.text == 'Сала Украине':
            bot.reply_to(message, 'Героям сала!')

        if message.text == 'Бот извинись' or message.text == 'Бот, извинись':
            sorry = str('Извините, ')
            sorry = sorry + '@' + str(message.from_user.username)
            bot.send_message(message.chat.id, sorry)

        if message.text == 'Бот спокойной ночи' or message.text == 'Bot bb' or message.text == 'Бот, спокойной ночи':
            bot.reply_to(message, 'И тебе @' + message.from_user.username)

        if message.text == 'Бот, команды' or message.text == '/commands' or str(
                message.text).lower() == '/commands@Consta_bot'.lower():
            commands_list = 'Бот, спокойной ночи' + '\n' + '/help' + '\n' + '/start' + '\n' + "Бот принимает сообщения с " \
                                                                                              "выставленными предметами на" \
                                                                                              " аукционе и возвращает ссылки" \
                                                                                              " для покупки" + '\n' + \
                            '.Пин + <any>' + '\n' + 'Отправка профиля из игры форвардом - вернет сообщение ' \
                                                    'с оставшимся опытом\n' + '/add_ping\n' + '/dl_ping\n' + \
                            '/ping_all только для админов чата\n'
            commands_list += 'Запрос в виде /get_recipe <Название предмета СТРОГО как в рецептах> пришлет ответное ' \
                             'сообщение с максимальными статами'
            bot.reply_to(message, commands_list)
        msg = message.text

        if message.forward_from is not None:
            # Parser messages from Dima's bot
            if message.forward_from.id == 1033007754:
                txt = message.text
                user_id = message.from_user.id
                if ' vs' in txt and 'лвл - %win% | твой урон || урон моба' not in txt:
                    right = txt.find(' vs')
                    player_name = txt[:right]
                    left = right + len(' vs')
                    txt = str(txt[left:])
                    txt = txt.replace('%', '')
                    txt = txt.replace('\n', ' - ')
                    players_and_percents = txt.split(' - ')
                    if players_and_percents[0] == '':
                        players_and_percents.pop(0)
                    all_percents = 0
                    sum_not_100_percents = 0
                    count_not_100_percents = 0
                    for i in range(1, len(players_and_percents), 2):
                        all_percents += float(players_and_percents[i])
                        if float(players_and_percents[i]) < 100:
                            count_not_100_percents += 1
                            sum_not_100_percents += float(players_and_percents[i])
                    return_message = f'Отчет для <a href="tg://user?id={user_id}">{player_name}</a> ' \
                                     f'за {int(len(players_and_percents) / 2)} боев:\n{round(all_percents, 2)}% ' \
                                     f'- всего ({round(all_percents / (len(players_and_percents) / 2), 2)}%' \
                                     f' в среднем)\n{sep_by_3(str(count_not_100_percents))} не 100% побед:\n' \
                                     f'{str(round(sum_not_100_percents, 2))}% всего (' \
                                     f'{round(sum_not_100_percents / count_not_100_percents, 2)}% в среднем)'
                    bot.send_message(message.chat.id, return_message, disable_web_page_preview=True, parse_mode="HTML")

        if command_trigger_exp_to_lvl in msg and message.forward_from is not None:
            # Parser messages from RF bot
            if message.forward_from.id == 577009581:
                if message.date - 60 * 10 <= message.forward_date:
                    try:
                        bot.delete_message(message.chat.id, message.message_id)
                        user_id = message.from_user.id
                        msg_text = ''
                        left = msg.find('Ник: ') + len('Ник: ')
                        game_username = msg[left:msg.find('\n', left)]
                        msg_text += f'<a href="tg://user?id={user_id}">{game_username}</a>, тебе осталось:'
                        stats = list(help_func.get_profile(msg))
                        left = msg.find('🌕Опыт: ') + len('🌕Опыт: ')
                        now_exp = msg[left:msg.find('/', left)]
                        need_exp = msg[msg.find('/', left) + 1:msg.find('\n', left)]
                        now_exp = int(float(now_exp.replace(' ', '')))
                        need_exp = int(need_exp.replace(' ', ''))
                        msg_text += f'\n  •{help_func.sep_by_3(str(round((need_exp - now_exp), 3)))}' \
                                    f' 🌕Опыта до {stats[3] + 1} уровня'
                        if '/paragon' in msg:
                            left = msg.find(f'🏅Уровень: {stats[3]}(') + len(f'🏅Уровень: {stats[3]}(')
                            paragon = msg[left:msg.find(')', left)]
                            if ' ' in paragon:
                                paragon = int(paragon.replace(" ", ''))
                            else:
                                paragon = int(paragon)
                            up_50 = 14200000
                            exp_to_par = int(help_func.exp_to_paragon(paragon, now_exp))
                            if exp_to_par == -1:
                                msg_text += f'\n  •Я не знаю сколько опыта надо. /p_info для бОльшей инфы'
                            else:
                                msg_text += f'\n  •{help_func.sep_by_3(str(exp_to_par))} 🌕Опыта до {paragon + 1} парагона '
                        stats.insert(5, now_exp)
                        msg_text += database_functions.save_profiles(*stats)
                        bot.send_message(message.chat.id, msg_text, disable_web_page_preview=True, parse_mode="HTML")
                        return 0
                    except Exception as error:
                        bot.send_message(roman, error)
                else:
                    bot.reply_to(message, 'Профиль не должен быть старше более 5 мин')

        if ')' in message.text and ' | ' in message.text and message.forward_from is not None:
            if message.forward_from.id == 577009581:
                bot.send_message(message.chat.id, help_func.vote_msg(message.text))
        elif database_functions.check_is_user_in_allowed(message, bot, message.chat.id):
            if 'не в ген. штабе]' in a or 'уже совершает действие]' in a:
                if ' не в ген. штабе]' in a:
                    msg = str(message.text[1:message.text.find(' не в ген. штабе]')])
                elif 'уже совершает действие]' in a:
                    msg = str(message.text[1:message.text.find(' уже совершает действие]')])
                message_txt = ''
                player_for_trigger = msg.split(', ')
                ids = database_functions.get_list_of_players_bu_nickname(player_for_trigger)
                if len(ids) == len(player_for_trigger):
                    for i in range(len(player_for_trigger)):
                        if ids[i] is not None:
                            message_txt += f"<a href='tg://user?id={ids[i]}'>{player_for_trigger[i]}</a>\n"
                            message_txt = str(message_txt)
                        # elif i == len(player_for_trigger)-1 and ids[i] is not None:
                        #     message_txt += f'<a href="tg://user?id={ids[i]}">{player_for_trigger[i]}</a>'
                    message_txt += '\nКабанчиком в ГШ, вас ожидают'
                else:
                    message_txt = 'Кого-то из игроков нет в моей базе, я не могу ничего поделать =('
                # print(message_txt)
                message_txt = str(message_txt)
                bot.send_message(message.chat.id, message_txt, disable_web_page_preview=True, parse_mode='HTML')

        if str(message.text).find(command_trigger_auction) != -1 and message.forward_from is not None:
            msg = 'Держи!\n'
            msg = message.text.replace('_return_', '_buy_')
            msg += '\n.'
            markup = types.InlineKeyboardMarkup(row_width=1)
            i = 1
            left = msg.find(f'{i})') + len(f'{i})')
            while left != -1:
                txt = msg[left:msg.find(' - ', left)]
                data = str(msg[msg.find('/a_buy', left):msg.find('\n', left)])
                button = types.InlineKeyboardButton(text=f"{txt}", callback_data='',
                                                    url=f"http://t.me/share/url?url={data}")
                # switch_inline_query=f"{data}")
                markup.add(button)
                i += 1
                left = msg.find(f'{i})')
                if left != -1:
                    left += len(f'{i})')
            msg = msg[:len(msg) - 1]
            bot.send_message(message.chat.id, msg, reply_markup=markup)
        if ('Ты направляешься в замок' in msg or 'Ты прибыл в замок, бой будет проходить автоматически!' in msg) and \
                message.forward_from is not None:  # and message.chat.id == -1001226877831:
            if message.forward_from.id == 577009581:
                edit_castle_pin(bot, message, msg)
        if ('Ты одержал победу над ' in msg or 'Ты ☠пал от рук ' in msg) and message.forward_from is not None: \
                # and message.chat.id == -1001226877831:
            if message.forward_from.id == 577009581:
                chat_info = bot.get_chat(message.chat.id)
                pin_txt = None
                if chat_info.pinned_message is not None:
                    if chat_info.pinned_message.from_user.is_bot is True:
                        pin_txt = str(chat_info.pinned_message.text)
                        if '===+++===' in pin_txt:
                            fight_editor(bot, message)

        if a.find(command_trigger_pin_low_case, 0, len(command_trigger_pin_low_case)) != -1 or a.find(
                command_trigger_pin_up_case, 0,
                len(
                    command_trigger_pin_up_case)) != -1:
            pinned_user_message_id = message.message_id
            chat_ida = message.chat.id
            bot_message = ''
            for z in range(len(command_trigger_pin_low_case), len(a)):
                if z == len(command_trigger_pin_low_case):
                    bot_message += a[z].upper()
                else:
                    bot_message += a[z]
            useless = str(bot.send_message(message.chat.id, bot_message).message_id)
            message_bot_sent_id = useless
            try:
                bot.pin_chat_message(message.chat.id, useless, False)
            except:
                bot.send_message(message.chat.id, 'Дайте больше прав, пожалуйста (:')

        if message.text == 'Кинь гифку' or message.text == '/gif' or str(
                message.text).lower() == '/gif@Consta_bot'.lower():
            num_of_gif = randint(1, 5)
            # num_of_gif = 1
            if num_of_gif == 1:
                bot.send_document(message.chat.id, 'https://media.giphy.com/media/XCm1DuH04vZ6KXIXh8/giphy.gif')
            if num_of_gif == 2:
                bot.send_document(message.chat.id, 'https://media.giphy.com/media/M8zyReUTgWeitlQI1G/giphy.gif')
            if num_of_gif == 3:
                bot.send_document(message.chat.id, 'https://media.giphy.com/media/kaHm4fBiIynYIkwwbD/giphy.gif')
            if num_of_gif == 4:
                bot.send_document(message.chat.id, 'https://media.giphy.com/media/jTBS0JwtWAeusllqiQ/giphy.gif')
            if num_of_gif == 5:
                bot.send_document(message.chat.id, 'https://media.giphy.com/media/TGLAvE48ERAJwFJMMh/giphy.gif')
        msg = str(message.text)

        if message.text.find(grace_trigger) != -1 and message.forward_from is not None:
            if message.forward_from.id == 577009581:
                bot.reply_to(message, 'Грац!')

        if msg.find(command_trigger_recipe, 0,
                    len(command_trigger_recipe) + 1) != -1 and message.forward_from is not None and msg.find(
            'антиграв') == -1:
            if message.forward_from.id == 577009581 and "Шанс крафта:" in a:
                message.text = message.text.lower()
                database_functions.check_recipe(message, bot)


# new chat member
@bot.message_handler(content_types=['new_chat_members'])
def greeting(message):
    bot.reply_to(message, "Приветствую, путник")


@bot.edited_message_handler(content_types=['text'])
def edit_message(message):
    if str(message.text).find(command_trigger_pin_up_case, 0, len(command_trigger_pin_up_case)) != -1 or str(
            message.text).find(
            command_trigger_pin_low_case, 0,
            len(command_trigger_pin_low_case)) != -1:
        new_text = ''
        got_message = str(message.text)
        for i in range(4, len(got_message)):
            new_text = new_text + got_message[i]
        bot.edit_message_text(new_text, chat_ida, message_bot_sent_id)


@bot.callback_query_handler(func=lambda call: True)
def checker(query):
    data = query.data
    if data.startswith('accept') and (query.from_user.id == query.message.reply_to_message.from_user.id or
                                      query.message.reply_to_message.from_user.id == 980441353 or
                                      query.from_user.id == roman):
        duel_func.accepted(bot, query)
    elif data.startswith('cancel') and query.from_user.id == query.message.reply_to_message.from_user.id:
        duel_func.cancel(bot, query)
    elif data.startswith('en'):
        try:
            # bot.send_message(roman, query)
            if query.message.reply_to_message.from_user.id == query.from_user.id or query.from_user.id == roman:
                bot.send_message(*help_func.make_energy_msg(query.data))
        except Exception as error:
            bot.send_message(roman, error)


if __name__ == '__main__':
    bot.polling(none_stop=True)
