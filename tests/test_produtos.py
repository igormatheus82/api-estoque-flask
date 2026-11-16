import pytest

PRODUTO_VALIDO = {"nome": "Teclado", "sku": "PER-002", "preco": 349.0}


# ------------------------------------------------------------------- CREATE

def test_criar_produto(client, categoria):
    resp = client.post("/produtos", json={**PRODUTO_VALIDO, "categoria_id": categoria["id"]})
    assert resp.status_code == 201
    corpo = resp.get_json()
    assert corpo["nome"] == "Teclado"
    assert corpo["quantidade"] == 0  # valor padrão
    assert corpo["categoria_nome"] == "Periféricos"


def test_sku_e_salvo_em_maiusculas(produto):
    assert produto["sku"] == "PER-001"


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("nome", ""),
        ("sku", None),
        ("preco", -1),
        ("preco", "dez"),
        ("preco", True),
        ("quantidade", -5),
        ("quantidade", 2.5),
        ("estoque_minimo", "3"),
    ],
)
def test_validacoes_de_produto(client, campo, valor):
    resp = client.post("/produtos", json={**PRODUTO_VALIDO, campo: valor})
    assert resp.status_code == 400
    assert campo in resp.get_json()["detalhes"]


def test_nao_permite_sku_duplicado(client, produto):
    resp = client.post("/produtos", json={**PRODUTO_VALIDO, "sku": "PER-001"})
    assert resp.status_code == 409


def test_categoria_inexistente_retorna_404(client):
    resp = client.post("/produtos", json={**PRODUTO_VALIDO, "categoria_id": 999})
    assert resp.status_code == 404


# --------------------------------------------------------------------- READ

def test_buscar_produto(client, produto):
    resp = client.get(f"/produtos/{produto['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["sku"] == "PER-001"


def test_buscar_produto_inexistente(client):
    assert client.get("/produtos/123").status_code == 404


def test_filtrar_produtos_por_busca_e_categoria(client, categoria, produto):
    client.post("/produtos", json={"nome": "Monitor", "sku": "MON-1", "preco": 900})

    por_nome = client.get("/produtos?busca=mouse").get_json()
    assert [p["nome"] for p in por_nome] == ["Mouse sem fio"]

    por_categoria = client.get(f"/produtos?categoria_id={categoria['id']}").get_json()
    assert len(por_categoria) == 1


# ------------------------------------------------------------------- UPDATE

def test_patch_atualiza_apenas_campos_enviados(client, produto):
    resp = client.patch(f"/produtos/{produto['id']}", json={"preco": 99.99})
    assert resp.status_code == 200
    corpo = resp.get_json()
    assert corpo["preco"] == 99.99
    assert corpo["nome"] == "Mouse sem fio"


def test_patch_sem_campos_retorna_400(client, produto):
    assert client.patch(f"/produtos/{produto['id']}", json={}).status_code == 400


def test_put_exige_campos_obrigatorios(client, produto):
    resp = client.put(f"/produtos/{produto['id']}", json={"nome": "Só nome"})
    assert resp.status_code == 400


def test_put_substitui_produto(client, produto):
    resp = client.put(
        f"/produtos/{produto['id']}",
        json={"nome": "Mouse gamer", "sku": "PER-001", "preco": 150},
    )
    assert resp.status_code == 200
    assert resp.get_json()["nome"] == "Mouse gamer"


# ------------------------------------------------------------------- DELETE

def test_excluir_produto(client, produto):
    assert client.delete(f"/produtos/{produto['id']}").status_code == 204
    assert client.get(f"/produtos/{produto['id']}").status_code == 404


def test_excluir_produto_inexistente(client):
    assert client.delete("/produtos/999").status_code == 404


# ------------------------------------------------------------ movimentações

def test_entrada_aumenta_estoque(client, produto):
    resp = client.post(
        f"/produtos/{produto['id']}/movimentacoes", json={"tipo": "entrada", "quantidade": 5}
    )
    assert resp.status_code == 201
    assert resp.get_json()["quantidade"] == 15


def test_saida_diminui_estoque_e_registra_historico(client, produto):
    client.post(f"/produtos/{produto['id']}/movimentacoes", json={"tipo": "SAIDA", "quantidade": 4})
    assert client.get(f"/produtos/{produto['id']}").get_json()["quantidade"] == 6

    historico = client.get(f"/produtos/{produto['id']}/movimentacoes").get_json()
    assert historico[0]["tipo"] == "SAIDA"
    assert historico[0]["quantidade"] == 4


def test_saida_maior_que_estoque_retorna_409(client, produto):
    resp = client.post(
        f"/produtos/{produto['id']}/movimentacoes", json={"tipo": "SAIDA", "quantidade": 11}
    )
    assert resp.status_code == 409
    # o saldo não pode ter mudado
    assert client.get(f"/produtos/{produto['id']}").get_json()["quantidade"] == 10


@pytest.mark.parametrize("corpo", [{"tipo": "TROCA", "quantidade": 1}, {"tipo": "ENTRADA", "quantidade": 0}])
def test_movimentacao_invalida(client, produto, corpo):
    resp = client.post(f"/produtos/{produto['id']}/movimentacoes", json=corpo)
    assert resp.status_code == 400


# --------------------------------------------------------------- relatórios

def test_relatorio_estoque_baixo(client, produto):
    client.post("/produtos", json={"nome": "SSD", "sku": "ARM-1", "preco": 400, "quantidade": 1, "estoque_minimo": 5})
    itens = client.get("/relatorios/estoque-baixo").get_json()
    assert [i["sku"] for i in itens] == ["ARM-1"]
    assert itens[0]["faltam"] == 4


def test_relatorio_por_categoria(client, produto):
    resumo = client.get("/relatorios/categorias").get_json()
    assert resumo[0]["categoria"] == "Periféricos"
    assert resumo[0]["valor_total"] == round(89.9 * 10, 2)
