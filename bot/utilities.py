import paramiko
import os

import psycopg2
from dotenv import load_dotenv
import logging


class SSHClientManager:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv('RM_HOST')
        self.port = os.getenv('RM_PORT')
        self.username = os.getenv('RM_USER')
        self.password = os.getenv('RM_PASSWORD')
        self.client = None

    def __enter__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.username, password=self.password, port=self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        data = stdout.read() + stderr.read()
        return data.decode('utf-8')

def run_ssh_command(update, context, command_desc, command):
    with SSHClientManager() as ssh_manager:
        try:
            request = ssh_manager.execute_command(command)
            update.message.reply_text(f'{command_desc}:\n{request}')
        except Exception as e:
            update.message.reply_text(f'Ошибка при выполнении команды: {e}')
            logging.error(f'Error: {e}')

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
       logging.error(f'Ошибка подключения к PostgresSQL: {e}')
