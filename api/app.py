from flask import Flask, request, jsonify, abort
from flask_login import login_user, login_required, logout_user, current_user
from extensions import db, login_manager  # Импортируем из extensions.py
from models import User, Product, Cart, Order
from instance.config import Config
from flask import Flask, render_template
from . import create_app
from api.extensions import db, login_manager  # Добавьте префикс api.
app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.config.from_object(Config)
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
@app.route('/')
def index():
    return render_template('index.html')
# Инициализация расширений
db.init_app(app)
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Обработчики ошибок
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Неверный запрос'}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Не авторизован'}), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Не найдено'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Ошибка сервера'}), 500


# Главная страница
@app.route('/', methods=['GET'])
def index():
    return 'Добро пожаловать в интернет-магазин!'


# Регистрация
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        abort(400, description="Необходимо указать username, email и пароль")

    if User.query.filter((User.email == data['email']) | (User.username == data['username'])).first():
        abort(400, description="Пользователь с таким email или username уже существует")

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Регистрация прошла успешно!'})


# Вход
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        abort(400, description="Необходимо указать email и пароль")

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        abort(401, description="Неверные учетные данные")

    login_user(user)
    return jsonify({'message': 'Вход выполнен!'})


# Выход
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Вы вышли из системы'})


# Профиль
@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return jsonify({
        'username': current_user.username,
        'email': current_user.email
    })


# Товары
@app.route('/create_products', methods=['POST'])
def create_products():
    product1 = Product(name='Товар 1', price=10.99)
    product2 = Product(name='Товар 2', price=20.99)
    db.session.add_all([product1, product2])
    db.session.commit()
    return jsonify({'message': 'Тестовые товары созданы!'})


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price
    } for p in products])


# Корзина
@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()

    if 'product_id' not in data:
        abort(400, description="Необходимо указать product_id")

    product = Product.query.get(data['product_id'])
    if not product:
        abort(404, description="Товар не найден")

    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product.id
    ).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=product.id,
            quantity=1
        )
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': f'Товар "{product.name}" добавлен в корзину!'})


@app.route('/cart', methods=['GET'])
@login_required
def view_cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = 0
    items = []

    for item in cart_items:
        product = item.product
        items.append({
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': item.quantity
        })
        total += product.price * item.quantity

    return jsonify({'items': items, 'total': total})


# Заказы
@app.route('/order', methods=['POST'])
@login_required
def create_order():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        abort(400, description="Корзина пуста")

    items_data = []
    total = 0

    for item in cart_items:
        product = item.product
        items_data.append({
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': item.quantity
        })
        total += product.price * item.quantity

    order = Order(
        user_id=current_user.id,
        total=total,
        items=items_data
    )

    db.session.add(order)
    Cart.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    return jsonify({
        'message': 'Заказ создан!',
        'order_id': order.id,
        'total': total
    })


@app.route('/orders', methods=['GET'])
@login_required
def get_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([{
        'id': order.id,
        'total': order.total,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
        'items': order.items
    } for order in orders])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)