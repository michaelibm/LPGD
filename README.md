# LGPD Manager

Sistema interno de gestao de conformidade com a LGPD (clone funcional do
DataMappingLGPD), com assistente de IA integrado para ajudar no preenchimento
do Mapeamento de Dados (ROPA), classificacao de dados sensiveis, riscos e
planos de acao.

## Rodando com Docker (recomendado)

### Pre-requisitos
- Docker e Docker Compose instalados na sua maquina.

### Passo a passo

```bash
# 1. Clone o repositorio (se ainda nao tiver)
git clone https://github.com/michaelibm/LPGD.git
cd LPGD

# 2. (Opcional) Edite as credenciais do admin no docker-compose.yml
#    LGPD_MANAGER_ADMIN_EMAIL e LGPD_MANAGER_ADMIN_SENHA

# 3. Suba o container
docker compose up --build
```

O sistema vai subir em: **http://localhost:8811**

Login padrao (definido no docker-compose.yml):
- E-mail: `admin@local`
- Senha: `TrocarSenha123!`

**Troque a senha e o e-mail no `docker-compose.yml` antes de subir**, ou defina
via variavel de ambiente:

```bash
LGPD_MANAGER_ADMIN_EMAIL=seuemail@exemplo.com \
LGPD_MANAGER_ADMIN_SENHA=SuaSenhaForte123! \
docker compose up --build
```

### Persistencia de dados

O banco de dados SQLite e a chave de criptografia local ficam salvos no
volume Docker `lgpd_manager_data`, entao seus dados sobrevivem a reinicios
do container. Para resetar tudo do zero:

```bash
docker compose down -v
docker compose up --build
```

### Parar o sistema

```bash
docker compose down
```

## Configurando o Assistente de IA

1. Acesse o sistema e faca login.
2. No menu lateral, clique em **"Configuracoes de IA"**.
3. Escolha o provedor (Anthropic, OpenAI, DeepSeek, GLM, Kimi ou outro
   compativel com a API da OpenAI) e cole sua chave de API.
4. A chave fica **criptografada** no banco de dados local (nunca em texto
   puro) e nunca e reexibida apos salva.
5. Acesse **"Assistente de IA"** no menu para conversar e tirar duvidas
   sobre LGPD, base legal, dados sensiveis e riscos.

## Rodando sem Docker (desenvolvimento local)

```bash
python3 -m venv .venv
source .venv/bin/activate  # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

export LGPD_MANAGER_ADMIN_EMAIL=admin@local
export LGPD_MANAGER_ADMIN_SENHA=TrocarSenha123!

uvicorn app.main:app --host 0.0.0.0 --port 8811 --reload
```

## Modulos disponiveis

- Dashboard com indicadores gerais
- Departamentos
- Processos
- Mapeamento de Dados / ROPA
- Riscos (com calculo automatico de nivel baixo/medio/alto)
- Terceiros (fornecedores, operadores de dados)
- Plano de Acao
- Assistente de IA (chat de apoio ao preenchimento)
- Configuracoes de IA (gerenciamento da chave de API do assistente)

## Seguranca

- Senhas de usuario com hash `pbkdf2_sha256` (nunca em texto puro).
- Sessao via cookie assinado (`itsdangerous`), `httponly`.
- Chave de API de IA criptografada com Fernet (`cryptography`), chave de
  cifra gerada localmente e armazenada fora do banco de dados.
- Nao compartilhe o arquivo `.secret_key` nem o banco `.db` publicamente —
  eles contem a chave de cifra e os dados criptografados, respectivamente.
