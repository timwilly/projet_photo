# Importe l'instance de l'application app
from app import app, db, cli
from app.models import User, Post

# Crée un contexte shell qui ajoute les instances des données et modèles...
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}