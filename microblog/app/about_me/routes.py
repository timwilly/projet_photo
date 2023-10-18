from flask import render_template, url_for
from app.about_me import bp


@bp.route('/about_me')
def about_me():
    image_file_me = url_for('static', filename='pictures/willy.JPG')
    return render_template('about_me/about_me.html', 
                           image_file_me=image_file_me)