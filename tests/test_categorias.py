def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_criar_categoria(client):
    resp = client.post("/categorias", json={"nome": "  Monitores  ", "descricao": "Telas"})
    assert resp.status_code == 201
    corpo = resp.get_json()
    assert corpo["id"] > 0
    assert corpo["nome"] == "Monitores"  # espaços removidos


def test_criar_categoria_sem_nome_retorna_400(client):
    resp = client.post("/categorias", json={})
    assert resp.status_code == 400
    assert "nome" in resp.get_json()["detalhes"]


def test_criar_categoria_sem_corpo_json_retorna_400(client):
    resp = client.post("/categorias", data="texto", content_type="text/plain")
    assert resp.status_code == 400


def test_nao_permite_categoria_duplicada(client, categoria):
    resp = client.post("/categorias", json={"nome": "Periféricos"})
    assert resp.status_code == 409


def test_listar_categorias_em_ordem_alfabetica(client):
    for nome in ["Monitores", "Armazenamento", "Periféricos"]:
        client.post("/categorias", json={"nome": nome})
    nomes = [c["nome"] for c in client.get("/categorias").get_json()]
    assert nomes == ["Armazenamento", "Monitores", "Periféricos"]


def test_buscar_categoria_inexistente_retorna_404(client):
    assert client.get("/categorias/999").status_code == 404


def test_atualizar_categoria(client, categoria):
    resp = client.put(f"/categorias/{categoria['id']}", json={"nome": "Acessórios"})
    assert resp.status_code == 200
    assert resp.get_json()["nome"] == "Acessórios"


def test_excluir_categoria(client, categoria):
    assert client.delete(f"/categorias/{categoria['id']}").status_code == 204
    assert client.get(f"/categorias/{categoria['id']}").status_code == 404


def test_nao_exclui_categoria_com_produtos(client, produto):
    resp = client.delete(f"/categorias/{produto['categoria_id']}")
    assert resp.status_code == 409


def test_rota_inexistente_retorna_json(client):
    resp = client.get("/nao-existe")
    assert resp.status_code == 404
    assert "erro" in resp.get_json()
