import logging
import re

from models.db import execute, execute_update, fetch_all, fetch_one, get_connection

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
        telefone = UsuarioModel._formatar_telefone(telefone)
        return execute(
            "INSERT INTO usuarios (nome, email, telefone, status) VALUES (%s, %s, %s, %s)",
            (nome, email, telefone or None, status),
        )

    @staticmethod
    def atualizar(usuario_id, nome, email, telefone, status):
        telefone = UsuarioModel._formatar_telefone(telefone)
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

    @staticmethod
    def excluir(usuario_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS n
                    FROM emprestimos
                    WHERE usuario_id = %s AND status <> 'devolvido'
                    """,
                    (usuario_id,),
                )
                emprestimos_pendentes = cursor.fetchone()["n"]
                if emprestimos_pendentes:
                    raise ValueError("Não é possível excluir: este usuário ainda possui devoluções pendentes.")

                cursor.execute(
                    """
                    DELETE devolucoes
                    FROM devolucoes
                    JOIN emprestimos ON emprestimos.id = devolucoes.emprestimo_id
                    WHERE emprestimos.usuario_id = %s
                    """,
                    (usuario_id,),
                )
                cursor.execute("DELETE FROM emprestimos WHERE usuario_id = %s", (usuario_id,))
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))

                if cursor.rowcount == 0:
                    raise ValueError("Usuário não encontrado.")

                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
        finally:
            connection.close()

    @staticmethod
    def _formatar_telefone(telefone):
        digitos = re.sub(r"\D", "", telefone or "")[:11]
        if not digitos:
            return None
        if len(digitos) == 10:
            return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
        if len(digitos) == 11:
            return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
        return digitos
