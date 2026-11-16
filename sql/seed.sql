-- Dados de exemplo para testar a API manualmente

INSERT INTO categorias (nome, descricao) VALUES
    ('Periféricos', 'Mouses, teclados e headsets'),
    ('Monitores', 'Monitores e suportes'),
    ('Armazenamento', 'SSDs, HDs e pendrives');

INSERT INTO produtos (nome, sku, preco, quantidade, estoque_minimo, categoria_id) VALUES
    ('Mouse sem fio', 'PER-001', 89.90, 40, 10, 1),
    ('Teclado mecânico', 'PER-002', 349.00, 5, 8, 1),
    ('Headset USB', 'PER-003', 199.90, 0, 5, 1),
    ('Monitor 24" Full HD', 'MON-001', 899.00, 12, 3, 2),
    ('SSD 1TB NVMe', 'ARM-001', 459.90, 2, 5, 3);

INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES
    (1, 'ENTRADA', 50),
    (1, 'SAIDA', 10),
    (2, 'ENTRADA', 5),
    (4, 'ENTRADA', 12),
    (5, 'ENTRADA', 2);
