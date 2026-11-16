-- Esquema do banco de dados da API de Estoque
-- Banco: SQLite (os comandos são SQL padrão e funcionam com poucas mudanças em PostgreSQL/MySQL)

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS movimentacoes;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS categorias;

CREATE TABLE categorias (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL UNIQUE,
    descricao   TEXT,
    criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE produtos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT    NOT NULL,
    sku             TEXT    NOT NULL UNIQUE,
    preco           REAL    NOT NULL CHECK (preco >= 0),
    quantidade      INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
    estoque_minimo  INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    categoria_id    INTEGER REFERENCES categorias (id) ON DELETE RESTRICT,
    criado_em       TEXT    NOT NULL DEFAULT (datetime('now')),
    atualizado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Histórico de entradas e saídas de estoque (auditoria)
CREATE TABLE movimentacoes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id  INTEGER NOT NULL REFERENCES produtos (id) ON DELETE CASCADE,
    tipo        TEXT    NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    quantidade  INTEGER NOT NULL CHECK (quantidade > 0),
    criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_produtos_categoria ON produtos (categoria_id);
CREATE INDEX idx_movimentacoes_produto ON movimentacoes (produto_id);
