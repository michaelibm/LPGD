"""
Assistente de IA integrado ao LGPD Manager.
Ajuda o usuario a preencher Mapeamentos de Dados (ROPA), sugerindo
base legal, dados sensiveis, prazos de retencao e riscos.

Suporta multiplos provedores configurados dentro do proprio sistema
(tela /configuracoes-ia), sem depender de variaveis de ambiente do host:
- anthropic (Claude, API nativa)
- openai (GPT, API nativa)
- compativel com OpenAI (DeepSeek, GLM/Zhipu, Kimi, etc.) via base_url customizada
"""
from sqlalchemy.orm import Session
from app import models
from app.crypto_utils import decifrar

SYSTEM_PROMPT = """Voce e o assistente de IA do LGPD Manager, um sistema interno de \
gestao de conformidade com a LGPD (Lei Geral de Protecao de Dados) e Provimentos do CNJ \
para cartorios e empresas no Brasil.

Seu papel e ajudar o usuario a:
1. Preencher corretamente o Mapeamento de Dados (ROPA - Registro de Operacoes de \
Tratamento de Dados Pessoais): processo, finalidade, dados coletados, se ha dados \
sensiveis, titulares, origem, forma de coleta, armazenamento, prazo de retencao, \
compartilhamento com terceiros, medidas de seguranca e base legal (art. 7 ou art. 11 \
da LGPD).
2. Sugerir a base legal mais adequada (consentimento, cumprimento de obrigacao legal, \
execucao de contrato, legitimo interesse, protecao da vida, exercicio regular de \
direitos, etc.) considerando o contexto informado.
3. Identificar se os dados descritos sao sensiveis (art. 5, II da LGPD: origem racial \
ou etnica, conviccao religiosa, opiniao politica, filiacao a sindicato/organizacao de \
carater religioso/filosofico/politico, dado referente a saude ou vida sexual, dado \
genetico ou biometrico).
4. Sugerir riscos associados ao tratamento descrito (vazamento, uso indevido, retencao \
excessiva, falta de base legal, compartilhamento sem salvaguardas) e propor planos de \
acao objetivos.
5. Ser direto, claro e em portugues do Brasil. Quando faltar informacao para preencher \
um campo, pergunte objetivamente. Nao invente dados especificos da empresa do usuario \
(CNPJ, nomes reais, numeros) - peca que ele informe.
6. Nunca sugira armazenar segredos, senhas ou dados sensiveis desnecessarios no proprio \
sistema.

Responda de forma pratica, pronta para o usuario copiar para o formulario, quando fizer \
sentido (ex: "Base legal sugerida: Execucao de contrato (art. 7, V, LGPD)").
"""

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-5",
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "glm": "glm-4.6",
    "kimi": "kimi-k2-0905-preview",
}

DEFAULT_BASE_URLS = {
    "deepseek": "https://api.deepseek.com",
    "glm": "https://open.bigmodel.cn/api/paas/v4",
    "kimi": "https://api.moonshot.cn/v1",
}


class ConfiguracaoAusente(Exception):
    pass


def obter_configuracao_ativa(db: Session) -> models.ConfiguracaoIA | None:
    return (
        db.query(models.ConfiguracaoIA)
        .filter(models.ConfiguracaoIA.ativo == True)  # noqa: E712
        .order_by(models.ConfiguracaoIA.id.desc())
        .first()
    )


def montar_contexto_sistema(contexto_modulo, dados_contexto) -> str:
    if not contexto_modulo and not dados_contexto:
        return ""
    partes = []
    if contexto_modulo:
        partes.append(f"Modulo atual do usuario: {contexto_modulo}")
    if dados_contexto:
        for k, v in dados_contexto.items():
            if v:
                partes.append(f"{k}: {v}")
    if not partes:
        return ""
    return "\n\n[Contexto atual do formulario]\n" + "\n".join(partes)


def _responder_anthropic(api_key, modelo, historico, mensagem_final):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    mensagens = list(historico) + [{"role": "user", "content": mensagem_final}]
    resposta = client.messages.create(
        model=modelo or DEFAULT_MODELS["anthropic"],
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=mensagens,
    )
    texto = ""
    for bloco in resposta.content:
        if bloco.type == "text":
            texto += bloco.text
    return texto or "(sem resposta)"


def _responder_openai_compat(api_key, modelo, base_url, historico, mensagem_final):
    from openai import OpenAI
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}] + list(historico) + [
        {"role": "user", "content": mensagem_final}
    ]
    resposta = client.chat.completions.create(
        model=modelo,
        messages=mensagens,
        max_tokens=1024,
    )
    return resposta.choices[0].message.content or "(sem resposta)"


def responder(db: Session, historico: list[dict], mensagem_usuario: str,
              contexto_modulo: str = None, dados_contexto: dict = None) -> str:
    config = obter_configuracao_ativa(db)
    if not config:
        raise ConfiguracaoAusente(
            "Nenhum provedor de IA configurado. Acesse Configuracoes de IA no menu para "
            "cadastrar sua chave de API."
        )

    api_key = decifrar(config.api_key_cifrada)
    contexto_extra = montar_contexto_sistema(contexto_modulo, dados_contexto)
    mensagem_final = mensagem_usuario + contexto_extra
    modelo = config.modelo or DEFAULT_MODELS.get(config.provedor)
    base_url = config.base_url or DEFAULT_BASE_URLS.get(config.provedor)

    if config.provedor == "anthropic":
        return _responder_anthropic(api_key, modelo, historico, mensagem_final)
    else:
        # openai, deepseek, glm, kimi e qualquer compativel com API OpenAI
        return _responder_openai_compat(api_key, modelo, base_url, historico, mensagem_final)
