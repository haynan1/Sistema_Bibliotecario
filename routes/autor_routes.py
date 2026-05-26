import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from mysql.connector import Error

from models.autor_model import AutorModel

logger = logging.getLogger(__name__)
autor_bp = Blueprint("autores", __name__, url_prefix="/autores")


@autor_bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    autores, total, total_pages = AutorModel.listar(page=page)
    autor_edicao = None
    if request.args.get("editar"):
        autor_edicao = AutorModel.buscar_por_id(request.args["editar"])
        page = 1
    return render_template(
        "autores.html",
        autores=autores,
        autor_edicao=autor_edicao,
        page=page,
        total_pages=total_pages,
    )


@autor_bp.route("/salvar", methods=["POST"])
@login_required
def salvar():
    autor_id = request.form.get("id")
    nome = request.form["nome"]
    nacionalidade = request.form.get("nacionalidade")
    data_nascimento = request.form.get("data_nascimento")

    try:
        if autor_id:
            AutorModel.atualizar(autor_id, nome, nacionalidade, data_nascimento)
            flash("Autor atualizado com sucesso.", "success")
        else:
            AutorModel.criar(nome, nacionalidade, data_nascimento)
            flash("Autor cadastrado com sucesso.", "success")
    except Error as erro:
        logger.exception("Erro ao salvar autor")
        flash(f"Não foi possível salvar o autor: {erro.msg}", "error")

    return redirect(url_for("autores.listar"))


@autor_bp.route("/excluir/<int:autor_id>", methods=["POST"])
@login_required
def excluir(autor_id):
    try:
        AutorModel.excluir(autor_id)
        flash("Autor excluído com sucesso.", "success")
    except Error:
        logger.exception("Erro ao excluir autor %s", autor_id)
        flash("Não foi possível excluir: existem livros vinculados a este autor.", "error")
    return redirect(url_for("autores.listar"))
