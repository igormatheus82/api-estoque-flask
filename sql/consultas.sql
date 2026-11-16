-- Consultas SQL de exemplo usadas (ou inspiradas) nos endpoints da API.
-- Rode depois de schema.sql e seed.sql para praticar.

-- 1) CREATE: cadastrar um produto
INSERT INTO produtos (nome, sku, preco, quantidade, estoque_minimo, categoria_id)
VALUES ('Webcam HD', 'PER-004', 159.90, 15, 5, 1);

-- 2) READ: listar produtos com o nome da categoria (JOIN)
SELECT p.id, p.nome, p.sku, p.preco, p.quantidade, c.nome AS categoria
FROM produtos p
LEFT JOIN categorias c ON c.id = p.categoria_id
ORDER BY p.nome;

-- 3) READ com filtro: buscar por parte do nome
SELECT * FROM produtos WHERE nome LIKE '%mouse%';

-- 4) UPDATE: reajustar preço em 10% de uma categoria
UPDATE produtos
SET preco = ROUND(preco * 1.10, 2), atualizado_em = datetime('now')
WHERE categoria_id = 2;

-- 5) DELETE: remover um produto pelo SKU
DELETE FROM produtos WHERE sku = 'PER-004';

-- 6) Relatório: produtos abaixo do estoque mínimo
SELECT p.nome, p.quantidade, p.estoque_minimo,
       (p.estoque_minimo - p.quantidade) AS faltam
FROM produtos p
WHERE p.quantidade < p.estoque_minimo
ORDER BY faltam DESC;

-- 7) Agregação: valor total em estoque por categoria (GROUP BY)
SELECT c.nome AS categoria,
       COUNT(p.id)                    AS total_produtos,
       SUM(p.quantidade)              AS itens_em_estoque,
       ROUND(SUM(p.preco * p.quantidade), 2) AS valor_total
FROM categorias c
LEFT JOIN produtos p ON p.categoria_id = c.id
GROUP BY c.id, c.nome
ORDER BY valor_total DESC;

-- 8) Subconsulta: produtos mais caros que a média
SELECT nome, preco FROM produtos
WHERE preco > (SELECT AVG(preco) FROM produtos);

-- 9) Histórico de movimentações de um produto
SELECT m.tipo, m.quantidade, m.criado_em
FROM movimentacoes m
WHERE m.produto_id = 1
ORDER BY m.criado_em DESC;
