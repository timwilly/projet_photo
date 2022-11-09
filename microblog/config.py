import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Si l'environnement ne définit pas de variable, le hardcoded string 
    # sera utilisé
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MOTDEPASSESUPERSECRETLA'
    
    # Localisation du database de l'application...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + \
                              os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False