from flask import render_template, jsonify
from flask_login import login_user, logout_user, login_required, current_user


def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/products', methods=['GET'])
    def get_products():
        products = Product.query.all()
        return jsonify([p.to_dict() for p in products])

    # ... остальные маршруты ...