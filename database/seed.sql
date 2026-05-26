USE biblioteca_db;

INSERT INTO autores (nome, nacionalidade, data_nascimento) VALUES
('Machado de Assis', 'Brasileira', '1839-06-21'),
('Clarice Lispector', 'Brasileira', '1920-12-10'),
('George Orwell', 'Britanica', '1903-06-25');

INSERT INTO livros (titulo, isbn, ano_publicacao, quantidade_total, quantidade_disponivel, autor_id) VALUES
('Dom Casmurro', '9788535910663', 1899, 3, 3, 1),
('A Hora da Estrela', '9788535914845', 1977, 2, 2, 2),
('1984', '9788535914846', 1949, 4, 4, 3);

INSERT INTO usuarios (nome, email, telefone, status) VALUES
('Ana Silva', 'ana@example.com', '(11) 99999-1111', 'ativo'),
('Bruno Santos', 'bruno@example.com', '(21) 98888-2222', 'ativo');
