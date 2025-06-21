import os
import importlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import redirect, url_for
from flask_login import current_user

# Создаём объекты
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

    db.init_app(app)
    login_manager.init_app(app)

    # Основные блюпринты
    from app.auth import auth
    from app.smm import smm
    app.register_blueprint(auth)
    app.register_blueprint(smm)

    # Дополнительные блюпринты из routes
    from app.routes.postgen import postgen_bp
    from app.routes.settings import settings
    from app.routes.vk_stats import vk_stats
    
    app.register_blueprint(postgen_bp)
    app.register_blueprint(settings)
    app.register_blueprint(vk_stats)

    @app.route("/")
    def root_redirect():
        if current_user.is_authenticated:
            return redirect(url_for("smm.dashboard"))
        return redirect(url_for("auth.login"))
    return app