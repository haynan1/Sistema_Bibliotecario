import logging

from models.db import execute, execute_update, fetch_all, fetch_one

logger = logging.getLogger(__name__)

PER_PAGE = 50


class UsuarioModel:
    @staticmethod
    def listar(page=1):
        offset = (page - 1) * PER_PAGE
        items = fetch_all(
            "SELECT * FROM usuarios ORDER BY nome LIMIT %s OFFSET %s",
            (PER_PAGE, offset),
        )
        total = fetch_one("SELECT COUNT(*) AS n FROM usuarios")["n"]
        return items, total, max(1, -(-total // PER_PAGE))

    @staticmethod
    def listar_ativos():
        return fetch_all("SELECT * FROM usuarios WHERE status = 'ativo' ORDER BY nome")

    @staticmethod
    def buscar_por_id(usuario_id):
        return fetch_one("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))

    @staticmethod
    def criar(nome, email, telefone, status):
        return execute(
            "INSERT INTO usuarios (nome, email, telefone, status) VALUES (%s, %s, %s, %s)",
            (nome, email, telefone or None, status),
        )

    @staticmethod
    def atualizar(usuario_id, nome, email, telefone, status):
        execute(
            """
            UPDATE usuarios
            SET nome = %s, email = %s, telefone = %s, status = %s
            WHERE id = %s
            """,
            (nome, email, telefone or None, status, usuario_id),
        )

    @staticmethod
    def alternar_status(usuario_id):
        affected = execute_update(
            "UPDATE usuarios SET status = IF(status = 'ativo', 'bloqueado', 'ativo') WHERE id = %s",
            (usuario_id,),
        )
        if affected == 0:
            raise ValueError("Usuário não encontrado.")
