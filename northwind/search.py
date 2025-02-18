from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, render_template_string
)
from werkzeug.exceptions import abort

from northwind.db import get_db

bp = Blueprint('search', __name__)



@bp.route('/', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        item = request.form['search']
        
        return redirect(url_for('search.display_search', item=item))
    else:
        return render_template('index.html')

def get_product(item):
    db = get_db()
    product = db.execute(
            'SELECT ProductName, UnitPrice'
            ' FROM Product'
            ' WHERE ProductName = ? COLLATE NOCASE', (item,)
        ).fetchall()

    product_type = db.execute(
            'SElECT ProductName, UnitPrice'
            ' FROM Product, Category'
            ' WHERE CategoryName = ? COLLATE NOCASE'
            ' AND Category.id = Product.CategoryId ', (item,)
        ).fetchall()

    if not product and not product_type:
        return None
    if not product_type:
        return product
    return product_type

@bp.route('/search/', methods=('GET', 'POST'))
def display_search():
    if request.method == 'POST':
        item = request.form['search']
        if item:
            return redirect(url_for('search.display_search', item=item))
        # want to reroute to a product page if clicked on product name
        # want to add to cart if clicked 'add to cart'
        
    
    # logic to display correct page
    item = request.args.get('item', '')  # Get the query parameter
    product = get_product(item)
    if product is None:
        return render_template('search/search-error.html')
    return render_template('search/search-display.html', products=product)