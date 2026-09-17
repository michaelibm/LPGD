from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
import os

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.environ.get("LGPD_MANAGER_SECRET", "troque-esta-chave-em-producao-lgpd-manager")
serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def criar_token_sessao(usuario_id: int) -> str:
    return serializer.dumps({"usuario_id": usuario_id})


def ler_token_sessao(token: str, max_age: int = 3600 * 8):
    try:
        data = serializer.loads(token, max_age=max_age)
        return data.get("usuario_id")
    except Exception:
        return None
