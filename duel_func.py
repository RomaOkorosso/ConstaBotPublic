import config
import telebot
from telebot import types
import database_functions
import random
from help_func import sep_by_3 as sep


def request_battle(bot, message, count):
    try:
        if message.reply_to_message is not None:
            defender = message.reply_to_message.from_user.id
        else:
            bot.reply_to(message, 'Необходимо отправить команду /fight ответом (реплай)'
                                  ' на сообщение тому, кого хочешь пригласить в дуэль')
            return 0
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text='🗡Сражаться!', callback_data='accept')
        button2 = types.InlineKeyboardButton(text='❌Отказаться', callback_data='cancel')
        markup.add(button1, button2)
        name1, name2 = database_functions.get_names(message.from_user.id, defender)
        if name1 is not None and name2 is not None:
            bot.reply_to(message.reply_to_message, f'Игрок {name1[0]} вызывает игрока {name2[0]}'
                                                   f' на дуэль (🏹{count} раз). Будем биться?', reply_markup=markup)
        elif name1 is None:
            bot.reply_to(message, 'Вас нет в моем списке игроков, необходимо скинуть свой профиль из игры')
        elif name2 is None:
            bot.reply_to(message, 'Противника нет у меня в списках, наобходимо скинуть профиль')
    except:
        pass


def cancel(bot, query):
    pass
    bot.edit_message_text("Соперник отказался от дуэли 😒", query.message.chat.id, query.message.message_id)


# TODO rewrite to OOP
def accepted(bot, query):
    try:
        msg = query.message.text
        message = query.message
        att = msg[msg.find('Игрок ') + len('Игрок '):msg.find(' вызывает')]
        first = list(database_functions.get_prof(att))
        first.append(first[1])
        deff = msg[msg.find('игрока ') + len('игрока '):msg.find(' на дуэль')]
        second = list(database_functions.get_prof(deff))
        second.append(second[1])
        count = int(msg[msg.find('🏹') + len('🏹'):msg.find(' раз')])

        first[5] = first[5] - second[9]
        second[5] = second[5] - first[9]
        if count < 5:
            fight_txt = f'Сражение между 🏅{first[6]}{first[0]}({first[1]}❤️) 🏅{second[6]}{second[0]}' \
                        f'({second[1]}❤️)\n\n'
            for i in range(count):
                first[1] = first[10]
                second[1] = second[10]
                exit_fl = 0
                if first[9] is None:
                    first[9] = 0
                elif second[9] is None:
                    second[9] = 0
                if random.randint(0, 1) == 1:
                    first, second = second, first
                # username[0], hp[1], atk[2], def[3], cri[4], ddg[5], lvl[6], win[7], loose[8],accu[9], full_hp[10]
                while first[1] > 0 and second[1] > 0 and exit_fl == 0:
                    if second[5] > round(random.uniform(0.0, 100.0), 2) and exit_fl == 0:
                        fight_txt += f'{second[0]}  увернулся от атаки 💨\n'
                    elif first[4] > round(random.uniform(0.0, 100.0), 2) and 1.4 * (
                            first[2] - second[3]) >= 300 and exit_fl == 0:
                        dmg = round(1.4 * (first[2] - second[3]), 2)
                        second[1] = second[1] - dmg
                        fight_txt += f'{first[0]}  нанес удар 💥💥-{dmg}\n'
                        if second[1] <= 0:
                            exit_fl = 1
                    elif first[2] - second[3] >= 300 and exit_fl == 0:
                        dmg = round(first[2] - second[3], 2)
                        second[1] = second[1] - dmg
                        fight_txt += f'{first[0]}  нанес удар 💥-{dmg}\n'
                        if second[1] <= 0:
                            exit_fl = 1
                    elif exit_fl == 0:
                        dmg = first[6] * 5 + random.randint(0, 50)
                        second[1] = second[1] - dmg
                        fight_txt += f'{first[0]}  нанес удар (min)💥-{dmg}\n'
                        if second[1] <= 0:
                            exit_fl = 1

                    if first[5] > round(random.uniform(0.0, 100.0), 2) and exit_fl == 0:
                        fight_txt += f'{first[0]}  увернулся от атаки 💨\n'
                    elif second[4] > round(random.uniform(0.0, 100.0), 2) and 1.4 * (
                            second[2] - first[3]) >= 300 and exit_fl == 0:
                        dmg = round(1.4 * (second[2] - first[3]), 2)
                        first[1] = first[1] - dmg
                        fight_txt += f'{second[0]}  нанес удар 💥💥-{dmg}\n'
                        if first[1] <= 0:
                            exit_fl = 1
                    elif second[2] - first[3] >= 300 and exit_fl == 0:
                        dmg = round(second[2] - first[3], 2)
                        first[1] = first[1] - dmg
                        fight_txt += f'{second[0]}  нанес удар 💥-{dmg}\n'
                        if first[1] <= 0:
                            exit_fl = 1
                    elif exit_fl == 0:
                        dmg = second[6] * 5 + random.randint(0, 50)
                        first[1] = first[1] - dmg
                        fight_txt += f'{second[0]}  нанес удар (min)💥-{dmg}\n'
                        if first[1] <= 0:
                            exit_fl = 1
                pass
                if first[1] < 0:
                    fight_txt += f'\n{second[0]}({round(second[1], 2)}❤/{second[10]}❤️)' \
                                 f' одержал победу над {first[0]}({round(first[1], 2)}❤/{first[10]}❤)'

                else:
                    fight_txt += f'\n{first[0]}({round(first[1], 2)}❤/{first[10]}❤))' \
                                 f' одержал победу над {second[0]}({round(second[1], 2)}❤/{second[10]}❤️)'
                if count == 1:
                    bot.edit_message_text(fight_txt, query.message.chat.id, query.message.message_id)
                elif count != 1 and i == 1:
                    bot.delete_message(query.message.chat.id, query.message.message_id)
                    bot.send_message(query.message.chat.id, fight_txt)
                    fight_txt = f'Сражение между 🏅{first[6]}{first[0]}({first[1]}❤️) 🏅{second[6]}{second[0]}' \
                                f'({second[1]}❤️)\n\n'
                else:
                    bot.send_message(query.message.chat.id, fight_txt)
                    fight_txt = f'Сражение между 🏅{first[6]}{first[0]}({first[1]}❤️) 🏅{second[6]}{second[0]}' \
                                f'({second[1]}❤️)\n\n'

        elif count >= 6:
            bot.delete_message(query.message.chat.id, query.message.message_id)
            fight_txt = f'Сражение между 🏅{first[6]}{first[0]}({first[1]}❤️) 🏅{second[6]}{second[0]}({second[1]}❤️)\n\n'
            for i in range(count):
                first[1] = first[10]
                second[1] = second[10]
                exit_fl = 0
                if first[9] is None:
                    first[9] = 0
                elif second[9] is None:
                    second[9] = 0
                if first[8] is None:
                    first[8] = int(0)
                if second[8] is None:
                    second[8] = int(0)
                if first[7] is None:
                    first[7] = int(0)
                if second[7] is None:
                    second[7] = int(0)

                if random.randint(0, 1):
                    first, second = second, first
                # username[0], hp[1], atk[2], def[3], cri[4], ddg[5], lvl[6], win[7], loose[8], accu[9], full_hp[10]
                while first[1] > 0 and second[1] > 0 and exit_fl == 0:
                    if second[5] > round(random.uniform(0.0, 100.0), 2) and exit_fl == 0:
                        pass
                    elif first[4] > round(random.uniform(0.0, 100.0), 2) and 1.4 * (
                            first[2] - second[3]) >= 300 and exit_fl == 0:
                        dmg = round(1.4 * (first[2] - second[3]), 2)
                        second[1] = second[1] - dmg
                        if second[1] <= 0:
                            exit_fl = 1
                    elif first[2] - second[3] >= 300 and exit_fl == 0:
                        dmg = round(first[2] - second[3], 2)
                        second[1] = second[1] - dmg
                        if second[1] <= 0:
                            exit_fl = 1
                    elif exit_fl == 0:
                        dmg = first[6] * 5 + random.randint(0, 50)
                        second[1] = second[1] - dmg
                        if second[1] <= 0:
                            exit_fl = 1

                    if first[5] > round(random.uniform(0.0, 100.0), 2) and exit_fl == 0:
                        pass
                    elif second[4] > round(random.uniform(0.0, 100.0), 2) and 1.4 * (
                            second[2] - first[3]) >= 300 and exit_fl == 0:
                        dmg = round(1.4 * (second[2] - first[3]), 2)
                        first[1] = first[1] - dmg
                        if first[1] <= 0:
                            exit_fl = 1
                    elif second[2] - first[3] >= 300 and exit_fl == 0:
                        dmg = round(second[2] - first[3], 2)
                        first[1] = first[1] - dmg
                        if first[1] <= 0:
                            exit_fl = 1
                    elif exit_fl == 0:
                        dmg = second[6] * 5 + random.randint(0, 50)
                        first[1] = first[1] - dmg
                        if first[1] <= 0:
                            exit_fl = 1

                if first[1] < 0:
                    first[8] += 1
                    second[7] += 1
                else:
                    first[7] += 1
                    second[8] += 1

            if first[7] > first[8]:
                fight_txt += f'{first[0]} выигрывает {second[0]} с {round((first[7] / count) * 100, 4)}% побед'
            else:
                fight_txt += f'{second[0]} выигрывает {first[0]} с {round((second[7] / count) * 100, 4)}% побед'
            fight_txt += f' на {str(sep(str(count)))} боёв'
            bot.send_message(message.chat.id, fight_txt)
    except:
        pass
