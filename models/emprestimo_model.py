import logging
from datetime import date

from models.db import fetch_all, fetch_one, get_connection

logger = logging.getLogger(__name__)

PER_PAGE = 50


class EmprestimoModel:
    @staticmethod
    def listar(page=1):
        offset = (page - 1) * PER_PAGE
        items = fetch_all(
            """
            SELECT
                emprestimos.*,
                usuarios.nome AS usuario_nome,
                livros.titulo AS livro_titulo
            FROM emprestimos
            JOIN usuarios ON usuarios.id = emprestimos.usuario_id
            JOIN livros ON livros.id = emprestimos.livro_id
            ORDER BY emprestimos.data_emprestimo DESC, emprestimos.id DESC
            LIMIT %s OFFSET %s
            """,
            (PER_PAGE, offset),
        )
        total = fetch_one("SELECT COUNT(*) AS n FROM emprestimos")["n"]
        return items, total, max(1, -(-total // PER_PAGE))

    @staticmethod
    def listar_ativos():
        return fetch_all(
            """
            SELECT
                emprestimos.*,
                usuarios.nome AS usuario_nome,
                livros.titulo AS livro_titulo
            FROM emprestimos
            JOIN usuarios ON usuarios.id = emprestimos.usuario_id
            JOIN livros ON livros.id = emprestimos.livro_id
            WHERE emprestimos.status = 'ativo'
            ORDER BY emprestimos.data_emprestimo DESC
            """
        )

    @staticmethod
    def criar(usuario_id, livro_id, data_emprestimo, data_prevista_devolucao):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
            usuario = cursor.fetchone()
            if not usuario or usuario["status"] != "ativo":
                raise ValueError("Somente usuários ativos podem realizar empréstimos.")

            cursor.execute("SELECT * FROM livros WHERE id = %s FOR UPDATE", (livro_id,))
            livro = cursor.fetchone()
            if not livro or livro["quantidade_disponivel"] <= 0:
                raise ValueError("Livro indisponível para empréstimo.")

            cursor.execute(
                """
                SELECT id FROM emprestimos
                WHERE usuario_id = %s AND livro_id = %s AND status = 'ativo'
                """,
                (usuario_id, livro_id),
            )
            if cursor.fetchone():
                raise ValueError("Este usuário já possui empréstimo ativo deste livro.")

            status = "atrasado" if data_prevista_devolucao < date.today().isoformat() else "ativo"
            cursor.execute(
                """
                INSERT INTO emprestimos
                    (usuario_id, livro_id, data_emprestimo, data_prevista_devolucao, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (usuario_id, livro_id, data_emprestimo, data_prevista_devolucao, status),
            )
            cursor.execute(
                """
                UPDATE livros
                SET quantidade_disponivel = quantidade_disponivel - 1
                WHERE id = %s
                """,
                (livro_id,),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
