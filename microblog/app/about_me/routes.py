from flask import render_template
from app.about_me import bp


@bp.route('/about_me')
def about_me():
    return render_template('about_me/about_me.html')