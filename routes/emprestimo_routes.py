import logging
from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from models.emprestimo_model import EmprestimoModel
from models.livro_model import LivroModel
from models.usuario_model import UsuarioModel

logger = logging.getLogger(__name__)
emprestimo_bp = Blueprint("emprestimos", __name__, url_prefix="/emprestimos")


@emprestimo_bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    emprestimos, total, total_pages = EmprestimoModel.listar(page=page)
    usuarios = UsuarioModel.listar_ativos()
    livros = LivroModel.listar_disponiveis()
    hoje = date.today()
    data_prevista_padrao = hoje + timedelta(days=7)
    return render_template(
        "emprestimos.html",
        emprestimos=emprestimos,
        usuarios=usuarios,
        livros=livros,
        hoje=hoje,
        data_prevista_padrao=data_prevista_padrao,
        page=page,
        total_pages=total_pages,
    )


@emprestimo_bp.route("/criar", methods=["POST"])
@login_required
def criar():
    try:
        EmprestimoModel.criar(
            request.form["usuario_id"],
            request.form["livro_id"],
            request.form["data_emprestimo"],
            request.form["data_prevista_devolucao"],
        )
        flash("Empréstimo registrado com sucesso.", "success")
    except ValueError as erro:
        flash(str(erro), "error")
    except Exception:
        logger.exception("Erro ao criar empréstimo")
        flash("Não foi possível registrar o empréstimo.", "error")

    return redirect(url_for("emprestimos.listar"))
