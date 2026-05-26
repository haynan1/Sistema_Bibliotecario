import logging

from models.db import execute, fetch_all, fetch_one

logger = logging.getLogger(__name__)

PER_PAGE = 50


class AutorModel:
    @staticmethod
    def listar(page=1):
        offset = (page - 1) * PER_PAGE
        items = fetch_all(
            "SELECT * FROM autores ORDER BY nome LIMIT %s OFFSET %s",
            (PER_PAGE, offset),
        )
        total = fetch_one("SELECT COUNT(*) AS n FROM autores")["n"]
        return items, total, max(1, -(-total // PER_PAGE))

    @staticmethod
    def listar_todos():
        return fetch_all("SELECT * FROM autores ORDER BY nome")

    @staticmethod
    def buscar_por_id(autor_id):
        return fetch_one("SELECT * FROM autores WHERE id = %s", (autor_id,))

    @staticmethod
    def criar(nome, nacionalidade, data_nascimento):
        return execute(
            "INSERT INTO autores (nome, nacionalidade, data_nascimento) VALUES (%s, %s, %s)",
            (nome, nacionalidade or None, data_nascimento or None),
        )

    @staticmethod
    def atualizar(autor_id, nome, nacionalidade, data_nascimento):
        execute(
            """
            UPDATE autores
            SET nome = %s, nacionalidade = %s, data_nascimento = %s
            WHERE id = %s
            """,
            (nome, nacionalidade or None, data_nascimento or None, autor_id),
        )

    @staticmethod
    def excluir(autor_id):
        execute("DELETE FROM autores WHERE id = %s", (autor_id,))
