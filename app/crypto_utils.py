"""
Criptografia simetrica da API key do provedor de IA.
A chave de cifra e derivada de um segredo local (arquivo .secret_key),
gerado automaticamente na primeira execucao e mantido fora do banco de dados.
"""
import os
import base64
from cryptography.fernet import Fernet

BASE_DIR = os.environ.get(
    "LGPD_MANAGER_DB_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
os.makedirs(BASE_DIR, exist_ok=True)
SECRET_FILE = os.path.join(BASE_DIR, ".secret_key")

_fernet = None


def _get_or_create_secret() -> bytes:
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "rb") as f:
            return f.read().strip()
    key = Fernet.generate_key()
    with open(SECRET_FILE, "wb") as f:
        f.write(key)
    os.chmod(SECRET_FILE, 0o600)
    return key


def get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_get_or_create_secret())
    return _fernet


def cifrar(texto: str) -> str:
    f = get_fernet()
    return f.encrypt(texto.encode("utf-8")).decode("utf-8")


def decifrar(texto_cifrado: str) -> str:
    f = get_fernet()
    return f.decrypt(texto_cifrado.encode("utf-8")).decode("utf-8")
