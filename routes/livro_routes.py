import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from mysql.connector import Error

from models.autor_model import AutorModel
from models.livro_model import LivroModel

logger = logging.getLogger(__name__)
livro_bp = Blueprint("livros", __name__, url_prefix="/livros")


@livro_bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    livros, total, total_pages = LivroModel.listar(page=page)
    autores = AutorModel.listar_todos()
    livro_edicao = None
    if request.args.get("editar"):
        livro_edicao = LivroModel.buscar_por_id(request.args["editar"])
        page = 1
    return render_template(
        "livros.html",
        livros=livros,
        autores=autores,
        livro_edicao=livro_edicao,
        page=page,
        total_pages=total_pages,
    )


@livro_bp.route("/salvar", methods=["POST"])
@login_required
def salvar():
    livro_id = request.form.get("id")
    dados = {
        "titulo": request.form["titulo"],
        "isbn": request.form["isbn"],
        "ano_publicacao": request.form.get("ano_publicacao"),
        "quantidade_total": request.form["quantidade_total"],
        "quantidade_disponivel": request.form["quantidade_disponivel"],
        "autor_id": request.form["autor_id"],
    }

    try:
        if livro_id:
            LivroModel.atualizar(livro_id, **dados)
            flash("Livro atualizado com sucesso.", "success")
        else:
            LivroModel.criar(**dados)
            flash("Livro cadastrado com sucesso.", "success")
    except ValueError as erro:
        flash(str(erro), "error")
    except Error as erro:
        logger.exception("Erro ao salvar livro")
        mensagem = "ISBN já cadastrado." if erro.errno == 1062 else erro.msg
        flash(f"Não foi possível salvar o livro: {mensagem}", "error")

    return redirect(url_for("livros.listar"))


@livro_bp.route("/excluir/<int:livro_id>", methods=["POST"])
@login_required
def excluir(livro_id):
    try:
        LivroModel.excluir(livro_id)
        flash("Livro excluído com sucesso.", "success")
    except ValueError as erro:
        flash(str(erro), "error")
    except Error:
        logger.exception("Erro ao excluir livro %s", livro_id)
        flash("Não foi possível excluir o livro.", "error")
    return redirect(url_for("livros.listar"))
