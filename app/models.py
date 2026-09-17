"""
LGPD Manager - modelos de banco de dados (SQLAlchemy)
Clone funcional do DataMappingLGPD para uso interno.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)


class Departamento(Base):
    __tablename__ = "departamentos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    responsavel = Column(String(200))
    descricao = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

    processos = relationship("Processo", back_populates="departamento")


class Finalidade(Base):
    __tablename__ = "finalidades"
    id = Column(Integer, primary_key=True)
    nome = Column(String(300), nullable=False)
    descricao = Column(Text)
    base_legal = Column(String(200))
    criado_em = Column(DateTime, default=datetime.utcnow)


class Processo(Base):
    __tablename__ = "processos"
    id = Column(Integer, primary_key=True)
    nome = Column(String(300), nullable=False)
    departamento_id = Column(Integer, ForeignKey("departamentos.id"))
    descricao = Column(Text)
    status = Column(String(50), default="Em andamento")
    criado_em = Column(DateTime, default=datetime.utcnow)

    departamento = relationship("Departamento", back_populates="processos")
    mapeamentos = relationship("Mapeamento", back_populates="processo")


class Mapeamento(Base):
    """Registro de Operacoes de Tratamento de Dados (ROPA base)"""
    __tablename__ = "mapeamentos"
    id = Column(Integer, primary_key=True)
    processo_id = Column(Integer, ForeignKey("processos.id"))
    finalidade_id = Column(Integer, ForeignKey("finalidades.id"))
    dados_coletados = Column(Text)  # lista textual de dados pessoais
    dados_sensiveis = Column(Boolean, default=False)
    titulares = Column(String(300))  # ex: clientes, funcionarios, fornecedores
    origem_dado = Column(String(300))
    forma_coleta = Column(String(300))
    armazenamento = Column(String(300))
    tempo_retencao = Column(String(200))
    compartilhamento = Column(Text)
    medidas_seguranca = Column(Text)
    base_legal = Column(String(200))
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    processo = relationship("Processo", back_populates="mapeamentos")


class Risco(Base):
    __tablename__ = "riscos"
    id = Column(Integer, primary_key=True)
    mapeamento_id = Column(Integer, ForeignKey("mapeamentos.id"), nullable=True)
    titulo = Column(String(300), nullable=False)
    descricao = Column(Text)
    probabilidade = Column(String(50))  # Baixa / Media / Alta
    impacto = Column(String(50))  # Baixo / Medio / Alto
    nivel_risco = Column(String(50))  # calculado
    status = Column(String(50), default="Aberto")
    criado_em = Column(DateTime, default=datetime.utcnow)


class Terceiro(Base):
    __tablename__ = "terceiros"
    id = Column(Integer, primary_key=True)
    nome = Column(String(300), nullable=False)
    cnpj_cpf = Column(String(30))
    tipo_relacao = Column(String(100))  # fornecedor, parceiro, operador
    dados_compartilhados = Column(Text)
    contrato_dpa = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)


class TitularDado(Base):
    __tablename__ = "titulares_dados"
    id = Column(Integer, primary_key=True)
    nome = Column(String(300), nullable=False)
    categoria = Column(String(100))  # cliente, funcionario, fornecedor
    email = Column(String(200))
    telefone = Column(String(50))
    observacoes = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)


class PlanoAcao(Base):
    __tablename__ = "planos_acao"
    id = Column(Integer, primary_key=True)
    risco_id = Column(Integer, ForeignKey("riscos.id"), nullable=True)
    titulo = Column(String(300), nullable=False)
    descricao = Column(Text)
    responsavel = Column(String(200))
    prazo = Column(DateTime, nullable=True)
    status = Column(String(50), default="Pendente")
    criado_em = Column(DateTime, default=datetime.utcnow)


class ConfiguracaoIA(Base):
    """Configuracao do provedor de IA usado pelo assistente (chave criptografada)."""
    __tablename__ = "configuracao_ia"
    id = Column(Integer, primary_key=True)
    provedor = Column(String(50), nullable=False, default="anthropic")  # anthropic, openai, deepseek, glm
    modelo = Column(String(100), nullable=True)
    api_key_cifrada = Column(Text, nullable=False)
    base_url = Column(String(300), nullable=True)  # para provedores compat. OpenAI (deepseek, glm, etc.)
    ativo = Column(Boolean, default=True)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMensagem(Base):
    """Historico do assistente de IA (chat de apoio ao preenchimento)"""
    __tablename__ = "chat_mensagens"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    papel = Column(String(20))  # user / assistant
    conteudo = Column(Text)
    contexto_modulo = Column(String(100), nullable=True)  # ex: mapeamento, risco
    criado_em = Column(DateTime, default=datetime.utcnow)
