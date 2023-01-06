import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))           # Charge le fichier .env

# Jeu d'instruction qui sont défini AVANT que l'app soit en live
class Config(object):
    # Si l'environnement ne définit pas de variable, le hardcoded string 
    # sera utilisé
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
                 os.getenv('SECRET_KEY')
    
    # Localisation du database de l'application...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + \
                              os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email à envoyer à l'admin lors d'une erreur
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT')) or os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMINS = ['your-email@example.com']
    POSTS_PER_PAGE = 4
    LANGUAGES = ['en', 'fr', 'es']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY') or \
                        os.getenv('MS_TRANSLATOR_KEY')
    