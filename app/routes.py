from audioop import avg
from requests import request
from app import app
from flask import jsonify, url_for, render_template, request, flash, redirect
from app.forms import ScrapForm
from app.modules import mlscraping
import numpy as np

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
                avg_sales = round(np.mean([int(k['sells']) for k in products if k['sells'] is not None]))
                avg_price = round(np.mean([int(k['price'].replace('.','')) for k in products if k['price'] is not None]))
                # avg_rating = round(np.mean([int(k['price']) for k in products if k['price'] is not None]))
                
                return render_template('index.html', products=products, form=form, avg_sales=avg_sales, avg_price=avg_price)
            
        flash('Debe introducir un termino para realizar la busqueda.')
        return redirect(url_for('index'))