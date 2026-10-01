import os, psycopg2, secrets
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'shop.db'))
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['WHATSAPP_NUMBER'] = os.environ.get('WHATSAPP_NUMBER', '917602687113')  # country code + number, digits only

SAMPLE_PRODUCTS = [
    (1, 'Smartphone', 'Mobile', 12999, 'A stylish smartphone with a high-quality display and powerful performance.', 'https://placehold.co/900x650?text=Smartphone', 'https://placehold.co/900x650?text=Smartphone+Front,https://placehold.co/900x650?text=Smartphone+Back,https://placehold.co/900x650?text=Smartphone+Side', 1),
    (2, 'Wireless Headphones', 'Headphones', 1499, 'Enjoy wireless audio with comfortable ear cushions and clear sound.', 'https://placehold.co/900x650?text=Headphones', 'https://placehold.co/900x650?text=Headphones+Front,https://placehold.co/900x650?text=Headphones+Side,https://placehold.co/900x650?text=Headphones+Case', 1),
    (3, 'Mobile Charger', 'Accessories', 499, 'A compact mobile charger for everyday use.', 'https://placehold.co/900x650?text=Mobile+Charger', 'https://placehold.co/900x650?text=Charger+Front,https://placehold.co/900x650?text=Charger+Side', 1),
    (4, 'Bluetooth Speaker', 'Electronics', 1999, 'A portable Bluetooth speaker for music at home or outdoors.', 'https://placehold.co/900x650?text=Bluetooth+Speaker', 'https://placehold.co/900x650?text=Speaker+Front,https://placehold.co/900x650?text=Speaker+Back', 1),
]

def db():
    conn = psycopg2.connect('postgresql://radhakrishna_db_user:KLmNGAzwjw9vZZm2I6lZl0QSRtMfrIkk@dpg-dauvpou0tbcc73cuofm0-a/radhakrishna_db')
    return conn

def init_db():
    with db() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0, description TEXT NOT NULL DEFAULT '', image TEXT NOT NULL DEFAULT '',
            gallery TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1)''')
        con.execute('''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)''')
        count = con.execute('SELECT COUNT(*) FROM products').fetchone()[0]
        if count == 0:
            con.executemany('INSERT INTO products (id,name,category,price,description,image,gallery,active) VALUES (?,?,?,?,?,?,?,?)', SAMPLE_PRODUCTS)
        if con.execute('SELECT COUNT(*) FROM admins').fetchone()[0] == 0:
            username = os.environ.get('ADMIN_USERNAME', 'admin')
            password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
            con.execute('INSERT INTO admins (username,password_hash) VALUES (?,?)', (username, generate_password_hash(password)))

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('admin_login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper

def product_dict(row):
    item = dict(row)
    item['gallery_list'] = [u.strip() for u in (item.get('gallery') or '').split(',') if u.strip()]
    return item

@app.context_processor
def common_context():
    return {'whatsapp_number': app.config['WHATSAPP_NUMBER']}

@app.route('/')
def index():
    search = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    with db() as con:
        categories = [r['category'] for r in con.execute('SELECT DISTINCT category FROM products WHERE active=1 ORDER BY category')]
        sql = 'SELECT * FROM products WHERE active=1'
        params = []
        if search:
            sql += ' AND (name LIKE ? OR description LIKE ? OR category LIKE ?)'
            params += [f'%{search}%'] * 3
        if category:
            sql += ' AND category=?'
            params.append(category)
        sql += ' ORDER BY id DESC'
        products = [product_dict(r) for r in con.execute(sql, params).fetchall()]
    return render_template('index.html', products=products, categories=categories, search=search, selected_category=category)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    with db() as con:
        row = con.execute('SELECT * FROM products WHERE id=? AND active=1', (product_id,)).fetchone()
        if not row: abort(404)
        product = product_dict(row)
        related = [product_dict(r) for r in con.execute('SELECT * FROM products WHERE active=1 AND category=? AND id!=? ORDER BY id DESC LIMIT 4', (product['category'], product_id)).fetchall()]
    return render_template('product.html', product=product, related=related)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        with db() as con:
            admin = con.execute('SELECT * FROM admins WHERE username=?', (username,)).fetchone()
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            return redirect(request.args.get('next') or url_for('admin_dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    with db() as con:
        products = [product_dict(r) for r in con.execute('SELECT * FROM products ORDER BY id DESC').fetchall()]
    return render_template('admin.html', products=products)

@app.route('/admin/product/new', methods=['GET', 'POST'])
@app.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_product_form(product_id=None):
    with db() as con:
        row = con.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone() if product_id else None
    if product_id and not row: abort(404)
    product = product_dict(row) if row else {'name':'','category':'','price':'','description':'','image':'','gallery':'','active':1}
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image', '').strip()
        gallery = request.form.get('gallery', '').strip()
        try: price = float(request.form.get('price', '0'))
        except ValueError: price = -1
        active = 1 if request.form.get('active') == 'on' else 0
        if not name or not category or price < 0:
            flash('Enter a product name, category, and a valid non-negative price.', 'error')
            product = dict(request.form)
            product['active'] = active
            return render_template('product_form.html', product=product, editing=bool(product_id))
        with db() as con:
            values = (name, category, price, description, image_url, gallery, active)
            if product_id:
                con.execute('UPDATE products SET name=?,category=?,price=?,description=?,image=?,gallery=?,active=? WHERE id=?', values + (product_id,))
            else:
                con.execute('INSERT INTO products (name,category,price,description,image,gallery,active) VALUES (?,?,?,?,?,?,?)', values)
        flash('Product saved.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('product_form.html', product=product, editing=bool(product_id))

@app.route('/admin/product/<int:product_id>/delete', methods=['POST'])
@admin_required
def admin_product_delete(product_id):
    with db() as con:
        con.execute('DELETE FROM products WHERE id=?', (product_id,))
    flash('Product deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/password', methods=['GET', 'POST'])
@admin_required
def admin_password():
    if request.method == 'POST':
        old = request.form.get('old_password', '')
        new = request.form.get('new_password', '')
        if len(new) < 12:
            flash('Use a new password with at least 12 characters.', 'error')
        else:
            with db() as con:
                admin = con.execute('SELECT * FROM admins WHERE id=?', (session['admin_id'],)).fetchone()
                if not admin or not check_password_hash(admin['password_hash'], old):
                    flash('Current password is incorrect.', 'error')
                else:
                    con.execute('UPDATE admins SET password_hash=? WHERE id=?', (generate_password_hash(new), session['admin_id']))
                    flash('Password changed.', 'success')
                    return redirect(url_for('admin_dashboard'))
    return render_template('admin_password.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    init_db()
