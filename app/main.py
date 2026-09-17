"""
LGPD Manager - Aplicacao principal (FastAPI)
Clone funcional do DataMappingLGPD com assistente de IA integrado.
"""
import os
from datetime import datetime
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app import models
from app.auth import hash_senha, verificar_senha, criar_token_sessao, ler_token_sessao
from app import ai_assistant
from app.formgeral_data import PERGUNTAS_FORMGERAL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="LGPD Manager")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.on_event("startup")
def startup():
    init_db()
    db = next(get_db())
    # cria usuario admin padrao se nao existir nenhum usuario
    if db.query(models.Usuario).count() == 0:
        admin_email = os.environ.get("LGPD_MANAGER_ADMIN_EMAIL", "admin@local")
        admin_senha = os.environ.get("LGPD_MANAGER_ADMIN_SENHA", "TrocarSenha123!")
        u = models.Usuario(
            nome="Administrador",
            email=admin_email,
            senha_hash=hash_senha(admin_senha),
            is_admin=True,
        )
        db.add(u)
        db.commit()
        print(f"[startup] Usuario admin criado: {admin_email}")


def usuario_atual(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        return None
    usuario_id = ler_token_sessao(token)
    if not usuario_id:
        return None
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()


def exigir_login(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


# ---------- AUTENTICACAO ----------

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"erro": None})


@app.post("/login")
def login_submit(request: Request, email: str = Form(...), senha: str = Form(...),
                  db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user or not verificar_senha(senha, user.senha_hash):
        return templates.TemplateResponse(request, "login.html", {"erro": "E-mail ou senha invalidos"})
    token = criar_token_sessao(user.id)
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("session_token", token, httponly=True, samesite="lax", max_age=3600 * 8)
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("session_token")
    return resp


# ---------- DASHBOARD ----------

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    stats = {
        "departamentos": db.query(models.Departamento).count(),
        "processos": db.query(models.Processo).count(),
        "mapeamentos": db.query(models.Mapeamento).count(),
        "riscos": db.query(models.Risco).count(),
        "terceiros": db.query(models.Terceiro).count(),
        "titulares": db.query(models.TitularDado).count(),
        "planos_acao": db.query(models.PlanoAcao).count(),
    }
    return templates.TemplateResponse(request, "dashboard.html", {"user": user, "stats": stats})


# ---------- DEPARTAMENTOS ----------

@app.get("/departamentos", response_class=HTMLResponse)
def listar_departamentos(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    itens = db.query(models.Departamento).order_by(models.Departamento.id.desc()).all()
    return templates.TemplateResponse(request, "departamentos.html", {"user": user, "itens": itens})


@app.post("/departamentos/novo")
def criar_departamento(request: Request, nome: str = Form(...), responsavel: str = Form(""),
                        descricao: str = Form(""), db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    d = models.Departamento(nome=nome, responsavel=responsavel, descricao=descricao)
    db.add(d)
    db.commit()
    return RedirectResponse(url="/departamentos", status_code=303)


# ---------- PROCESSOS ----------

@app.get("/processos", response_class=HTMLResponse)
def listar_processos(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    itens = db.query(models.Processo).order_by(models.Processo.id.desc()).all()
    departamentos = db.query(models.Departamento).all()
    return templates.TemplateResponse(
        request, "processos.html", {"user": user, "itens": itens, "departamentos": departamentos}
    )


@app.post("/processos/novo")
def criar_processo(request: Request, nome: str = Form(...), departamento_id: str = Form(""),
                    descricao: str = Form(""), db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    p = models.Processo(
        nome=nome,
        departamento_id=int(departamento_id) if departamento_id else None,
        descricao=descricao,
    )
    db.add(p)
    db.commit()
    return RedirectResponse(url="/processos", status_code=303)


# ---------- MAPEAMENTO DE DADOS (ROPA) ----------

@app.get("/mapeamentos", response_class=HTMLResponse)
def listar_mapeamentos(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    itens = db.query(models.Mapeamento).order_by(models.Mapeamento.id.desc()).all()
    processos = db.query(models.Processo).all()
    finalidades = db.query(models.Finalidade).all()
    return templates.TemplateResponse(
        request,
        "mapeamentos.html",
        {"user": user, "itens": itens, "processos": processos, "finalidades": finalidades},
    )


@app.post("/mapeamentos/novo")
def criar_mapeamento(
    request: Request,
    processo_id: str = Form(""),
    finalidade_id: str = Form(""),
    dados_coletados: str = Form(""),
    dados_sensiveis: str = Form(""),
    titulares: str = Form(""),
    origem_dado: str = Form(""),
    forma_coleta: str = Form(""),
    armazenamento: str = Form(""),
    tempo_retencao: str = Form(""),
    compartilhamento: str = Form(""),
    medidas_seguranca: str = Form(""),
    base_legal: str = Form(""),
    db: Session = Depends(get_db),
):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    m = models.Mapeamento(
        processo_id=int(processo_id) if processo_id else None,
        finalidade_id=int(finalidade_id) if finalidade_id else None,
        dados_coletados=dados_coletados,
        dados_sensiveis=(dados_sensiveis == "on"),
        titulares=titulares,
        origem_dado=origem_dado,
        forma_coleta=forma_coleta,
        armazenamento=armazenamento,
        tempo_retencao=tempo_retencao,
        compartilhamento=compartilhamento,
        medidas_seguranca=medidas_seguranca,
        base_legal=base_legal,
    )
    db.add(m)
    db.commit()
    return RedirectResponse(url="/mapeamentos", status_code=303)


# ---------- RISCOS ----------

@app.get("/riscos", response_class=HTMLResponse)
def listar_riscos(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    itens = db.query(models.Risco).order_by(models.Risco.id.desc()).all()
    return templates.TemplateResponse(request, "riscos.html", {"user": user, "itens": itens})


def calcular_nivel_risco(probabilidade: str, impacto: str) -> str:
    escala = {"Baixa": 1, "Baixo": 1, "Media": 2, "Medio": 2, "Alta": 3, "Alto": 3}
    p = escala.get(probabilidade, 1)
    i = escala.get(impacto, 1)
    score = p * i
    if score <= 2:
        return "Baixo"
    if score <= 6:
        return "Medio"
    return "Alto"


@app.post("/riscos/novo")
def criar_risco(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(""),
    probabilidade: str = Form("Baixa"),
    impacto: str = Form("Baixo"),
    db: Session = Depends(get_db),
):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    nivel = calcular_nivel_risco(probabilidade, impacto)
    r = models.Risco(
        titulo=titulo, descricao=descricao, probabilidade=probabilidade,
        impacto=impacto, nivel_risco=nivel,
    )
    db.add(r)
    db.commit()
    return RedirectResponse(url="/riscos", status_code=303)


# ---------- TERCEIROS ----------

@app.get("/terceiros", response_class=HTMLResponse)
def listar_terceiros(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    itens = db.query(models.Terceiro).order_by(models.Terceiro.id.desc()).all()
    return templates.TemplateResponse(request, "terceiros.html", {"user": user, "itens": itens})


@app.post("/terceiros/novo")
def criar_terceiro(
    request: Request,
    nome: str = Form(...),
    cnpj_cpf: str = Form(""),
    tipo_relacao: str = Form(""),
    dados_compartilhados: str = Form(""),
    contrato_dpa: str = Form(""),
    db: Session = Depends(get_db),
):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    t = models.Terceiro(
        nome=nome, cnpj_cpf=cnpj_cpf, tipo_relacao=tipo_relacao,
        dados_compartilhados=dados_compartilhados, contrato_dpa=(contrato_dpa == "on"),
    )
    db.add(t)
    db.commit()
    return RedirectResponse(url="/terceiros", status_code=303)


# ---------- PLANO DE ACAO ----------

@app.get("/plano-acao", response_class=HTMLResponse)
def listar_plano_acao(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    itens = db.query(models.PlanoAcao).order_by(models.PlanoAcao.id.desc()).all()
    riscos = db.query(models.Risco).all()
    return templates.TemplateResponse(request, "plano_acao.html", {"user": user, "itens": itens, "riscos": riscos})


@app.post("/plano-acao/novo")
def criar_plano_acao(
    request: Request,
    titulo: str = Form(...),
    descricao: str = Form(""),
    responsavel: str = Form(""),
    risco_id: str = Form(""),
    db: Session = Depends(get_db),
):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    p = models.PlanoAcao(
        titulo=titulo, descricao=descricao, responsavel=responsavel,
        risco_id=int(risco_id) if risco_id else None,
    )
    db.add(p)
    db.commit()
    return RedirectResponse(url="/plano-acao", status_code=303)


# ---------- ASSISTENTE DE IA ----------

@app.get("/assistente", response_class=HTMLResponse)
def assistente_page(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    historico = (
        db.query(models.ChatMensagem)
        .filter(models.ChatMensagem.usuario_id == user.id)
        .order_by(models.ChatMensagem.id.asc())
        .all()
    )
    return templates.TemplateResponse(request, "assistente.html", {"user": user, "historico": historico})


@app.post("/api/assistente/mensagem")
async def assistente_mensagem(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Nao autenticado")

    body = await request.json()
    mensagem = (body.get("mensagem") or "").strip()
    contexto_modulo = body.get("contexto_modulo")
    dados_contexto = body.get("dados_contexto")

    if not mensagem:
        raise HTTPException(status_code=400, detail="Mensagem vazia")

    historico_db = (
        db.query(models.ChatMensagem)
        .filter(models.ChatMensagem.usuario_id == user.id)
        .order_by(models.ChatMensagem.id.asc())
        .all()
    )
    historico = [{"role": h.papel, "content": h.conteudo} for h in historico_db[-20:]]

    msg_user = models.ChatMensagem(
        usuario_id=user.id, papel="user", conteudo=mensagem, contexto_modulo=contexto_modulo
    )
    db.add(msg_user)
    db.commit()

    try:
        resposta_texto = ai_assistant.responder(
            db, historico, mensagem, contexto_modulo=contexto_modulo, dados_contexto=dados_contexto
        )
    except ai_assistant.ConfiguracaoAusente as e:
        resposta_texto = str(e)
    except Exception as e:
        resposta_texto = f"Erro ao consultar o assistente de IA: {e}"

    msg_assistant = models.ChatMensagem(
        usuario_id=user.id, papel="assistant", conteudo=resposta_texto, contexto_modulo=contexto_modulo
    )
    db.add(msg_assistant)
    db.commit()

    return JSONResponse({"resposta": resposta_texto})


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


# ---------- CONFIGURACAO DE IA ----------

from app.crypto_utils import cifrar  # noqa: E402


@app.get("/configuracoes-ia", response_class=HTMLResponse)
def configuracoes_ia_page(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    config = (
        db.query(models.ConfiguracaoIA)
        .filter(models.ConfiguracaoIA.ativo == True)  # noqa: E712
        .order_by(models.ConfiguracaoIA.id.desc())
        .first()
    )
    return templates.TemplateResponse(
        request, "configuracoes_ia.html", {"user": user, "config": config, "mensagem": None, "erro": None}
    )


@app.post("/configuracoes-ia")
def configuracoes_ia_salvar(
    request: Request,
    provedor: str = Form(...),
    api_key: str = Form(...),
    modelo: str = Form(""),
    base_url: str = Form(""),
    db: Session = Depends(get_db),
):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # desativa configuracoes anteriores
    db.query(models.ConfiguracaoIA).update({models.ConfiguracaoIA.ativo: False})

    nova = models.ConfiguracaoIA(
        provedor=provedor,
        modelo=modelo or None,
        base_url=base_url or None,
        api_key_cifrada=cifrar(api_key),
        ativo=True,
    )
    db.add(nova)
    db.commit()

    return RedirectResponse(url="/configuracoes-ia?salvo=1", status_code=303)


# ---------- EMPRESAS ----------

@app.get("/empresas", response_class=HTMLResponse)
def listar_empresas(request: Request, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    itens = db.query(models.Empresa).order_by(models.Empresa.id.desc()).all()
    return templates.TemplateResponse(request, "empresas.html", {"user": user, "itens": itens})


@app.post("/empresas/novo")
def criar_empresa(
    request: Request,
    nome: str = Form(...),
    cpf_cnpj: str = Form(""),
    telefone: str = Form(""),
    email: str = Form(""),
    cep: str = Form(""),
    observacoes: str = Form(""),
    db: Session = Depends(get_db),
):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    e = models.Empresa(
        nome=nome, cpf_cnpj=cpf_cnpj, telefone=telefone, email=email,
        cep=cep, observacoes=observacoes, status=True,
    )
    db.add(e)
    db.commit()
    return RedirectResponse(url="/empresas", status_code=303)


@app.post("/empresas/{empresa_id}/editar")
def editar_empresa(
    request: Request,
    empresa_id: int,
    nome: str = Form(...),
    telefone: str = Form(""),
    email: str = Form(""),
    cep: str = Form(""),
    status: str = Form(""),
    observacoes: str = Form(""),
    db: Session = Depends(get_db),
):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    e = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if e:
        e.nome = nome
        e.telefone = telefone
        e.email = email
        e.cep = cep
        e.status = (status == "1")
        e.observacoes = observacoes
        db.commit()
    return RedirectResponse(url="/empresas", status_code=303)


# ---------- FORMULARIO GERAL (questionario de diagnostico LGPD) ----------

def calcular_percentual_adequacao(respostas_map: dict) -> int:
    """Percentual de perguntas respondidas com SIM sobre o total aplicavel (exclui NAO SE APLICA e pendentes)."""
    total_aplicavel = 0
    total_sim = 0
    for p in PERGUNTAS_FORMGERAL:
        resp = respostas_map.get(p["numero"])
        if resp in ("S", "N"):
            total_aplicavel += 1
            if resp == "S":
                total_sim += 1
    if total_aplicavel == 0:
        return 0
    return round((total_sim / total_aplicavel) * 100)


@app.get("/empresas/{empresa_id}/formulario-geral", response_class=HTMLResponse)
def formulario_geral_page(request: Request, empresa_id: int, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        return RedirectResponse(url="/empresas", status_code=303)

    respostas = (
        db.query(models.FormularioGeralResposta)
        .filter(models.FormularioGeralResposta.empresa_id == empresa_id)
        .all()
    )
    respostas_map = {r.pergunta_id: r.resposta for r in respostas}
    observacoes_map = {r.pergunta_id: r.observacao for r in respostas}
    percentual = calcular_percentual_adequacao(respostas_map)

    return templates.TemplateResponse(
        request,
        "formulario_geral.html",
        {
            "user": user,
            "empresa": empresa,
            "perguntas": PERGUNTAS_FORMGERAL,
            "respostas_map": respostas_map,
            "observacoes_map": observacoes_map,
            "percentual": percentual,
        },
    )


@app.post("/empresas/{empresa_id}/formulario-geral")
async def formulario_geral_salvar(request: Request, empresa_id: int, db: Session = Depends(get_db)):
    user = usuario_atual(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    form = await request.form()

    for p in PERGUNTAS_FORMGERAL:
        numero = p["numero"]
        resposta_valor = form.get(f"Q_{numero}") or None
        observacao_valor = form.get(f"obs_{numero}") or None

        existente = (
            db.query(models.FormularioGeralResposta)
            .filter(
                models.FormularioGeralResposta.empresa_id == empresa_id,
                models.FormularioGeralResposta.pergunta_id == numero,
            )
            .first()
        )
        if existente:
            existente.resposta = resposta_valor
            existente.observacao = observacao_valor
        else:
            nova_resposta = models.FormularioGeralResposta(
                empresa_id=empresa_id,
                pergunta_id=numero,
                resposta=resposta_valor,
                observacao=observacao_valor,
            )
            db.add(nova_resposta)

    db.commit()
    return RedirectResponse(url=f"/empresas/{empresa_id}/formulario-geral?salvo=1", status_code=303)
