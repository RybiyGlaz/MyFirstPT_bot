import logging
import re
import os
import subprocess

import psycopg2
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext
from utilities import run_ssh_command, connect_to_postgresql


PHONE_REGEX = re.compile(
    r'\+7[\s-]?\(?\d{3}\)?[\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'  # для +7
    r'|8[\s-]?\(?\d{3}\)?[\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'  # для 8
    r'|8\d{10}'  # для 8XXXXXXXXXX
    r'|8\s\d{3}\s\d{3}\s\d{2}\s\d{2}'  # для 8 XXX XXX XX XX
    r'|8\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}'  # для 8 (XXX) XXX XX XX
    r'|8-\d{3}-\d{3}-\d{2}-\d{2}'  # для 8-XXX-XXX-XX-XX
    r'|\+7-\d{3}-\d{3}-\d{2}-\d{2}'  # для +7-XXX-XXX-XX-XX
)

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    return 'findEmail'

def findPhoneNumberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска номеров телефонов: ')
    return 'findPhoneNumber'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки на сложность:')
    return 'verifyPassword'

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'8 \(\d{3}\) \d{3}-\d{2}-\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return

    phoneNumbers = '\n'.join(f'{i + 1}. {num}' for i, num in enumerate(phoneNumberList))
    update.message.reply_text(phoneNumbers)
    return ConversationHandler.END

def findEmail(update: Update, context):
    user_input = update.message.text
    email_list = EMAIL_REGEX.findall(user_input)

    if not email_list:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END

    emails = '\n'.join(f'{i + 1}. {email}' for i, email in enumerate(email_list))
    update.message.reply_text(emails)
    context.user_data['emails'] = email_list
    update.message.reply_text('Желаете внести в базу данных? Да или Нет')
    return 'db_insert_emails'

def db_insert_emails(update, context):
    user_input = update.message.text.lower()
    if user_input == 'да':
        try:
            with connect_to_postgresql() as conn, conn.cursor() as cursor:
                emails_list = context.user_data.get('emails', [])
                for email in emails_list:
                    cursor.execute("INSERT INTO emails (email) VALUES (%s);", (email,))
                conn.commit()

                update.message.reply_text('Адреса успешно записаны в базу данных.')
        except psycopg2.Error as e:
            update.message.reply_text(f'Ошибка при записи почтовых адресов в базу данных: {e}')
            logging.error(f'Error: {e}')
    else:
        update.message.reply_text('Отмена записи...')
    return ConversationHandler.END

def findPhoneNumber(update: Update, context):
    user_input = update.message.text
    phone_number_list = PHONE_REGEX.findall(user_input)

    if not phone_number_list:
        update.message.reply_text('Номера телефонов не найдены')
        return ConversationHandler.END

    phone_numbers = '\n'.join(f'{i + 1}. {num}' for i, num in enumerate(phone_number_list))
    update.message.reply_text(phone_numbers)
    context.user_data['phone_numbers'] = phone_number_list
    update.message.reply_text('Желаете внести в базу данных? Да или Нет')
    return 'db_insert_phones'

def db_insert_phones(update, context):
    user_input = update.message.text.lower()
    if user_input == 'да':
        try:
            # Используем контекстный менеджер для управления подключением и курсором.
            with connect_to_postgresql() as conn, conn.cursor() as cursor:
                phone_number_list = context.user_data.get('phone_numbers', [])

                # Пакетная вставка номеров телефонов
                for phone_number1 in phone_number_list:
                    cursor.execute("INSERT INTO phones (phone) VALUES (%s);", (phone_number1,))
                conn.commit()

                update.message.reply_text('Номера успешно записаны в базу данных.')
        except psycopg2.Error as e:
            update.message.reply_text(f'Ошибка при записи номеров в базу данных: {e}')
            logging.error(f'Error: {e}')
    else:
        update.message.reply_text('Отмена записи...')
    return ConversationHandler.END

def verifyPassword(update: Update, context):
    user_input = update.message.text
    pattern = re.compile(
        r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}$"
    )
    if pattern.match(user_input):
        update.message.reply_text('Ваш пароль сложный')
    else:
        update.message.reply_text('Ваш пароль простой')
    return ConversationHandler.END

def get_release(update, context):
    run_ssh_command(update, context, 'Версия', 'lsb_release -a')

def get_uname(update, context):
    run_ssh_command(update, context, 'Информация', 'uname -a')

def get_uptime(update, context):
    run_ssh_command(update, context, 'Uptime', 'uptime -p')

def get_df(update, context):
    run_ssh_command(update, context, 'Информация о файловой системе', 'df | tail -n 5')

def get_free(update, context):
    run_ssh_command(update, context, 'Информация об оперативной памяти', 'free')

def get_mpstat(update, context):
    run_ssh_command(update, context, 'Информация о производительности системы', 'mpstat')

def get_w(update, context):
    run_ssh_command(update, context, 'Информация о работающих в данной системе пользователях', 'w')

def get_auths(update, context):
    run_ssh_command(update, context, 'Последние 10 входов в систему', 'last -n 10')

def get_critical(update, context):
    run_ssh_command(update, context, 'Последние 5 критических события',
                    'journalctl -p crit | tail -n 5')

def get_ps(update, context):
    run_ssh_command(update, context, 'Текущие процессы в системе', 'ps | tail -n 10')

def get_ss(update, context):
    run_ssh_command(update, context, 'Сбор информации об используемых портах',
                    'ss | tail -n 10')


SEARCH_PACKAGE = 0  # Костыль: состояние для поиска пакета.
def get_apt_list(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Введите название пакета для поиска или отправьте 'all' для вывода всех установленных пакетов."
    )
    return SEARCH_PACKAGE

def get_specific_package(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()
    if user_input.lower() == 'all':
        command = 'apt list --installed | tail -n 10'
    else:
        command = f"apt list --installed | grep {user_input} | tail -n 20"

    run_ssh_command(update, context, 'Результат поиска', command)
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def get_services(update, context):
    run_ssh_command(update, context, 'Информация о сервисах (20 строчек)',
                    'systemctl list-units --type=service | tail -n 20')

def get_repl_logs(update, context):
    user = update.effective_user
    command = "cat /var/log/postgresql/postgresql.log | grep repl | tail -n 15"
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or res.stderr.decode():
        update.message.reply_text("Can not open log file!")
    else:
        update.message.reply_text(res.stdout.decode().strip('\n'))


def get_emails(update, context):
    cursor, connection = None, None
    try:
        connection = connect_to_postgresql()
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails;")
        emails = cursor.fetchall()
        email_list = [email[0] for email in emails]
        email_text = "\n".join(email_list)
        update.message.reply_text(f"Email адреса:\n{email_text}")
    except psycopg2.Error as e:
        update.message.reply_text(f'Возникли ошибки: {e}')
        logging.error(f'Error: {e}')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_phone_numbers(update, context):
    cursor, connection = None, None
    try:
        connection = connect_to_postgresql()
        cursor = connection.cursor()
        cursor.execute("SELECT phone FROM phones;")
        phone_numbers = cursor.fetchall()
        phone_number_list = [phone[0] for phone in phone_numbers]
        phone_number_text = "\n".join(phone_number_list)
        update.message.reply_text(f"Номера телефонов:\n{phone_number_text}")
    except psycopg2.Error as e:
        update.message.reply_text(f'Возникли ошибки: {e}')
        logging.error(f'Error: {e}')
    finally:
        cursor.close()
        connection.close()

def echo(update: Update, context):
    update.message.reply_text(update.message.text)
