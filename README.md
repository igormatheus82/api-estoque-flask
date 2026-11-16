# API de Controle de Estoque — Python + Flask + SQL

![CI](https://github.com/igormatheus82/api-estoque-flask/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3-black)
![SQL](https://img.shields.io/badge/SQL-SQLite-003B57)

API REST para controle de estoque com **CRUD completo em SQL puro** (sem ORM), validação de dados, histórico de movimentações e relatórios. Projeto criado para praticar **Python, SQL, design de APIs e testes automatizados**.

## Funcionalidades

- CRUD de **categorias** e **produtos** (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`)
- Busca de produtos por nome/SKU e filtro por categoria
- **Entradas e saídas de estoque** em transação, com histórico (auditoria)
- Regra de negócio: não permite saída maior que o saldo disponível
- Relatórios com SQL: **estoque abaixo do mínimo** e **valor em estoque por categoria** (`JOIN`, `GROUP BY`, `SUM`)
- Respostas de erro padronizadas em JSON (`400`, `404`, `405`, `409`)
- Consultas parametrizadas (proteção contra SQL Injection)
- **39 testes automatizados** com pytest + pipeline de CI no GitHub Actions

## Tecnologias

| Camada | Ferramenta |
|---|---|
| Linguagem | Python 3.11+ |
| Framework web | Flask 3 |
| Banco de dados | SQLite (`sqlite3` da biblioteca padrão) |
| Testes | pytest |
| CI | GitHub Actions |

## Estrutura

```
api-estoque-flask/
├── app/
│   ├── __init__.py      # fábrica da aplicação e tratamento de erros
│   ├── db.py            # conexão com o banco e comando init-db
│   ├── repositorio.py   # todo o SQL (camada de dados)
│   ├── rotas.py         # endpoints HTTP
│   └── validacao.py     # validação dos dados de entrada
├── sql/
│   ├── schema.sql       # criação das tabelas
│   ├── seed.sql         # dados de exemplo
│   └── consultas.sql    # consultas SQL de estudo (CRUD, JOIN, GROUP BY, subconsulta)
├── tests/               # testes automatizados (pytest)
├── requisicoes.http     # exemplos de requisições
└── .github/workflows/   # pipeline de CI
```

## Como rodar

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/igormatheus82/api-estoque-flask.git
cd api-estoque-flask

# 2. Criar ambiente virtual e instalar dependências
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Criar o banco com dados de exemplo
flask --app app init-db

# 4. Subir a API em http://localhost:5000
flask --app app run --debug
```

## Rodando os testes

```bash
pytest -v
```

Cada teste usa um banco temporário e isolado, então os testes não interferem uns nos outros nem no banco de desenvolvimento.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Verifica se a API está no ar |
| GET | `/categorias` | Lista categorias |
| GET | `/categorias/{id}` | Busca categoria |
| POST | `/categorias` | Cria categoria |
| PUT | `/categorias/{id}` | Atualiza categoria |
| DELETE | `/categorias/{id}` | Exclui categoria (bloqueia se tiver produtos) |
| GET | `/produtos?busca=&categoria_id=` | Lista produtos com filtros |
| GET | `/produtos/{id}` | Busca produto |
| POST | `/produtos` | Cria produto |
| PUT | `/produtos/{id}` | Substitui produto |
| PATCH | `/produtos/{id}` | Atualiza campos específicos |
| DELETE | `/produtos/{id}` | Exclui produto |
| POST | `/produtos/{id}/movimentacoes` | Registra ENTRADA ou SAIDA |
| GET | `/produtos/{id}/movimentacoes` | Histórico de movimentações |
| GET | `/relatorios/estoque-baixo` | Produtos abaixo do estoque mínimo |
| GET | `/relatorios/categorias` | Total de itens e valor por categoria |

### Exemplo

```http
POST /produtos
Content-Type: application/json

{ "nome": "Mouse sem fio", "sku": "PER-001", "preco": 89.9, "quantidade": 40, "estoque_minimo": 10, "categoria_id": 1 }
```

```json
{
  "id": 1,
  "nome": "Mouse sem fio",
  "sku": "PER-001",
  "preco": 89.9,
  "quantidade": 40,
  "estoque_minimo": 10,
  "categoria_id": 1,
  "categoria_nome": "Periféricos",
  "criado_em": "2026-11-16 15:00:00",
  "atualizado_em": "2026-11-16 15:00:00"
}
```

Erro de validação (`400`):

```json
{ "erro": "Dados inválidos", "detalhes": { "preco": "Deve ser um número maior ou igual a zero." } }
```

## Próximos passos

- [ ] Paginação na listagem de produtos
- [ ] Documentação OpenAPI/Swagger
- [ ] Versão com PostgreSQL via Docker

---

Feito por **Igor Cavalcante** · [LinkedIn](https://www.linkedin.com/in/cavalcanteigor)
