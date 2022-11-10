from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Ici on retrouve les objets qui représente les extensions !
# __name__ : nom du module qui est 'app'. 'app' ici est une instance 
# de la classe Flask qui créer l'application simplement
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

# L'url 'login' si n'est pas connecté
login.login_view = 'login'

# L'importation de routes ici évite le phénomène d'importations
# circulaires
from app import routes, models