from flask import Flask
from .extensions import db, login_manager


def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config.from_object('config.Config')

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)

    # Регистрация маршрутов
    from .routes import init_routes
    init_routes(app)

    return app