"""Endpoints da API (camada HTTP)."""
from flask import Blueprint, jsonify, request

from . import repositorio as repo
from .validacao import validar_categoria, validar_movimentacao, validar_produto

bp = Blueprint("api", __name__)


@bp.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------- categorias

@bp.get("/categorias")
def listar_categorias():
    return jsonify(repo.listar_categorias())


@bp.get("/categorias/<int:categoria_id>")
def buscar_categoria(categoria_id):
    return repo.buscar_categoria(categoria_id)


@bp.post("/categorias")
def criar_categoria():
    dados = validar_categoria(request.get_json(silent=True))
    return repo.criar_categoria(**dados), 201


@bp.put("/categorias/<int:categoria_id>")
def atualizar_categoria(categoria_id):
    dados = validar_categoria(request.get_json(silent=True))
    return repo.atualizar_categoria(categoria_id, **dados)


@bp.delete("/categorias/<int:categoria_id>")
def excluir_categoria(categoria_id):
    repo.excluir_categoria(categoria_id)
    return "", 204


# ------------------------------------------------------------------ produtos

@bp.get("/produtos")
def listar_produtos():
    busca = request.args.get("busca")
    categoria_id = request.args.get("categoria_id", type=int)
    return jsonify(repo.listar_produtos(busca=busca, categoria_id=categoria_id))


@bp.get("/produtos/<int:produto_id>")
def buscar_produto(produto_id):
    return repo.buscar_produto(produto_id)


@bp.post("/produtos")
def criar_produto():
    dados = validar_produto(request.get_json(silent=True))
    return repo.criar_produto(dados), 201


@bp.put("/produtos/<int:produto_id>")
def substituir_produto(produto_id):
    dados = validar_produto(request.get_json(silent=True))
    return repo.atualizar_produto(produto_id, dados)


@bp.patch("/produtos/<int:produto_id>")
def atualizar_produto(produto_id):
    dados = validar_produto(request.get_json(silent=True), parcial=True)
    return repo.atualizar_produto(produto_id, dados)


@bp.delete("/produtos/<int:produto_id>")
def excluir_produto(produto_id):
    repo.excluir_produto(produto_id)
    return "", 204


@bp.post("/produtos/<int:produto_id>/movimentacoes")
def movimentar(produto_id):
    dados = validar_movimentacao(request.get_json(silent=True))
    return repo.movimentar_estoque(produto_id, **dados), 201


@bp.get("/produtos/<int:produto_id>/movimentacoes")
def listar_movimentacoes(produto_id):
    return jsonify(repo.listar_movimentacoes(produto_id))


# --------------------------------------------------------------- relatórios

@bp.get("/relatorios/estoque-baixo")
def estoque_baixo():
    return jsonify(repo.produtos_estoque_baixo())


@bp.get("/relatorios/categorias")
def resumo_categorias():
    return jsonify(repo.resumo_por_categoria())
