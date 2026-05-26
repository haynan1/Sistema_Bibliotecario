import logging
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from models.devolucao_model import DevolucaoModel
from models.emprestimo_model import EmprestimoModel

logger = logging.getLogger(__name__)
devolucao_bp = Blueprint("devolucoes", __name__, url_prefix="/devolucoes")


@devolucao_bp.route("/")
@login_required
def listar():
    page = request.args.get("page", 1, type=int)
    devolucoes, total, total_pages = DevolucaoModel.listar(page=page)
    emprestimos_ativos = EmprestimoModel.listar_ativos()
    return render_template(
        "devolucoes.html",
        devolucoes=devolucoes,
        emprestimos_ativos=emprestimos_ativos,
        hoje=date.today(),
        emprestimo_id_preselecionado=request.args.get("emprestimo_id"),
        page=page,
        total_pages=total_pages,
    )


@devolucao_bp.route("/registrar", methods=["POST"])
@login_required
def registrar():
    try:
        DevolucaoModel.registrar(
            request.form["emprestimo_id"],
            request.form["data_devolucao"],
            request.form.get("observacao"),
        )
        flash("Devolução registrada com sucesso.", "success")
    except ValueError as erro:
        flash(str(erro), "error")
    except Exception:
        logger.exception("Erro ao registrar devolução")
        flash("Não foi possível registrar a devolução.", "error")

    origem = request.form.get("origem")
    if origem == "emprestimos":
        return redirect(url_for("emprestimos.listar"))
    return redirect(url_for("devolucoes.listar"))
