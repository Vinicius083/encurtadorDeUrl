from dataclasses import dataclass
from datetime import datetime


@dataclass
class Usuario:
    id: int
    codigo: str
    nome: str
    email: str
    senha: str
    criado_em: datetime
    ultimo_login: datetime | None


@dataclass
class UrlEncurtada:
    codigo: str
    url_original: str
    usuario_id: int
    criado_em: datetime
    atualizado_em: datetime
    desabilitado: bool
    data_expiracao: datetime | None
    qr_code: str | None


@dataclass
class AcessoUrlEncurtada:
    codigo: str
    dia: object
    id: int
    acessado_em: datetime
