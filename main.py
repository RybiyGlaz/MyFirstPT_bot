import os
import logging
import re
import subprocess

import psycopg2
from dotenv import load_dotenv
import paramiko

from telegram import Update, ForceReply, update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()

TOKEN = os.getenv("TOKEN")
RM_HOST = os.getenv("RM_HOST")
RM_PORT = os.getenv("RM_PORT")
RM_USER = os.getenv("RM_USER")
OWNER_ID = os.getenv("OWNER_ID")
RM_PASSWORD = os.getenv("RM_PASSWORD")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_REPL_USER = os.getenv("DB_REPL_USER")
DB_REPL_PASSWORD = os.getenv("DB_REPL_PASSWORD")
DB_REPL_HOST = os.getenv("DB_REPL_HOST")
DB_REPL_PORT = os.getenv("DB_REPL_PORT")

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')
def connect_to_postgresql():
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('DB_DATABASE'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return connection
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)

def ssh_connect_command(update: Update, context):
    update.message.reply_text('Введите команду, которую нужно выполнить на удаленном сервере: ')
    return 'ssh_connect'

def get_release_command(update: Update, context):
    ssh_command = "lsb_release -a"
    return execute_ssh_command(update, context, ssh_command)

def get_uname_command(update: Update, context):
    ssh_command = "uname -a"
    return execute_ssh_command(update, context, ssh_command)

def get_uptime_command(update: Update, context):
    ssh_command = "uptime -p"
    return execute_ssh_command(update, context, ssh_command)

def get_df_command(update: Update, context):
    ssh_command = "df | tail -n 20"
    return execute_ssh_command(update, context, ssh_command)

def get_free_command(update: Update, context):
    ssh_command = "free -h"
    return execute_ssh_command(update, context, ssh_command)

def get_mpstat_command(update: Update, context):
    ssh_command = "mpstat"
    return execute_ssh_command(update, context, ssh_command)

def get_w_command(update: Update, context):
    ssh_command = "w"
    return execute_ssh_command(update, context, ssh_command)

def get_auths_command(update: Update, context):
    ssh_command = "last -n 10"
    return execute_ssh_command(update, context, ssh_command)

def get_critical_command(update: Update, context):
    ssh_command = "journalctl -p crit | tail -n 5"
    return execute_ssh_command(update, context, ssh_command)

def get_ps_command(update: Update, context):
    ssh_command = "ps"
    return execute_ssh_command(update, context, ssh_command)

def get_ss_command(update: Update, context):
    ssh_command = "ss -tuln"
    return execute_ssh_command(update, context, ssh_command)

def get_apt_list_command(update: Update, context):
    update.message.reply_text("Введите 'all' для вывода всех установленных пакетов или введите название пакета для поиска информации о нем:")
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text.strip().lower()
    if user_input == 'all':
        ssh_command = "apt list --installed | tail -n 10"
    else:
        ssh_command = f"apt list --installed | grep {user_input} | tail -n 20"
    return execute_ssh_command(update, context, ssh_command)

def run_ssh_command(update: Update, context, ssh_command, host=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=int(port), username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(ssh_command)
        output = stdout.read().decode('utf-8')
        ssh.close()
        update.message.reply_text(output)
    except Exception as e:
        update.message.reply_text(f'Error executing command: {e}')

    return ConversationHandler.END

def execute_ssh_command(update: Update, context, ssh_command, host=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD):
    return run_ssh_command(update, context, ssh_command, host, port, username, password)


def get_repl_logs(update, context):
    user = update.effective_user
    command = "cat /var/log/postgresql/postgresql.log | grep repl | tail -n 15"
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or res.stderr.decode():
        update.message.reply_text("Can not open log file!")
    else:
        update.message.reply_text(res.stdout.decode().strip('\n'))

def get_services(update, context):
    return run_ssh_command(update, context, 'systemctl list-units --type=service | tail -n 20')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')
    return 'findEmail'

def findPhoneNumbers(update: Update, context):
    global cursor, connection
    user_input = update.message.text
    phone_regex = re.compile(
        r'\+7[\s-]?\(?\d{3}\)?[\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'  # для +7
        r'|8[\s-]?\(?\d{3}\)?[\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'  # для 8
        r'|8\d{10}'  # для 8XXXXXXXXXX
        r'|8\s\d{3}\s\d{3}\s\d{2}\s\d{2}'  # для 8 XXX XXX XX XX
        r'|8\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}'  # для 8 (XXX) XXX XX XX
        r'|8-\d{3}-\d{3}-\d{2}-\d{2}'  # для 8-XXX-XXX-XX-XX
        r'|\+7-\d{3}-\d{3}-\d{2}-\d{2}'  # для +7-XXX-XXX-XX-XX
    )
    phone_number_list = phone_regex.findall(user_input)

    if not phone_number_list:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END

    phone_numbers = '\n'.join(phone_number_list)
    update.message.reply_text(f'Найденные номера телефонов:\n{phone_numbers}')
    context.user_data['phone_numbers'] = phone_number_list
    # Предлагаем записать найденные номера в базу данных
    update.message.reply_text('Хотите записать найденные номера в базу данных? (Да/Нет)')
    return 'confirm_action'

def confirm_action(update: Update, context):
    global cursor, connection
    user_input = update.message.text.lower()
    if user_input == 'да':
        try:
            connection = connect_to_postgresql()
            cursor = connection.cursor()

            # Получаем найденные номера из сообщения
            phone_regex = re.compile(
                r'\+7[\s-]?\(?\d{3}\)?[\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'  # для +7
                r'|8[\s-]?\(?\d{3}\)?[\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'  # для 8
                r'|8\d{10}'  # для 8XXXXXXXXXX
                r'|8\s\d{3}\s\d{3}\s\d{2}\s\d{2}'  # для 8 XXX XXX XX XX
                r'|8\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}'  # для 8 (XXX) XXX XX XX
                r'|8-\d{3}-\d{3}-\d{2}-\d{2}'  # для 8-XXX-XXX-XX-XX
                r'|\+7-\d{3}-\d{3}-\d{2}-\d{2}'  # для +7-XXX-XXX-XX-XX
            )
            phone_number_list = phone_regex.findall(update.message.text)
            phone_number_list = context.user_data['phone_numbers']
            # Вставляем найденные номера в таблицу
            for phone_number in phone_number_list:
                cursor.execute("INSERT INTO phones (phone) VALUES (%s);", (phone_number,))
            connection.commit()

            update.message.reply_text('Номера успешно записаны в базу данных.')
        except psycopg2.Error as e:
            update.message.reply_text(f'Ошибка при записи номеров в базу данных: {e}')
        finally:
            cursor.close()
            connection.close()
    else:
        update.message.reply_text('Запись номеров в базу данных отменена.')

    return ConversationHandler.END

def findEmail(update: Update, context):
    user_input = update.message.text
    email_regex = re.compile(r'\b[A-Za-z0-9.%+-]+@[A-Za-z0-9.-]+.[A-Z|a-z]{2,}\b')
    email_list = email_regex.findall(user_input)

    if not email_list:
        update.message.reply_text('Email-адреса не найдены')
        return ConversationHandler.END

    context.user_data['email_list'] = email_list  # Сохраняем список email-адресов в контексте

    emails = '\n'.join(email_list)
    update.message.reply_text(f'Найденные email-адреса:\n{emails}')
    update.message.reply_text('Хотите записать найденные email-адреса в базу данных? (Да/Нет)')
    return 'confirm_email_addition'

def confirm_email_addition(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'да':
        email_list = context.user_data.get('email_list')
        add_emails_to_db(update, context, email_list)
    else:
        update.message.reply_text('Запись адресов отменена. Адреса не были добавлены в базу данных.')

    return ConversationHandler.END

def add_emails_to_db(update, context, email_list):
    try:
        connection = connect_to_postgresql()
        cursor = connection.cursor()

        # Insert the found email addresses into the table
        for email in email_list:
            cursor.execute("INSERT INTO emails (email) VALUES (%s);", (email,))
        connection.commit()

        update.message.reply_text('Адреса записаны.')
    except psycopg2.Error as e:
        update.message.reply_text(f'Ошибка записи адресов: {e}')
    finally:
        cursor.close()
        connection.close()

    return ConversationHandler.END

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки на сложность:')
    return 'verifyPassword'

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
def get_emails(update, context):
    global connection, cursor
    try:
        connection = connect_to_postgresql()
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails;")
        emails = cursor.fetchall()
        email_list = [email[0] for email in emails]
        email_text = "\n".join(email_list)
        update.message.reply_text(f"Email addresses:\n{email_text}")
    except psycopg2.Error as e:
        update.message.reply_text(f'Error retrieving email addresses: {e}')
    finally:
        cursor.close()
        connection.close()
def get_phone_numbers(update, context):
    global connection, cursor
    try:
        connection = connect_to_postgresql()
        cursor = connection.cursor()
        cursor.execute("SELECT phone FROM phones;")
        phone_numbers = cursor.fetchall()
        phone_number_list = [phone[0] for phone in phone_numbers]
        phone_number_text = "\n".join(phone_number_list)
        update.message.reply_text(f"Phone numbers:\n{phone_number_text}")
    except psycopg2.Error as e:
        update.message.reply_text(f"Error retrieving phone numbers: {e}")
    finally:
        cursor.close()
        connection.close()

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'confirm_action': [MessageHandler(Filters.text & ~Filters.command, confirm_action)]
        },
        fallbacks=[]
    )

    conv_handler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verifyPassword', verifyPasswordCommand)],
        states={'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)]},
        fallbacks=[]
    )

    # Обработчик диалога для поиска email-адресов
    conv_handler_find_email = ConversationHandler(
        entry_points=[CommandHandler('findEmail', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'confirm_email_addition': [MessageHandler(Filters.text & ~Filters.command, confirm_email_addition)],
        },
        fallbacks=[]
    )

    conv_handler_get_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)]},
        fallbacks=[]
    )
    dp.add_handler(conv_handler_get_apt_list)

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(conv_handler_find_email)
    dp.add_handler(conv_handler_verify_password)
    dp.add_handler(CommandHandler("ssh_connect", ssh_connect_command))
    dp.add_handler(CommandHandler("get_release", get_release_command))
    dp.add_handler(CommandHandler("get_uname", get_uname_command))
    dp.add_handler(CommandHandler("get_uptime", get_uptime_command))
    dp.add_handler(CommandHandler("get_df", get_df_command))
    dp.add_handler(CommandHandler("get_free", get_free_command))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat_command))
    dp.add_handler(CommandHandler("get_w", get_w_command))
    dp.add_handler(CommandHandler("get_auths", get_auths_command))
    dp.add_handler(CommandHandler("get_critical", get_critical_command))
    dp.add_handler(CommandHandler("get_ps", get_ps_command))
    dp.add_handler(CommandHandler("get_ss", get_ss_command))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list_command))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
