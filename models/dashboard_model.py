from models.db import fetch_one


class DashboardModel:
    @staticmethod
    def obter_totais():
        return fetch_one(
            """
            SELECT
                (SELECT COUNT(*) FROM livros) AS livros,
                (SELECT COUNT(*) FROM usuarios WHERE status = 'ativo') AS usuarios_ativos,
                (SELECT COUNT(*) FROM emprestimos WHERE status = 'ativo') AS emprestimos_ativos,
                (SELECT COUNT(*) FROM emprestimos
                 WHERE status = 'atrasado'
                    OR (status = 'ativo' AND data_prevista_devolucao < CURDATE())
                ) AS emprestimos_atrasados
            """
        )
