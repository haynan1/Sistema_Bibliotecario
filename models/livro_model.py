import logging

from models.db import execute, fetch_all, fetch_one, get_connection

logger = logging.getLogger(__name__)

PER_PAGE = 50


class LivroModel:
    @staticmethod
    def listar(page=1):
        offset = (page - 1) * PER_PAGE
        items = fetch_all(
            """
            SELECT livros.*, autores.nome AS autor_nome
            FROM livros
            JOIN autores ON autores.id = livros.autor_id
            ORDER BY livros.titulo
            LIMIT %s OFFSET %s
            """,
            (PER_PAGE, offset),
        )
        total = fetch_one("SELECT COUNT(*) AS n FROM livros")["n"]
        return items, total, max(1, -(-total // PER_PAGE))

    @staticmethod
    def listar_disponiveis():
        return fetch_all(
            """
            SELECT livros.*, autores.nome AS autor_nome
            FROM livros
            JOIN autores ON autores.id = livros.autor_id
            WHERE livros.quantidade_disponivel > 0
            ORDER BY livros.titulo
            """
        )

    @staticmethod
    def buscar_por_id(livro_id):
        return fetch_one("SELECT * FROM livros WHERE id = %s", (livro_id,))

    @staticmethod
    def criar(titulo, isbn, ano_publicacao, quantidade_total, quantidade_disponivel, autor_id):
        LivroModel._validar_quantidades(quantidade_total, quantidade_disponivel)
        return execute(
            """
            INSERT INTO livros
                (titulo, isbn, ano_publicacao, quantidade_total, quantidade_disponivel, autor_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                titulo,
                isbn,
                ano_publicacao or None,
                quantidade_total,
                quantidade_disponivel,
                autor_id,
            ),
        )

    @staticmethod
    def atualizar(livro_id, titulo, isbn, ano_publicacao, quantidade_total, quantidade_disponivel, autor_id):
        LivroModel._validar_quantidades(quantidade_total, quantidade_disponivel)
        execute(
            """
            UPDATE livros
            SET titulo = %s,
                isbn = %s,
                ano_publicacao = %s,
                quantidade_total = %s,
                quantidade_disponivel = %s,
                autor_id = %s
            WHERE id = %s
            """,
            (
                titulo,
                isbn,
                ano_publicacao or None,
                quantidade_total,
                quantidade_disponivel,
                autor_id,
                livro_id,
            ),
        )

    @staticmethod
    def excluir(livro_id):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS n
                    FROM emprestimos
                    WHERE livro_id = %s AND status <> 'devolvido'
                    """,
                    (livro_id,),
                )
                emprestimos_pendentes = cursor.fetchone()["n"]
                if emprestimos_pendentes:
                    raise ValueError("Não é possível excluir: ainda existem devoluções pendentes para este livro.")

                cursor.execute(
                    """
                    DELETE devolucoes
                    FROM devolucoes
                    JOIN emprestimos ON emprestimos.id = devolucoes.emprestimo_id
                    WHERE emprestimos.livro_id = %s
                    """,
                    (livro_id,),
                )
                cursor.execute("DELETE FROM emprestimos WHERE livro_id = %s", (livro_id,))
                cursor.execute("DELETE FROM livros WHERE id = %s", (livro_id,))

                if cursor.rowcount == 0:
                    raise ValueError("Livro não encontrado.")

                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()
        finally:
            connection.close()

    @staticmethod
    def _validar_quantidades(quantidade_total, quantidade_disponivel):
        total = int(quantidade_total)
        disponivel = int(quantidade_disponivel)
        if total < 0 or disponivel < 0:
            raise ValueError("As quantidades não podem ser negativas.")
        if disponivel > total:
            raise ValueError("A quantidade disponível não pode ser maior que a total.")
