from fastapi import Depends, Response, status

from app.api.dependencies import get_current_user, get_usuario_repository
from app.models.domain import Usuario
from app.repositories.usuarios import UsuarioRepository
from app.schemas.usuarios import AuthResponse, LoginRequest, UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.usuarios_service import UsuarioService


def get_usuario_service(usuarios: UsuarioRepository = Depends(get_usuario_repository)) -> UsuarioService:
    return UsuarioService(usuarios)


def listar_usuarios(
    limit: int = 50,
    service: UsuarioService = Depends(get_usuario_service),
    _: Usuario = Depends(get_current_user),
) -> list[UsuarioResponse]:
    return service.listar(limit)


def buscar_usuario(
    usuario_id: int,
    service: UsuarioService = Depends(get_usuario_service),
    atual: Usuario = Depends(get_current_user),
) -> UsuarioResponse:
    return service.buscar_por_id(usuario_id, atual)


def criar_usuario(
    payload: UsuarioCreate,
    service: UsuarioService = Depends(get_usuario_service),
) -> UsuarioResponse:
    return service.criar(payload)


def registrar(
    payload: UsuarioCreate,
    service: UsuarioService = Depends(get_usuario_service),
) -> AuthResponse:
    return service.registrar(payload)


def login(
    payload: LoginRequest,
    service: UsuarioService = Depends(get_usuario_service),
) -> AuthResponse:
    return service.login(payload)


def atualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    service: UsuarioService = Depends(get_usuario_service),
    atual: Usuario = Depends(get_current_user),
) -> UsuarioResponse:
    return service.atualizar(usuario_id, payload, atual)


def deletar_usuario(
    usuario_id: int,
    service: UsuarioService = Depends(get_usuario_service),
    atual: Usuario = Depends(get_current_user),
) -> Response:
    service.deletar(usuario_id, atual)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
