CREATE DATABASE IF NOT EXISTS biblioteca_db;
USE biblioteca_db;

CREATE TABLE IF NOT EXISTS autores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    nacionalidade VARCHAR(100),
    data_nascimento DATE
);

CREATE TABLE IF NOT EXISTS livros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    isbn VARCHAR(30) NOT NULL UNIQUE,
    ano_publicacao INT,
    quantidade_total INT NOT NULL DEFAULT 1,
    quantidade_disponivel INT NOT NULL DEFAULT 1,
    autor_id INT NOT NULL,
    FOREIGN KEY (autor_id) REFERENCES autores(id),
    CONSTRAINT chk_quantidade_livros CHECK (
        quantidade_total >= 0
        AND quantidade_disponivel >= 0
        AND quantidade_disponivel <= quantidade_total
    )
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefone VARCHAR(30),
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ativo', 'bloqueado') DEFAULT 'ativo'
);

CREATE TABLE IF NOT EXISTS emprestimos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    livro_id INT NOT NULL,
    data_emprestimo DATE NOT NULL,
    data_prevista_devolucao DATE NOT NULL,
    status ENUM('ativo', 'devolvido', 'atrasado') DEFAULT 'ativo',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (livro_id) REFERENCES livros(id)
);

CREATE TABLE IF NOT EXISTS devolucoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emprestimo_id INT NOT NULL UNIQUE,
    data_devolucao DATE NOT NULL,
    observacao TEXT,
    FOREIGN KEY (emprestimo_id) REFERENCES emprestimos(id)
);
