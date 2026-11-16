"""Validação simples dos dados recebidos no corpo das requisições."""


class ErroValidacao(Exception):
    def __init__(self, erros: dict):
        super().__init__("Dados inválidos")
        self.erros = erros


def validar_categoria(dados: dict | None) -> dict:
    dados = dados or {}
    erros = {}
    nome = dados.get("nome")
    if not isinstance(nome, str) or not nome.strip():
        erros["nome"] = "Campo obrigatório."
    elif len(nome.strip()) > 80:
        erros["nome"] = "Máximo de 80 caracteres."
    if erros:
        raise ErroValidacao(erros)
    return {"nome": nome.strip(), "descricao": dados.get("descricao")}


def validar_produto(dados: dict | None, parcial: bool = False) -> dict:
    """Valida um produto. Com parcial=True (PATCH), só valida os campos enviados."""
    dados = dados or {}
    erros = {}
    limpo = {}

    def obrigatorio(campo):
        return not parcial or campo in dados

    if obrigatorio("nome"):
        nome = dados.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            erros["nome"] = "Campo obrigatório."
        else:
            limpo["nome"] = nome.strip()

    if obrigatorio("sku"):
        sku = dados.get("sku")
        if not isinstance(sku, str) or not sku.strip():
            erros["sku"] = "Campo obrigatório."
        else:
            limpo["sku"] = sku.strip().upper()

    if obrigatorio("preco"):
        preco = dados.get("preco")
        if isinstance(preco, bool) or not isinstance(preco, (int, float)) or preco < 0:
            erros["preco"] = "Deve ser um número maior ou igual a zero."
        else:
            limpo["preco"] = round(float(preco), 2)

    for campo in ("quantidade", "estoque_minimo"):
        if campo in dados:
            valor = dados[campo]
            if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
                erros[campo] = "Deve ser um número inteiro maior ou igual a zero."
            else:
                limpo[campo] = valor

    if "categoria_id" in dados:
        cat = dados["categoria_id"]
        if cat is not None and (isinstance(cat, bool) or not isinstance(cat, int)):
            erros["categoria_id"] = "Deve ser um número inteiro ou null."
        else:
            limpo["categoria_id"] = cat

    if parcial and not limpo and not erros:
        erros["corpo"] = "Envie ao menos um campo para atualizar."

    if erros:
        raise ErroValidacao(erros)
    return limpo


def validar_movimentacao(dados: dict | None) -> dict:
    dados = dados or {}
    erros = {}
    tipo = str(dados.get("tipo", "")).upper()
    if tipo not in ("ENTRADA", "SAIDA"):
        erros["tipo"] = "Use ENTRADA ou SAIDA."
    qtd = dados.get("quantidade")
    if isinstance(qtd, bool) or not isinstance(qtd, int) or qtd <= 0:
        erros["quantidade"] = "Deve ser um número inteiro maior que zero."
    if erros:
        raise ErroValidacao(erros)
    return {"tipo": tipo, "quantidade": qtd}
