import click
import os

def register(app):
    # Groupe d'application 'translate' et que l'on va ensuite ajouter des 
    # applications/commandes tel que 'init', 'update', etc.
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass


    # (venv) $ flask translate init <LANG>
    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel init -i messages.pot -d app/translations -l ' 
                    + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')


    # (venv) $ flask translate update
    @translate.command()
    def update():
        """Update all languages."""
        # Si retourne 0, commande exécuté sans erreur
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')


    # (venv) $ flask translate compile
    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')