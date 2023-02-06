import json
from app.models import BusinessMontreal
from app.api import bp
from app.api.forms import SearchForm
from flask import render_template, redirect, url_for, flash, request, Response

@bp.route('/map', methods=['GET', 'POST'])
def map():
    form = SearchForm(request.form)
    search = request.args.get('search')
    #print(all)
    
    if form.validate_on_submit():
        search2 = BusinessMontreal.query.filter_by(name=form.search.data).first()
        if search2 is None:
            flash('Data not found!')
        else:
            flash('Your search is successful!')
        return redirect(url_for('api.map'))
        
    return render_template('api/map.html', title="Map", form=form)

@bp.route('/search', methods=['GET'])
def search():
    all = BusinessMontreal.query.all()
    #all_businesses = [r.as_dict() for r in all]
    #print(all_businesses)
    values = [str(value) for value in all]
    #test = list(all)
    #print(values)
    #print(type(test[0]))
    return Response(json.dumps(values), mimetype='application/json')

"""
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