import random
import config
import help_func
import database_functions
import time
import telebot


def generate_main_castle_msg(bot, message, castle):
    try:
        msg = f'Воины, вас призвали на битву в замок {castle}\nПрисылайте форварды с вашим выходом и приходом в замок' \
              f' в чат!!!\n===+++===\n'
        new_id = bot.send_message(message.chat.id, msg)
        bot.pin_chat_message(message.chat.id, new_id.message_id, False)
    except:
        pass


def edit_castle_pin(bot, message, txt):
    try:
        chat_info = bot.get_chat(message.chat.id)
        pinned_castle_msg_id = None
        pinned_castle = None
        pin_txt = None
        if chat_info.pinned_message is not None:
            if chat_info.pinned_message.from_user.is_bot is True:
                pinned_castle_msg_id = chat_info.pinned_message.message_id
                pin_txt = chat_info.pinned_message.text
                pinned_castle = pin_txt[pin_txt.find('на битву в замок ') + len('на битву в замок '):
                                        pin_txt.find('\nПрисылайте')]
            gamename = database_functions.get_name(message.from_user.id)
            if gamename is not None:
                gamename = str(gamename[0])
            elif gamename is None:
                bot.send_message(message.chat.id, 'МНЕ НУЖЕН ТВОЙ ПРОФИЛЬ', reply_to_message_id=message.message_id)
                return 0
            msg = chat_info.pinned_message.text
            if 'Ты направляешься в замок' in txt:
                to_castle = txt[txt.find('Ты направляешься в замок ') +
                                len('Ты направляешься в замок '):txt.find('🐾, прибудешь')]
                if txt.find(str(gamename)) == -1 and (to_castle == pinned_castle):
                    add_msg = f'\n{gamename} 🐾 бои: 0/0'
                    if pin_txt.find('====💃====') != -1:
                        txt = msg[0:(msg.find('====💃====') - 1)] + add_msg + '\n' + msg[msg.find('====💃===='):]
                    else:
                        txt = chat_info.pinned_message.text + add_msg
                    bot.delete_message(message.chat.id, message.message_id)
                    bot.edit_message_text(txt, message.chat.id, pinned_castle_msg_id)
            elif 'Ты прибыл в замок, бой будет проходить автоматически!' in txt:
                # bot.send_message(message.chat.id, message)
                if gamename in pin_txt:
                    left = pin_txt.find(f'{gamename} ') + len(f'{gamename} ')
                    now_icon = pin_txt[left:pin_txt.find(' ', left)]
                    if now_icon == '🐾':
                        new_msg = pin_txt[0:left] + '🌚' + pin_txt[pin_txt.find(' ', left)::]
                        # message.text = new_msg
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.edit_message_text(new_msg, message.chat.id, pinned_castle_msg_id)
                elif txt.find(gamename) == -1:
                    bot.reply_to(message, 'А ты точно кидал сообщение о выходе?🤔')
    except:
        pass


def fight_editor(bot, message):
    try:
        chat_info = bot.get_chat(message.chat.id)
        pinned_castle_msg_id = None
        pinned_castle = None
        pin_txt = None

        if chat_info.pinned_message is not None:
            if chat_info.pinned_message.from_user.is_bot is True:
                pinned_castle_msg_id = chat_info.pinned_message.message_id
                pin_txt = str(chat_info.pinned_message.text)
                pinned_castle = pin_txt[pin_txt.find('на битву в замок ') + len('на битву в замок '):
                                        pin_txt.find('\nПрисылайте')]
        txt = message.text
        first = database_functions.get_name(message.from_user.id)
        second, end_type, win_count, loose_count = None, None, None, None
        if first is not None:
            first = str(first[0])
        elif first is None:
            bot.send_message(message.chat.id, 'МНЕ НУЖЕН ТВОЙ ПРОФИЛЬ', reply_to_message_id=message.message_id)
            return 0
        if first in pin_txt:
            if 'Ты одержал победу над ' in txt:
                left = txt.find('Ты одержал победу над ') + len('Ты одержал победу над ')
                second = txt[txt.find(']', left) + 1:txt.find(' (+')]
                end_type = 'win'
            elif 'Ты ☠пал от рук ' in txt:
                left = txt.find('Ты ☠пал от рук ') + len('Ты ☠пал от рук ')
                second = str(txt[txt.find(']', left) + 1:txt.find(' (-')])
                end_type = 'loose'
            if pin_txt.find('====💃====') == -1:
                pin_txt += '\n====💃===='
                pin_txt += f'\n{second} бои: 0/0'
            if second not in pin_txt:
                pin_txt += f'\n{second} бои: 0/0'
            left_f = pin_txt.find(first)
            first_w_l = pin_txt[left_f + len(first) + len(' 🌚 бои: '):pin_txt.find('\n', left_f)].split('/')
            left_s = pin_txt.find(second)
            if pin_txt.find('\n', left_s) != -1:
                second_w_l = pin_txt[left_s + len(second) + len(' бои: '):pin_txt.find('\n', left_s)].split('/')
            else:
                second_w_l = pin_txt[left_s + len(second) + len(' бои: '):].split('/')
            if pin_txt.find('🐾', left_f, pin_txt.find('\n', left_f)) != -1:
                icon = '🐾'
            else:
                icon = '🌚'
            first_repl_str = f'{first} {icon} бои: {first_w_l[0]}/{first_w_l[1]}'
            second_repl_str = f'{second} бои: {second_w_l[0]}/{second_w_l[1]}'

            if end_type == 'win':
                first_w_l[0] = int(first_w_l[0]) + 1
                second_w_l[1] = int(second_w_l[1]) + 1
            else:
                first_w_l[1] = int(first_w_l[1]) + 1
                second_w_l[0] = int(second_w_l[0]) + 1

            ned_f = f'{first} {icon} бои: {first_w_l[0]}/{first_w_l[1]}'
            ned_s = f'{second} бои: {second_w_l[0]}/{second_w_l[1]}'
            new_msg = pin_txt.replace(first_repl_str, ned_f)
            new_msg = new_msg.replace(second_repl_str, ned_s)
            bot.delete_message(message.chat.id, message.message_id)
            bot.edit_message_text(new_msg, message.chat.id, pinned_castle_msg_id)
            # bot.send_message(message.chat.id, new_msg)
        else:
            bot.send_message(message.chat.id, f'Ты ТОЧНО вышел в замок {pinned_castle}?')
    except:
        pass
