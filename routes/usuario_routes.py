import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from mysql.connector import Error

from models.usuario_model import UsuarioModel

logger = logging.getLogger(__name__)
usuario_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuario_bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    usuarios, total, total_pages = UsuarioModel.listar(page=page)
    usuario_edicao = None
    if request.args.get("editar"):
        usuario_edicao = UsuarioModel.buscar_por_id(request.args["editar"])
        page = 1
    return render_template(
        "usuarios.html",
        usuarios=usuarios,
        usuario_edicao=usuario_edicao,
        page=page,
        total_pages=total_pages,
    )


@usuario_bp.route("/salvar", methods=["POST"])
@login_required
def salvar():
    usuario_id = request.form.get("id")
    nome = request.form["nome"]
    email = request.form["email"]
    telefone = request.form.get("telefone")
    status = request.form["status"]

    try:
        if usuario_id:
            UsuarioModel.atualizar(usuario_id, nome, email, telefone, status)
            flash("Usuário atualizado com sucesso.", "success")
        else:
            UsuarioModel.criar(nome, email, telefone, status)
            flash("Usuário cadastrado com sucesso.", "success")
    except Error as erro:
        logger.exception("Erro ao salvar usuário")
        mensagem = "E-mail já cadastrado." if erro.errno == 1062 else erro.msg
        flash(f"Não foi possível salvar o usuário: {mensagem}", "error")

    return redirect(url_for("usuarios.listar"))


@usuario_bp.route("/excluir/<int:usuario_id>", methods=["POST"])
@login_required
def excluir(usuario_id):
    try:
        UsuarioModel.excluir(usuario_id)
        flash("Usuário excluído com sucesso.", "success")
    except ValueError as erro:
        flash(str(erro), "error")
    except Error:
        logger.exception("Erro ao excluir usuário %s", usuario_id)
        flash("Não foi possível excluir o usuário.", "error")
    return redirect(url_for("usuarios.listar"))


@usuario_bp.route("/alternar-status/<int:usuario_id>", methods=["POST"])
@login_required
def alternar_status(usuario_id):
    try:
        UsuarioModel.alternar_status(usuario_id)
        flash("Status do usuário atualizado.", "success")
    except ValueError as erro:
        flash(str(erro), "error")
    except Error:
        logger.exception("Erro ao alternar status do usuário %s", usuario_id)
        flash("Não foi possível atualizar o status.", "error")
    return redirect(url_for("usuarios.listar"))
