"""Camada de acesso a dados: todo o SQL da aplicação fica aqui.

As consultas usam parâmetros (?) para evitar SQL Injection.
"""
from .db import get_db


class NaoEncontrado(Exception):
    pass


class Conflito(Exception):
    pass


def _dict(linha):
    return dict(linha) if linha is not None else None


# ---------------------------------------------------------------- categorias

def listar_categorias():
    linhas = get_db().execute("SELECT * FROM categorias ORDER BY nome").fetchall()
    return [dict(l) for l in linhas]


def buscar_categoria(categoria_id: int):
    linha = get_db().execute(
        "SELECT * FROM categorias WHERE id = ?", (categoria_id,)
    ).fetchone()
    if linha is None:
        raise NaoEncontrado(f"Categoria {categoria_id} não encontrada.")
    return dict(linha)


def criar_categoria(nome: str, descricao: str | None):
    db = get_db()
    if db.execute("SELECT 1 FROM categorias WHERE nome = ?", (nome,)).fetchone():
        raise Conflito(f"Já existe uma categoria com o nome '{nome}'.")
    cur = db.execute(
        "INSERT INTO categorias (nome, descricao) VALUES (?, ?)", (nome, descricao)
    )
    db.commit()
    return buscar_categoria(cur.lastrowid)


def atualizar_categoria(categoria_id: int, nome: str, descricao: str | None):
    buscar_categoria(categoria_id)
    db = get_db()
    duplicada = db.execute(
        "SELECT 1 FROM categorias WHERE nome = ? AND id <> ?", (nome, categoria_id)
    ).fetchone()
    if duplicada:
        raise Conflito(f"Já existe uma categoria com o nome '{nome}'.")
    db.execute(
        "UPDATE categorias SET nome = ?, descricao = ? WHERE id = ?",
        (nome, descricao, categoria_id),
    )
    db.commit()
    return buscar_categoria(categoria_id)


def excluir_categoria(categoria_id: int):
    buscar_categoria(categoria_id)
    db = get_db()
    em_uso = db.execute(
        "SELECT COUNT(*) FROM produtos WHERE categoria_id = ?", (categoria_id,)
    ).fetchone()[0]
    if em_uso:
        raise Conflito("Categoria possui produtos vinculados e não pode ser excluída.")
    db.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
    db.commit()


# ------------------------------------------------------------------ produtos

_SELECT_PRODUTO = """
    SELECT p.*, c.nome AS categoria_nome
    FROM produtos p
    LEFT JOIN categorias c ON c.id = p.categoria_id
"""


def listar_produtos(busca: str | None = None, categoria_id: int | None = None):
    sql = _SELECT_PRODUTO + " WHERE 1 = 1"
    params = []
    if busca:
        sql += " AND (p.nome LIKE ? OR p.sku LIKE ?)"
        params += [f"%{busca}%", f"%{busca}%"]
    if categoria_id is not None:
        sql += " AND p.categoria_id = ?"
        params.append(categoria_id)
    sql += " ORDER BY p.nome"
    return [dict(l) for l in get_db().execute(sql, params).fetchall()]


def buscar_produto(produto_id: int):
    linha = get_db().execute(_SELECT_PRODUTO + " WHERE p.id = ?", (produto_id,)).fetchone()
    if linha is None:
        raise NaoEncontrado(f"Produto {produto_id} não encontrado.")
    return dict(linha)


def _checar_categoria(categoria_id):
    if categoria_id is not None:
        buscar_categoria(categoria_id)


def _checar_sku(sku: str, ignorar_id: int | None = None):
    sql, params = "SELECT 1 FROM produtos WHERE sku = ?", [sku]
    if ignorar_id is not None:
        sql += " AND id <> ?"
        params.append(ignorar_id)
    if get_db().execute(sql, params).fetchone():
        raise Conflito(f"Já existe um produto com o SKU '{sku}'.")


def criar_produto(dados: dict):
    _checar_categoria(dados.get("categoria_id"))
    _checar_sku(dados["sku"])
    db = get_db()
    cur = db.execute(
        """INSERT INTO produtos (nome, sku, preco, quantidade, estoque_minimo, categoria_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            dados["nome"],
            dados["sku"],
            dados["preco"],
            dados.get("quantidade", 0),
            dados.get("estoque_minimo", 0),
            dados.get("categoria_id"),
        ),
    )
    db.commit()
    return buscar_produto(cur.lastrowid)


def atualizar_produto(produto_id: int, dados: dict):
    """Atualiza apenas os campos enviados (serve para PUT e PATCH)."""
    buscar_produto(produto_id)
    if "categoria_id" in dados:
        _checar_categoria(dados["categoria_id"])
    if "sku" in dados:
        _checar_sku(dados["sku"], ignorar_id=produto_id)

    colunas = ", ".join(f"{campo} = ?" for campo in dados)  # campos já validados
    db = get_db()
    db.execute(
        f"UPDATE produtos SET {colunas}, atualizado_em = datetime('now') WHERE id = ?",
        (*dados.values(), produto_id),
    )
    db.commit()
    return buscar_produto(produto_id)


def excluir_produto(produto_id: int):
    buscar_produto(produto_id)
    db = get_db()
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


# ------------------------------------------------------------ movimentações

def movimentar_estoque(produto_id: int, tipo: str, quantidade: int):
    """Registra entrada/saída e atualiza o saldo na mesma transação."""
    produto = buscar_produto(produto_id)
    if tipo == "SAIDA" and quantidade > produto["quantidade"]:
        raise Conflito(
            f"Estoque insuficiente: disponível {produto['quantidade']}, solicitado {quantidade}."
        )
    delta = quantidade if tipo == "ENTRADA" else -quantidade
    db = get_db()
    with db:  # commit automático; rollback se der erro
        db.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (?, ?, ?)",
            (produto_id, tipo, quantidade),
        )
        db.execute(
            """UPDATE produtos SET quantidade = quantidade + ?, atualizado_em = datetime('now')
               WHERE id = ?""",
            (delta, produto_id),
        )
    return buscar_produto(produto_id)


def listar_movimentacoes(produto_id: int):
    buscar_produto(produto_id)
    linhas = get_db().execute(
        "SELECT * FROM movimentacoes WHERE produto_id = ? ORDER BY id DESC", (produto_id,)
    ).fetchall()
    return [dict(l) for l in linhas]


# --------------------------------------------------------------- relatórios

def produtos_estoque_baixo():
    linhas = get_db().execute(
        """SELECT id, nome, sku, quantidade, estoque_minimo,
                  (estoque_minimo - quantidade) AS faltam
           FROM produtos
           WHERE quantidade < estoque_minimo
           ORDER BY faltam DESC"""
    ).fetchall()
    return [dict(l) for l in linhas]


def resumo_por_categoria():
    linhas = get_db().execute(
        """SELECT c.id, c.nome AS categoria,
                  COUNT(p.id) AS total_produtos,
                  COALESCE(SUM(p.quantidade), 0) AS itens_em_estoque,
                  ROUND(COALESCE(SUM(p.preco * p.quantidade), 0), 2) AS valor_total
           FROM categorias c
           LEFT JOIN produtos p ON p.categoria_id = c.id
           GROUP BY c.id, c.nome
           ORDER BY valor_total DESC"""
    ).fetchall()
    return [dict(l) for l in linhas]
