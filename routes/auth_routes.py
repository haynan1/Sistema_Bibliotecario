import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from config import Config
from models.admin_user import AdminUser

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (
            username == Config.ADMIN_USERNAME
            and Config.ADMIN_PASSWORD_HASH
            and check_password_hash(Config.ADMIN_PASSWORD_HASH, password)
        ):
            login_user(AdminUser())
            return redirect(request.args.get("next") or url_for("index"))

        logger.warning("Tentativa de login inválida para usuário: %s", username)
        flash("Credenciais inválidas.", "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
