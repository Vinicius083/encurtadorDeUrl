from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.core.security import decode_access_token
from app.db.cassandra import get_session
from app.models.domain import Usuario
from app.repositories.usuarios import UsuarioRepository

bearer_scheme = HTTPBearer()


def get_usuario_repository() -> UsuarioRepository:
    return UsuarioRepository(get_session())


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    usuarios: UsuarioRepository = Depends(get_usuario_repository),
) -> Usuario:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado.",
        )

    usuario = usuarios.find_by_id(user_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario nao encontrado.")
    return usuario
