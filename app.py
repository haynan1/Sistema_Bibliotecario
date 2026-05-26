import logging
import os

from flask import Flask, render_template
from flask_login import LoginManager, login_required
from flask_wtf.csrf import CSRFProtect

from config import Config
from database.init_db import init_database
from models.admin_user import AdminUser
from models.dashboard_model import DashboardModel
from models.db import init_pool
from routes.auth_routes import auth_bp
from routes.autor_routes import autor_bp
from routes.devolucao_routes import devolucao_bp
from routes.emprestimo_routes import emprestimo_bp
from routes.livro_routes import livro_bp
from routes.usuario_routes import usuario_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

csrf = CSRFProtect()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "error"

    init_database(Config)
    init_pool(Config)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == "admin":
            return AdminUser()
        return None

    app.register_blueprint(auth_bp)
    app.register_blueprint(autor_bp)
    app.register_blueprint(livro_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(emprestimo_bp)
    app.register_blueprint(devolucao_bp)

    @app.route("/")
    @login_required
    def index():
        totais = DashboardModel.obter_totais()
        return render_template("index.html", totais=totais)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
