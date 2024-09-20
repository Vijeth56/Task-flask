import os
 
class Config:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Vij@1234')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'lilly')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')