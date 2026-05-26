```text
Autor
- id
- nome
- nacionalidade
- data_nascimento

Livro
- id
- titulo
- isbn
- ano_publicacao
- quantidade_total
- quantidade_disponivel
- autor_id

Usuario
- id
- nome
- email
- telefone
- data_cadastro
- status

Emprestimo
- id
- usuario_id
- livro_id
- data_emprestimo
- data_prevista_devolucao
- status

Devolucao
- id
- emprestimo_id
- data_devolucao
- observacao
```

Relacionamentos:

```text
Autor 1 ---- N Livro
Usuario 1 ---- N Emprestimo
Livro 1 ---- N Emprestimo
Emprestimo 1 ---- 1 Devolucao
```
