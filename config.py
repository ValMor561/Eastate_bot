import configparser
from distutils.util import strtobool

#Чтение конфигурационного файла
def get_config(filename):
    config = configparser.ConfigParser()
    config.read(filename, encoding="utf-8")

    return config

#Функция для считывания значений из файла если он указан в качестве параметра, либо из .ini файла
#На вход подается значение хранящееся в конфиге
def get_multiple_values(param):
    if ".txt" in param:
        with open(param, encoding = 'utf-8', mode = 'r') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    return param.replace(" ", "").split(',')

config = get_config('config.ini')

#Глобальные переменные всех параметров
BOT_TOKEN = config['DEFAULT']['bot_token']
CHANELL_ID = config['DEFAULT']['channel_id']
CHANELL_URL = config['DEFAULT']['channel_url']
ADMINS = get_multiple_values(config['DEFAULT']['admins'])
HOST=config['BD']['host']
DATABASE=config['BD']['database']
USER=config['BD']['user']
PASSWORD=config['BD']['password']
