"""Fábrica da aplicação Flask."""
import os

from flask import Flask, jsonify

from . import db
from .repositorio import Conflito, NaoEncontrado
from .rotas import bp
from .validacao import ErroValidacao


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.json.sort_keys = False
    app.json.ensure_ascii = False
    app.config["DATABASE"] = os.environ.get("DATABASE", "estoque.db")
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(bp)
    _registrar_erros(app)
    return app


def _registrar_erros(app: Flask) -> None:
    """Respostas de erro padronizadas em JSON."""

    @app.errorhandler(ErroValidacao)
    def erro_validacao(e):
        return jsonify(erro="Dados inválidos", detalhes=e.erros), 400

    @app.errorhandler(NaoEncontrado)
    def nao_encontrado(e):
        return jsonify(erro=str(e)), 404

    @app.errorhandler(Conflito)
    def conflito(e):
        return jsonify(erro=str(e)), 409

    @app.errorhandler(404)
    def rota_inexistente(_e):
        return jsonify(erro="Rota não encontrada."), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(_e):
        return jsonify(erro="Método não permitido."), 405
