import config
import telebot
from telebot import types
import database_functions
import random


def boss_starter(bot, message):
    try:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="Лич", callback_data="lich")
        button2 = types.InlineKeyboardButton(text="Архилич", callback_data="archilich")
        markup.add(button1, button2)
        name = database_functions.get_name(message.from_user.id)
        bot.reply_to(
            message.reply_to_message,
            f"{name}Выберите босса на которого будет собран рейд",
            markup=markup,
        )
    except Exception as e:
        database_functions.alarm(bot, message, e)


def mob_fight(bot, message, mob_lvl, player_id, mob_type):
    first = list(database_functions.get_profile_by_id(player_id))
    second = list(database_functions.get_mob_by_lvl(mob_lvl, mob_type))
    if second is None:
        bot.send_message(
            message.chat.id,
            "Необходимо ввести сообщение в формате /mobf <lvl> <e> Этер опционален",
        )
        return 0
    first.append(first[1])
    second.append(second[1])
    first[1] = first[10]
    second[1] = second[10]
    fight_txt = f"Сражение между\n🏅{first[6]} {first[0]}({first[1]}❤️)\nИ\n🏅{second[6]} {second[0]}({second[1]}❤️)\n\n"
    exit_fl = 0
    if first[9] is None:
        first[9] = 0
    elif second[9] is None:
        second[9] = 0
    first[5] = first[5] - second[9]
    second[5] = second[5] - first[9]
    if random.randint(0, 1) == 1:
        first, second = second, first
    # username[0], hp[1], atk[2], def[3], cri[4], ddg[5], lvl[6], win[7], loose[8],accu[9], full_hp[10]
    while first[1] > 0 and second[1] > 0 and exit_fl == 0:
        if second[5] > round(random.uniform(0.0, 100.0), 2) and exit_fl == 0:
            fight_txt += f"{second[0]}  увернулся от атаки 💨\n"
        elif (
            first[4] > round(random.uniform(0.0, 100.0), 2)
            and 1.4 * (first[2] - second[3]) >= 310
            and exit_fl == 0
        ):
            dmg = round(1.4 * (first[2] - second[3]), 2)
            second[1] = second[1] - dmg
            fight_txt += f"{first[0]}  нанес удар 💥💥-{dmg}\n"
            if second[1] <= 0:
                exit_fl = 1
        elif first[2] - second[3] >= 310 and exit_fl == 0:
            dmg = round(first[2] - second[3], 2)
            second[1] = second[1] - dmg
            fight_txt += f"{first[0]}  нанес удар 💥-{dmg}\n"
            if second[1] <= 0:
                exit_fl = 1
        elif exit_fl == 0:
            dmg = first[6] * 5 + random.randint(0, 50)
            second[1] = second[1] - dmg
            fight_txt += f"{first[0]}  нанес удар (min)💥-{dmg}\n"
            if second[1] <= 0:
                exit_fl = 1

        if first[5] > round(random.uniform(0.0, 100.0), 2) and exit_fl == 0:
            fight_txt += f"{first[0]}  увернулся от атаки 💨\n"
        elif (
            second[4] > round(random.uniform(0.0, 100.0), 2)
            and 1.4 * (second[2] - first[3]) >= 310
            and exit_fl == 0
        ):
            dmg = round(1.4 * (second[2] - first[3]), 2)
            first[1] = first[1] - dmg
            fight_txt += f"{second[0]}  нанес удар 💥💥-{dmg}\n"
            if first[1] <= 0:
                exit_fl = 1
        elif second[2] - first[3] >= 310 and exit_fl == 0:
            dmg = round(second[2] - first[3], 2)
            first[1] = first[1] - dmg
            fight_txt += f"{second[0]}  нанес удар 💥-{dmg}\n"
            if first[1] <= 0:
                exit_fl = 1
        elif exit_fl == 0:
            dmg = second[6] * 5 + random.randint(0, 50)
            first[1] = first[1] - dmg
            fight_txt += f"{second[0]}  нанес удар (min)💥-{dmg}\n"
            if first[1] <= 0:
                exit_fl = 1
    pass
    if first[1] < 0:
        fight_txt += (
            f"\n{second[0]}({round(second[1], 2)}❤/{second[10]}❤️)"
            f" одержал победу над {first[0]}({round(first[1], 2)}❤/{first[10]}❤)"
        )

    else:
        fight_txt += (
            f"\n{first[0]}({round(first[1], 2)}❤/{first[10]}❤)"
            f" одержал победу над {second[0]}({round(second[1], 2)}❤/{second[10]}❤️)"
        )

    bot.send_message(message.chat.id, fight_txt)


def mob_fight_more_1(bot, message, mob_lvl, player_id, mob_type, count: int):
    try:
        first = list(database_functions.get_profile_by_id(player_id))
        second = list(database_functions.get_mob_by_lvl(mob_lvl, mob_type))
        fight_txt = f"Сражение между\n🏅{first[6]} {first[0]}({first[1]}❤️)\nИ\n🏅{second[6]} {second[0]}({second[1]}❤️)\n\n"
        first.append(first[1])
        second.append(second[1])
        first[7], first[8], second[7], second[8] = int(0), int(0), int(0), int(0)
        first[5] = first[5] - second[9]
        second[5] = second[5] - first[9]
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
            # username[0], hp[1], atk[2], def[3], cri[4], ddg[5], lvl[6], win[7], loose[8], accu[9], full_hp[10]
            while first[1] > 0 and second[1] > 0 and exit_fl == 0:
                if second[5] > round(random.uniform(0.0, 100.0), 2) and exit_fl == 0:
                    pass
                elif (
                    first[4] > round(random.uniform(0.0, 100.0), 2)
                    and 1.4 * (first[2] - second[3]) >= 300
                    and exit_fl == 0
                ):
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
                elif (
                    second[4] > round(random.uniform(0.0, 100.0), 2)
                    and 1.4 * (second[2] - first[3]) >= 300
                    and exit_fl == 0
                ):
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
            pass
            if first[1] < 0:
                first[8] += 1
                second[7] += 1

            else:
                first[7] += 1
                second[8] += 1
        if first[7] > first[8]:
            fight_txt += f"{first[0]} выигрывает {second[0]} с {round((first[7] / count) * 100, 2)}% побед"
        else:
            fight_txt += f"{second[0]} выигрывает {first[0]} с {round((second[7] / count) * 100, 2)}% побед"
        fight_txt += f" на {count} боёв"
        bot.send_message(message.chat.id, fight_txt)
    except:
        pass


def mob_fight_more_1_without_heal(
    bot, message, mob_lvl, player_id, mob_type, count: int = 10000
):
    try:
        first = list(database_functions.get_profile_by_id(player_id))
        if first is not None:
            second = list(database_functions.get_mob_by_lvl(mob_lvl, mob_type))
            fight_txt = f"Сражение между\n🏅{first[6]} {first[0]}({first[1]}❤️)\nИ\n🏅{second[6]} {second[0]}({second[1]}❤️)\n\n"
            first.append(first[1])
            second.append(second[1])
            first.append(0)
            second.append(0)

            ll = []
            player = first[0]
            first[7], first[8], second[7], second[8] = int(0), int(0), int(0), int(0)
            if first[9] is None:
                first[9] = 0
            elif second[9] is None:
                second[9] = 0
            first[5] = first[5] - second[9]
            second[5] = second[5] - first[9]
            avg = 0
            lll = 0
            for i in range(count):

                if second[0] != player:
                    second[1] = second[10]
                if first[0] != player:
                    first[1] = first[10]
                exit_fl = 0
                if random.randint(0, 1) == 1:
                    first, second = second, first
                # username[0], hp[1], atk[2], def[3], cri[4], ddg[5], lvl[6], win[7], loose[8], accu[9], full_hp[10],
                # max_length[11]
                while first[1] > 0 and second[1] > 0 and exit_fl == 0:
                    if (
                        second[5] > round(random.uniform(0.0, 100.0), 2)
                        and exit_fl == 0
                    ):
                        pass
                    elif (
                        first[4] > round(random.uniform(0.0, 100.0), 2)
                        and 1.4 * (first[2] - second[3]) >= 300
                        and exit_fl == 0
                    ):
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
                    elif (
                        second[4] > round(random.uniform(0.0, 100.0), 2)
                        and 1.4 * (second[2] - first[3]) >= 300
                        and exit_fl == 0
                    ):
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
                if first[1] > 0 and first[0] == player:
                    lll += 1
                    # bot.send_message(message.chat.id, 'win')
                elif second[1] > 0 and second[0] == player:
                    lll += 1
                    # bot.send_message(message.chat.id, 'win')
                elif (first[1] > 0 and first[0] != player) or (
                    second[1] > 0 and second[0] != player
                ):
                    if first[0] != player:
                        first, second = second, first
                    if lll != 0 and lll > first[11]:
                        if len(ll) > 1:
                            lll = lll - ll[len(ll) - 1]
                        first[11] = lll
                        ll.append(lll)
                        avg += lll
                        lll = 0
                    first[1] = first[10]

            if first[0] != player:
                first, second = second, first
            ll.sort(reverse=True)
            first[11] = ll[0]
            fight_txt += (
                f"{first[0]} максимальная серия побед над мобом {second[0]}: {first[11]}\nВ среднем:"
                f" {round(avg / len(ll), 4)} побед подряд\nДанные актуальны на прогоне"
                f" в 10 000 симуляций\nДанные примерные и могут отличаться от реальности!!!"
            )
            bot.send_message(message.chat.id, fight_txt)
        elif first is None:
            bot.send_message(message.chat.id, "Может профиль сначала скинешь, а?")
    except:
        pass
