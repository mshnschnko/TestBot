import multiprocessing

import telebot
import schedule
import time
import subprocess
from multiprocessing import *
import datetime
# from flask import Flask, request

token = 'TOKEN'
bot = telebot.TeleBot(token)
# app = Flask(__name__)
APP_NAME = 'secondtestbotautomati'

# def start_process():
#     p1 = Process(target=P_schedule.start_schedule, args=()).start()
#
# class P_schedule():
#     @staticmethod
#     def start_schedule():  # Запуск schedule
#         ######Параметры для schedule######
#         # p1 = Process(target=P_schedule.start_schedule, args=()).start()
#         schedule.every().day.at("17:37").do(P_schedule.send_message1())
#         schedule.every(5).seconds.do(P_schedule.send_message2())
#         while(True):
#             schedule.run_pending()
#             time.sleep(1)
#
#     @staticmethod
#     def send_message1():
#         bot.send_message('USERID', 'Отправка сообщения по времени')
#
#     @staticmethod
#     def send_message2():
#         bot.send_message('USERID', 'Отправка сообщения через определенное время')

# @bot.message_handler(content_types=['text'])
# def get_text_messages(message):
#     # global mes
#     # mes = message
#     if message.text == "/start":
#         bot.send_message(message.chat.id, "Привет, теперь тебе постоянно будут приходить сообщения")
#     else:
#         name = message.from_user.first_name
#         bot.send_message(message.chat.id, f"{name}, не балуйся!")



def start_schedule(id, i):
    # global fl
    # fl = True
    ######Параметры для schedule######
    # global job1
    # job1 = schedule.every().day.at("11:02").do(send_message1).tag('daily', '1')
    # global job2
    # job2 = schedule.every(5).seconds.do(send_message2).tag('secondly', '2')
    ##################################
    # print('sch')
    # global id
    # print(id)
    job1 = schedule.every().day.at("11:02").do(lambda: send_message1(id)).tag('daile', '1')
    job2 = schedule.every(5).seconds.do(lambda: send_message2(id)).tag('secondly', '2')
    while (True):  # Запуск цикла
        schedule.run_pending()
        time.sleep(1)



def start_process(id):  # Запуск Process
    # global fl
    # # fl = True
    # print(fl)
    # global id
    global p1
    # print('start')
    p1 = Process(target=start_schedule, args=((id, 'i')))
    p1.start()

def stop_process():
    # global fl
    # print(fl)
    # fl = False
    # print(fl)
    global p1
    p1.terminate()
    # schedule.cancel_job(job2)
    # schedule.clear('secondly')


def send_message1(id):
    # global id
    # print(id)
    bot.send_message(id, 'Отправка сообщения по времени')

def send_message2(id):
    # global id
    # print(id)
    bot.send_message(id, 'Отправка сообщения через определенное время')

# class P_schedule():  # Class для работы с schedule
#     @staticmethod
#     def start_schedule():  # Запуск schedule
#         global fl
#         print(fl)
#         ######Параметры для schedule######
#         global job1
#         job1 = schedule.every().day.at("11:02").do(P_schedule.send_message1).tag('daily', '1')
#         global job2
#         job2 = schedule.every(5).seconds.do(P_schedule.send_message2).tag('secondly', '2')
#         ##################################
#         while (fl == True):  # Запуск цикла
#             schedule.run_pending()
#             time.sleep(1)
#
#     ####Функции для выполнения заданий по времени
#     @staticmethod
#     def send_message1():
#         bot.send_message(354866247, 'Отправка сообщения по времени')
#         bot.send_message(354866247, fl)
#
#     @staticmethod
#     def send_message2():
#         bot.send_message(354866247, 'Отправка сообщения через определенное время')
#         bot.send_message(354866247, fl)
#     ################


###Настройки команд telebot#########


@bot.message_handler(content_types=['text'])
def start(message):
    global last_command
    id = str(message.chat.id)
    # print(id)
    # process = subprocess
    if (message.text == '/start'):
        if (last_command != '/start'):
            bot.send_message(message.chat.id, 'Вы подписались на рассылку сообщений о результатах работы смены. Сейчас вы начнете получать сообщения каждые 5 секунд, а также каждый день в 11:02. Чтобы отписаться, нажмите /stop.')
            # if (len(multiprocessing.active_children()) > 4):
            start_process(id)
            last_command = message.text
        else:
            bot.send_message(message.chat.id, 'Вы уже подписаны на расслыку.')
    elif (message.text == '/stop'):
        if (last_command != '/stop'):
            bot.send_message(message.chat.id, 'Вы отписались от рассылки. Чтобы подписаться снова, нажмите /start.')
            stop_process()
            last_command = message.text
        else:
            bot.send_message(message.chat.id, 'Вы ни на что не подписаны.')
    elif (message.text == '/help'):
        bot.send_message(message.chat.id, 'Для запуска напишите /start\nДля остановки напишите /stop')
        last_command = message.text
    else:
        bot.send_message(message.from_user.id, 'Неизвестная команда. Напишите /help')
        last_command = message.text

# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, 'Нажали start')
#     start_process()
#
# @bot.message_handler(commands=['stop'])
# def stop(message):
#     bot.send_message(message.chat.id, 'Нажали stop')
#     stop_process()

p1: Process
last_command: str = ' '

if (__name__ == '__main__'):
    # bot.polling(none_stop=True)
    try:
        bot.polling(none_stop=True)
    except:
        pass