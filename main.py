import multiprocessing
from pickle import FALSE, TRUE
import numpy

import telebot
import schedule
import time
from telebot import types
from multiprocessing import *
import db_manager
# from flask import Flask, request

token = 'TOKEN'
bot = telebot.TeleBot(token)
# app = Flask(__name__)
APP_NAME = 'secondtestbotautomati'
password = '123'
conn = db_manager.con_to_db()

def start_schedule(id, line, process_id):
    job1 = schedule.every().day.at("11:02").do(lambda: send_message2(id)).tag('daily', '1')
    job2 = schedule.every(5).seconds.do(lambda: send_message2(id)).tag('secondly', '2')
    res = db_manager.search_user(conn, id)
    if (res == 0):
        db_manager.add_active_user(conn, id, line, process_id, '/start')
    else:
        db_manager.update_status(conn, id, line, process_id, '/start')
    while (True):  # Запуск цикла
        schedule.run_pending()
        time.sleep(1)

permission = True

def start_process(id, line):  # Запуск Process
    global process_list
    global p
    free_proc_id = len(process_list)
    p = Process(target=start_schedule, args=((id, line, free_proc_id)))
    global permission
    if (permission):
        process_list.append(p)
        p.start()

def stop_process(id):
    global process_list
    res = db_manager.search_user(conn, id)
    proc_id = res[2]
    p1 = process_list[proc_id]
    p1.terminate()
    process_list.pop(proc_id)


def send_message1(id):
    search_res = db_manager.search_user(conn, id)
    line = search_res[1]
    bot.send_message(id, f'Отправка сообщения по времени. Ваш город - {line}')

def send_message2(id):
    search_res = db_manager.search_user(conn, id)
    line = search_res[1]
    info_res = db_manager.select_efficiency(conn, line)
    if (info_res == 0):
        bot.send_message(id, f'Данные о показателях эффективности на данной линии отсутствуют')
        db_manager.update_status(conn, id, search_res[1], search_res[2], '/stop')
        stop_process(id)
        global permission
        permission = False
    else:
        for i in range (numpy.shape(info_res)[0]):
            assessment = '🟢'
            total = info_res[i][2]
            defects = info_res[i][3]
            efficiency = (total - defects) / total * 100
            efficiency_str = format(efficiency, '.2f')
            if (efficiency < 90):
                assessment = '🔴'
            bot.send_message(id, f'Линия: {line}\nВсего произведено: {total}\nБрак: {defects}\nЭффективность: {efficiency_str}{assessment}')


@bot.message_handler(content_types=['text'])
def start(message):

    global last_command
    id = int(message.chat.id)
    res1 = db_manager.search_user(conn, id)
    if (res1 == 0):
        print('sas')
        db_manager.add_active_user(conn, id, 'null', 0, '/stop')
    if (db_manager.is_logged(conn, id)):
        if (message.text == '/start'):
            search_res = db_manager.search_user(conn, id)
            if (search_res == 0 or search_res[3] == '/stop'):
                last_command = message.text
                bot.send_message(message.chat.id, 'Вы подписались на рассылку сообщений о результатах работы смены. Теперь вам будут приходить результаты работы выбранной линии в конце каждой рабочей смены. Чтобы отписаться, нажмите /stop.')

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                Hanky_btn = types.KeyboardButton("HANKY")
                Facial_btn = types.KeyboardButton("FACIAL")
                Both_btn = types.KeyboardButton("Обе линии")
                markup.add(Hanky_btn, Facial_btn, Both_btn)
                bot.send_message(message.chat.id, 'Выберите линию.', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Вы уже подписаны на расслыку.')
        elif (message.text == '/stop'):
            search_res = db_manager.search_user(conn, id)
            if (search_res == 0 or search_res[3] == '/stop'):
                bot.send_message(message.chat.id, 'Вы ни на что не подписаны. Чтобы подписаться на информационную рассылку, нажмите /start.')
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                Hanky_btn = types.KeyboardButton("HANKY")
                Facial_btn = types.KeyboardButton("FACIAL")
                Both_btn = types.KeyboardButton("Обе линии")
                markup.add(Hanky_btn, Facial_btn, Both_btn)
                bot.send_message(message.chat.id, 'Вы отписались от рассылки. Чтобы подписаться снова, нажмите /start или сразу выберете линию', reply_markup=markup)
                db_manager.update_status(conn, id, search_res[1], search_res[2], '/stop')
                stop_process(id)
                
                last_command = message.text

        elif (message.text == '/help'):
            bot.send_message(message.chat.id, 'Для запуска напишите /start\nДля остановки напишите /stop\nДля выхода из учетной записи напишите /logout')
            last_command = message.text
        elif (message.text == 'HANKY' or message.text == 'FACIAL' or message.text == 'Обе линии' or message.text == 'жопа'):
            search_res = db_manager.search_user(conn, id)
            if (search_res == 0 or search_res[3] == '/stop'):
                line = message.text
                if (message.text == 'HANKY' or message.text == 'FACIAL' or message.text == 'жопа'):
                    bot.send_message(message.chat.id, f"Вы выбрали линию {line}.")
                    start_process(id, line)
                elif (message.text == 'Обе линии'):
                    bot.send_message(message.chat.id, f"Вы выбрали обе линии.")
                    start_process(id, line)
            else:
                bot.send_message(message.chat.id, 'Вы уже подписаны на расслыку.')
        elif (message.text == '/logout'):
            res = db_manager.search_user(conn, id)
            if (res == 0 or res[3] == '/stop'):
                db_manager.update_log_in(conn, id, 'false')
                db_manager.update_tried_to_log(conn, id, 'false')
                bot.send_message(message.chat.id, 'Вы вышли из учетной записи. Для повторного входа отправьте любое сообщение.')
            else:
                bot.send_message(message.chat.id, 'Нельзя выйти из учетной записи до завершения процесса рассылки. Для остановки рассылки напишите /stop')
        else:
            bot.send_message(message.from_user.id, 'Неизвестная команда. Напишите /help')
            last_command = message.text
    else:
        if (db_manager.is_tried_to_log(conn, id) == 0):
            bot.send_message(message.chat.id, 'Введите пароль. В целях Вашей же безопасности сообщения с вводами пароля будут удалены.')
            db_manager.update_tried_to_log(conn, id, 'true')
        elif (message.text == password):
            db_manager.update_log_in(conn, id, 'true')
            bot.send_message(message.chat.id, 'Пароль успешно введен.\nДля запуска напишите /start\nДля остановки напишите /stop\nДля выхода из учетной записи напишите /logout')
            bot.delete_message(message.chat.id, message.message_id)
        else:
            bot.send_message(message.chat.id, 'Неверный пароль, попробуйте еще раз')
            bot.delete_message(message.chat.id, message.message_id)


p: Process
process_list = []
last_command: str = ' '

if (__name__ == '__main__'):
    try:
        db_manager.create_table_users(conn)
        bot.polling(none_stop=True)
    except:
        pass
    finally:
        conn.close()