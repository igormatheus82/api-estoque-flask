"""Conexão com o banco SQLite usando apenas a biblioteca padrão (sqlite3)."""
import sqlite3
from pathlib import Path

from flask import current_app, g

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def get_db() -> sqlite3.Connection:
    """Retorna a conexão da requisição atual (uma por requisição)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(com_dados_exemplo: bool = False) -> None:
    """Cria as tabelas (e opcionalmente insere dados de exemplo)."""
    db = get_db()
    db.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
    if com_dados_exemplo:
        db.executescript((SQL_DIR / "seed.sql").read_text(encoding="utf-8"))
    db.commit()


def init_app(app) -> None:
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command():
        """flask --app app init-db  ->  recria o banco com dados de exemplo."""
        init_db(com_dados_exemplo=True)
        print("Banco de dados criado com dados de exemplo.")
