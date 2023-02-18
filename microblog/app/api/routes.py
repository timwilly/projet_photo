import json
from app.models import BusinessMontreal
from app.api import bp
from app.api.forms import SearchForm
from flask import render_template, redirect, url_for, flash, request, Response
from itertools import islice
from json import JSONEncoder
from sqlalchemy import asc


@bp.route('/map', methods=['GET', 'POST'])
def map():
    form = SearchForm(request.form)
    result_name = request.args.get('result_name')
    if form.validate_on_submit():
        result = BusinessMontreal.query.filter_by(name=form.search.data) \
                 .first()
        if result is None:
            flash('Data not found!')
        else:
            flash('Your search is successful!')
        return redirect(url_for('api.map', result_name=result.name))
    result = BusinessMontreal.query.filter_by(name=result_name).order_by \
                              (BusinessMontreal.date_statut.asc())
    for r in result:
        print(r.date_statut)
    return render_template('api/map.html', title="Map", form=form,
                           result=result)

@bp.route('/search', methods=['GET'])
def search():
    all = BusinessMontreal.query.all()
    values = list(set([str(value) for value in all]))

    return Response(json.dumps(values), mimetype='application/json')

"""
src = ['foo', 'bar', 'foobar', 'bar', 'barfoo']
tree = create(src)
print_tree(tree)

for word in src:
    print('search {0}, result: {1}'.format(word, search(tree, word)))

@bp.route('/process', methods=['POST'])
def process():
    search = request.form['search']
    if search:
        return jsonify({'name':search})
    return jsonify({'error': 'missing data..'})

@bp.route('/business', methods=["GET", "POST"])
def get_business_json():
    name = request.args.get("arrondissement")
  
    if not installations:
        return jsonify({'Erreur': 'Aucune installation trouvé'})

    return jsonify({'Installations': installations})
    """