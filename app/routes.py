from requests import request
from app import app
from flask import jsonify, url_for, render_template, request, flash, redirect
from app.forms import ScrapForm
from app.modules import mlscraping

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ScrapForm()
    if request.method == 'GET':
        return render_template('index.html', title='Inicio | MELI-Scrapper', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            term_to_search = form.term.data
            links = mlscraping.get_list('https://listado.mercadolibre.com.uy', term_to_search)
        
            if len(links) is not None:
                products = mlscraping.makeScrap(links)
                return render_template('index.html', products=products, form=form)
            
        flash('Debe introducir un termino para realizar la busqueda.')
        return redirect(url_for('index'))