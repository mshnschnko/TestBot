import imp
import multiprocessing
from pickle import FALSE, TRUE

import telebot
import schedule
import time
from telebot import types
import subprocess
from multiprocessing import *
import db_manager
from psycopg2 import Error
import datetime
# from flask import Flask, request

token = 'TOKEN'
bot = telebot.TeleBot(token)
# app = Flask(__name__)
APP_NAME = 'secondtestbotautomati'
password = '123'
conn = db_manager.con_to_db()

def start_schedule(id, region, process_id):
    job1 = schedule.every().day.at("11:02").do(lambda: send_message2(id)).tag('daily', '1')
    job2 = schedule.every(5).seconds.do(lambda: send_message2(id)).tag('secondly', '2')
    res = db_manager.search_user(conn, id)
    if (res == 0):
        db_manager.add_active_user(conn, id, region, process_id, '/start')
    else:
        db_manager.update_status(conn, id, region, process_id, '/start')
    while (True):  # Запуск цикла
        schedule.run_pending()
        time.sleep(1)



def start_process(id, region):  # Запуск Process
    global process_list
    global p
    free_proc_id = len(process_list)
    p = Process(target=start_schedule, args=((id, region, free_proc_id)))
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
    region = search_res[1]
    bot.send_message(id, f'Отправка сообщения по времени. Ваш город - {region}')

def send_message2(id):
    search_res = db_manager.search_user(conn, id)
    region = search_res[1]
    info_res = db_manager.select_efficiency(conn, region)
    if (info_res == 0):
        bot.send_message(id, f'Данные о показателях эффективности в данном регионе отсутствуют')
    else:
        total = info_res[2]
        defects = info_res[3]
        efficiency = format((total - defects) / total * 100, '.2f')
        bot.send_message(id, f'Фабрика: {region}\nВсего произведено: {total}\nБрак: {defects}\nЭффективность: {efficiency}')


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
                bot.send_message(message.chat.id, 'Вы подписались на рассылку сообщений о результатах работы смены. Сейчас вы начнете получать сообщения каждые 5 секунд, а также каждый день в 11:02. Чтобы отписаться, нажмите /stop.')

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                Tula_btn = types.KeyboardButton("Тула")
                SaintP_btn = types.KeyboardButton("Питер")
                Pskov_btn = types.KeyboardButton("Псков")
                markup.add(Tula_btn, SaintP_btn, Pskov_btn)
                bot.send_message(message.chat.id, 'Выберите регион.', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Вы уже подписаны на расслыку.')
        elif (message.text == '/stop'):
            search_res = db_manager.search_user(conn, id)
            if (search_res == 0 or search_res[3] == '/stop'):
                bot.send_message(message.chat.id, 'Вы ни на что не подписаны. Чтобы подписаться на информационную рассылку, нажмите /start.')
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                Tula_btn = types.KeyboardButton("Тула")
                SaintP_btn = types.KeyboardButton("Питер")
                Pskov_btn = types.KeyboardButton("Псков")
                markup.add(Tula_btn, SaintP_btn, Pskov_btn)
                bot.send_message(message.chat.id, 'Вы отписались от рассылки. Чтобы подписаться снова, нажмите /start или сразу выберете город', reply_markup=markup)
                db_manager.update_status(conn, id, search_res[1], search_res[2], '/stop')
                stop_process(id)
                
                last_command = message.text

        elif (message.text == '/help'):
            bot.send_message(message.chat.id, 'Для запуска напишите /start\nДля остановки напишите /stop\nДля выхода из учетной записи напишите /logout')
            last_command = message.text
        elif (message.text == 'Тула' or message.text == 'Питер' or message.text == 'Псков'):
            search_res = db_manager.search_user(conn, id)
            if (search_res == 0 or search_res[3] == '/stop'):
                region = message.text
                bot.send_message(message.chat.id, f"Вы выбрали регион {region}")
                start_process(id, region)
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
            bot.send_message(message.chat.id, 'Введите пароль')
            db_manager.update_tried_to_log(conn, id, 'true')
        elif (message.text == password):
            db_manager.update_log_in(conn, id, 'true')
            bot.send_message(message.chat.id, 'Пароль успешно введен.\nДля запуска напишите /start\nДля остановки напишите /stop\nДля выхода из учетной записи напишите /logout')
        else:
            bot.send_message(message.chat.id, 'Неверный пароль, попробуйте еще раз')


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