import pytest

from app import create_app
from app.db import init_db


@pytest.fixture
def app(tmp_path):
    """Cada teste roda com um banco novo e isolado (arquivo temporário)."""
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "teste.db")})
    with app.app_context():
        init_db()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def categoria(client):
    resp = client.post("/categorias", json={"nome": "Periféricos"})
    return resp.get_json()


@pytest.fixture
def produto(client, categoria):
    resp = client.post(
        "/produtos",
        json={
            "nome": "Mouse sem fio",
            "sku": "per-001",
            "preco": 89.9,
            "quantidade": 10,
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
        },
    )
    return resp.get_json()
