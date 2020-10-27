import pytz
import datetime


def finding_in_totem(text):
    if '✨Максимальный уровень тотема✨' in text:
        lvl = 10
        aden, bronze, silver, gold = 0, 0, 0, 0
    else:
        lvl = text[text.find('ур.') - 1]
        start = text.find('Стоимость апгрейда:') + len('Стоимость апгрейда:') + 1
        stop = len(text)
        left = text.find('🏵', start, stop) + 1
        right = text.find('/', start, stop)
        aden = text[left:right]
        start = right + 3
        left = text.find('🥉', start, stop) + 1
        right = text.find('/', start, stop)
        bronze = text[left:right]
        start = right + 3
        left = text.find('🥈', start, stop) + 1
        right = text.find('/', start, stop)
        silver = text[left:right]
        start = right + 3
        left = text.find('🥇', start, stop) + 1
        right = text.find('/', start, stop)
        gold = text[left:right]
    return lvl, aden, bronze, silver, gold


# (табла: profiles:: user_id, username, hp, lvl, pvp, exp, credits, atk, def,
#                    cri, ddg, win, loose, rates, last_update_time, last_update_day)


def get_profile(profile: str):
    left = profile.find('Ник: ') + len('Ник: ')
    name = profile[left:profile.find('Идентификатор:', left)]
    if "'" in name:
        name = name.replace("'", '')
    name = name.replace('\n', '')
    left = profile.find('Идентификатор:') + 1 + len('Идентификатор:')
    user_id = int(profile[left:profile.find('\n', left)])
    left = profile.find('Здоровье:') + 1 + len('Здоровье:')
    left = profile.find('/', left, left + 12) + 1
    hp = int(profile[left:profile.find('\n', left)])
    left = profile.find('🏅Уровень: ') + len('🏅Уровень: ')
    lvl = profile[left:profile.find('\n', left)]
    if '/paragon' in profile:
        left = profile.find('🏅Уровень: ') + len('🏅Уровень: ')
        lvl = int(profile[left:profile.find('(', left)])
    else:
        lvl = int(lvl)
    left = profile.find('👊🏻PVP: ') + len('👊🏻PVP: ')
    pvp = int(str(profile[left:profile.find('\n', left)]).replace(' ', ''))
    left = profile.find('⚔️Атака: 45 (+') + len('⚔️Атака: 45 (+')
    atk = int(profile[left:profile.find(') ', left)]) + 45
    left = profile.find('🛡Защита: 20 (+') + len('🛡Защита: 20 (+')
    defence = int(profile[left:profile.find(')', left)]) + 20
    left = profile.find('💨Уворот: 3% (+') + len('💨Уворот: 3% (+')
    ddg = float(profile[left:profile.find('%)', left)]) + 3
    left = profile.find('🎯Крит: 10% (+') + len('🎯Крит: 10% (+')
    crt = float(profile[left:profile.find('%)', left)]) + 10
    left = profile.find('⏳Точность: 1% (+') + len('⏳Точность: 1% (+')
    accu = float(profile[left:profile.find('%)', left)]) + 1
    if '💰Кредитов: ' in profile:
        left = profile.find('💰Кредитов: ') + len('💰Кредитов: ')
        credits = str(profile[left:profile.find('\n', left)]).replace(' ', '')
        credits = int(credits)
    else:
        credits = 0
    left = profile.find('🏵Аден: ') + len('🏵Аден: ')
    aden = profile[left:profile.find('\n', left)]
    aden = aden.replace(' ', '')
    aden = int(aden)
    prem_acc, abu = False, False
    prem_duration, abu_duration = datetime.date(1991, 1, 1), datetime.date(1991, 1, 1)
    left = profile.find('🎗Премиум аккаунт по - ')
    if left != -1:
        left += len('🎗Премиум аккаунт по - ')
        prem_acc = True
        prem_duration_str = profile[left:profile.find('\n', left)]
        nums = [int(n) for n in prem_duration_str.split('.')]
        nums = reversed(nums)
        prem_duration = datetime.date(*nums)
    left = profile.find('🖲АБУ - ')
    if left != -1:
        left += len('🖲АБУ - ')
        abu = True
        right = profile.find(' (копает)')
        if right != -1:
            abu_duration_str = profile[left:right]
        else:
            abu_duration_str = profile[left:profile.find('\n', left)]
        nums = [int(n) for n in abu_duration_str.split('.')]
        nums = reversed(nums)
        abu_duration = datetime.date(*nums)
    return user_id, name, hp, lvl, pvp, credits, aden, atk, defence, crt, ddg, accu, prem_acc, prem_duration, abu, \
           abu_duration


# (табла: profiles:: user_id, username, hp, lvl, pvp, exp, credits, atk, def,
#                    cri, ddg, win, loose, rates, last_update_time, last_update_day, aden)


def sep_by_3(txt: str):
    txt = txt[::-1]
    return_txt = ''
    _ = 0
    while _ < len(txt):
        ii = _
        while ii < _ + 3 and ii != len(txt):
            return_txt = return_txt + txt[ii]
            ii += 1
        return_txt = return_txt + ' '
        _ += 3
    return_txt = return_txt[::-1]
    if return_txt[0] == ' ':
        return_txt = return_txt[1::]
    return return_txt


def vote_msg(text):
    try:
        from itertools import repeat, zip_longest
        users = [
            {
                **user,
                'name': ')'.join(user['name'].split(')')[1:]),
                'percent': float(user['percent'].rstrip('%'))
            }
            for user in (
                dict(
                    zip_longest(
                        [
                            'name',
                            'level',
                            'pvp',
                            'percent',
                            'vote_link',
                            'self_votes'
                        ],
                        [word.strip() for word in line.split('|')]
                    )
                )
                for line in text.split('\n')
            )
        ]

        # Здесь можно выкинуть players_x, и players_y сразу делать set-ами, но как-то лень
        players_x, players_y = zip(*(list(zip(*player)) for player in (
            [
                (x, y)
                for x in range(1, 250)
                for y in range(1, 250)
                if abs(x / y * 100 - user['percent']) < 1e-2
            ] + (list(zip(repeat(0), range(250))) if user['percent'] == 0 else [])
            for user in users
        )))
        pass

        all_votes = (min(set.intersection(*[set(votes) for votes in players_y])))
        for i in range(len(users)):
            users[i]['self_votes'] = players_x[i][players_y[i].index(all_votes)]

        users.sort(key=lambda x: x['self_votes'], reverse=True)
        if users[0]['self_votes'] == 0:
            users.sort(key=lambda x: x['pvp'], reverse=True)

        icons = ['👑Патриарх (+15% ⚔️ и +15% 🛡):\n', '🔱Архонт (+20% 🛡):\n', '🗡Атакующий (+10% ⚔):\n',
                 '🛡Защитник (+10% 🛡):\n', '📯Поддержка (+10% ❤️ и +5% 🛡):\n']
        msg = ''
        if len(users) > 0:
            for i in range(len(users)):
                if i < len(icons):
                    msg += str(icons[i])
                    new_line = '\t\t' + str(users[i]['name']) + ' | ' + str(users[i]['pvp']) + '👊🏻 | ' + str(
                        users[i]['self_votes']) + '🗳 | ' + str(users[i]['percent']) + '%\n'
                    msg = msg + new_line + '\n'
                elif i > len(icons):
                    new_line = str(users[i]['name']) + ' | ' + str(users[i]['pvp']) + '👊🏻 | ' + str(
                        users[i]['self_votes']) + '🗳 | ' + str(users[i]['percent']) + '%\n'
                    msg = msg + new_line[1::]
                if i == len(icons) - 1:
                    msg += '\n'
        msg += f'\nВсего проголосовало: {all_votes}🗳\nДанные примерные и могут отличаться от реальности'
        return msg
    except:
        pass


# def collect_items_to_check(txt: str):
#     body = 'корпус'
#     legs = 'штаны'
#     arms = 'перчатки'
#     head = 'шлем'
#     feets = 'ботинки'
#     arm = [body, legs, arms, head, feets]
#     left = 0
#     check_armor = [[]]
#     for item in arm:
#         left = txt.find(item, left)
#         if left != -1:
#             item = txt


def make_energy_msg(data):
    data = str(data)
    left = data.find('en_') + len('en_')
    right = data.find('_', left)
    to_user = data[left:right]
    left = right + len('_')
    right = data.find('_', left)
    type_acc = data[left:right]
    left = right + len('_')
    energy_and_time = data[left:]
    energy_and_time = energy_and_time.split('_')
    energy_and_time = list(map(int, energy_and_time))
    msg = ''
    prem_energy = 17.5 * 60
    not_prem_energy = 25 * 60
    if type_acc == 'prem':
        next_time = prem_energy
    else:
        next_time = not_prem_energy
    while energy_and_time[0] < 6:
        msg += f"""{energy_and_time[0]} 🔋 в 🕐{datetime.datetime.fromtimestamp(energy_and_time[1],
                                                                                tz=pytz.timezone(
                                                                                    'Europe/Moscow')).strftime(
            "%H:%M:%S")}\n"""
        energy_and_time[0] = energy_and_time[0] + 1
        energy_and_time[1] = energy_and_time[1] + next_time
    return int(to_user), msg


# 1-25 75к
# 26-50 80к
# 51-75 85к
# 76-100 95к
# 101-125 100к
# 126-151 105к
# 151-200 110к
# 200-250 120к
# 251-300 130к
# 301-350 140к
# 351-400 160к
# 401-450 180к
# 451 - 500 200к
# 501 - 550 225к
# 551 - 600 ????
# 601-636 275к


# Does not work yet...
def exp_to_paragon(lvl, now_exp):
    exp = -1
    # now_exp -= 6100000
    now_exp -= 14200000
    if 1 <= lvl <= 25:
        exp = now_exp - lvl * 75000
        return exp
    if 26 <= lvl <= 50:
        now_exp -= 25 * 75000
        lvl -= 25
        exp = now_exp - lvl * 80000
        return exp
    if 51 <= lvl <= 75:
        now_exp -= (25 * (75 + 80)) * 1000
        lvl -= 50
        exp = now_exp - lvl * 85000
        return exp
    if 76 <= lvl <= 100:
        now_exp -= (25 * (75 + 80 + 85)) * 1000
        lvl -= 75
        exp = now_exp - lvl * 95000
        return exp
    if 101 <= lvl <= 125:
        now_exp -= (25 * (75 + 80 + 85 + 95)) * 1000
        lvl -= 100
        exp = now_exp - lvl * 100000
        return exp
    if 126 <= lvl <= 150:
        now_exp -= (25 * (75 + 80 + 85 + 95 + 100)) * 1000
        lvl -= 125
        exp = now_exp - lvl * 105 * 1000
        return exp
    if 151 <= lvl <= 200:
        now_exp -= (25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 150
        exp = now_exp - lvl * 110 * 1000
        return exp
    if 201 <= lvl <= 250:
        now_exp -= (50 * 110 + 25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 200
        exp = now_exp - lvl * 120 * 1000
        return exp
    if 251 <= lvl <= 300:
        now_exp -= (50 * (110 + 120) + 25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 250
        exp = now_exp - lvl * 130 * 1000
        return exp
    if 301 <= lvl <= 350:
        now_exp -= (50 * (110 + 120 + 130) + 25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 300
        exp = 140000 - (lvl * 140000)
        return exp
    if 351 <= lvl <= 400:
        now_exp -= (50 * (120 + 130 + 160 + 110) + 25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 350
        exp = now_exp - lvl * 180 * 1000
        return exp
    if 401 <= lvl <= 450:
        now_exp -= (50 * (120 + 130 + 160 + 180 + 110) + 25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 400
        exp = now_exp - lvl * 200 * 1000
        return exp
    if 451 <= lvl <= 500:
        now_exp -= (50 * (110 + 120 + 130 + 160 + 180 + 200) + 25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 450
        exp = now_exp - lvl * 225 * 1000
        return exp
    if 501 <= lvl <= 551:
        now_exp -= (50 * (110 + 120 + 130 + 160 + 180 + 200 + 225) + 25 * (75 + 80 + 85 + 95 + 100 + 105)) * 1000
        lvl -= 500
        exp = now_exp - lvl * 250 * 1000
        return exp
    if 602 <= lvl <= 636:
        pass
    return exp
