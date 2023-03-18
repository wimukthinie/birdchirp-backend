import os

from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = ''
MYSQL_DB = os.getenv('MYSQL_DB')
SECRET_SALT_KEY = os.getenv('HASH_SECRET_KEY')
