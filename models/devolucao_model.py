import logging

from models.db import fetch_all, fetch_one, get_connection

logger = logging.getLogger(__name__)

PER_PAGE = 50


class DevolucaoModel:
    @staticmethod
    def listar(page=1):
        offset = (page - 1) * PER_PAGE
        items = fetch_all(
            """
            SELECT
                devolucoes.*,
                emprestimos.data_emprestimo,
                usuarios.nome AS usuario_nome,
                livros.titulo AS livro_titulo
            FROM devolucoes
            JOIN emprestimos ON emprestimos.id = devolucoes.emprestimo_id
            JOIN usuarios ON usuarios.id = emprestimos.usuario_id
            JOIN livros ON livros.id = emprestimos.livro_id
            ORDER BY devolucoes.data_devolucao DESC, devolucoes.id DESC
            LIMIT %s OFFSET %s
            """,
            (PER_PAGE, offset),
        )
        total = fetch_one("SELECT COUNT(*) AS n FROM devolucoes")["n"]
        return items, total, max(1, -(-total // PER_PAGE))

    @staticmethod
    def registrar(emprestimo_id, data_devolucao, observacao):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT emprestimos.*, devolucoes.id AS devolucao_id
                FROM emprestimos
                LEFT JOIN devolucoes ON devolucoes.emprestimo_id = emprestimos.id
                WHERE emprestimos.id = %s
                FOR UPDATE
                """,
                (emprestimo_id,),
            )
            emprestimo = cursor.fetchone()
            if not emprestimo:
                raise ValueError("Empréstimo não encontrado.")
            if emprestimo["devolucao_id"]:
                raise ValueError("Este empréstimo já possui devolução registrada.")
            if emprestimo["status"] == "devolvido":
                raise ValueError("Este empréstimo já foi devolvido.")

            cursor.execute(
                """
                INSERT INTO devolucoes (emprestimo_id, data_devolucao, observacao)
                VALUES (%s, %s, %s)
                """,
                (emprestimo_id, data_devolucao, observacao or None),
            )
            cursor.execute(
                "UPDATE emprestimos SET status = 'devolvido' WHERE id = %s",
                (emprestimo_id,),
            )
            cursor.execute(
                """
                UPDATE livros
                SET quantidade_disponivel = quantidade_disponivel + 1
                WHERE id = %s
                """,
                (emprestimo["livro_id"],),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()
