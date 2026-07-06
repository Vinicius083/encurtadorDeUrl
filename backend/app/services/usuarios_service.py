from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.domain import Usuario
from app.repositories.usuarios import UsuarioRepository
from app.schemas.usuarios import AuthResponse, LoginRequest, UsuarioCreate, UsuarioResponse, UsuarioUpdate


def usuario_to_response(usuario: Usuario) -> UsuarioResponse:
    return UsuarioResponse(
        id=usuario.id,
        codigo=usuario.codigo,
        nome=usuario.nome,
        email=usuario.email,
        criado_em=usuario.criado_em,
        ultimo_login=usuario.ultimo_login,
    )


class UsuarioService:
    def __init__(self, usuarios: UsuarioRepository):
        self.usuarios = usuarios

    def listar(self, limit: int = 50) -> list[UsuarioResponse]:
        return [usuario_to_response(usuario) for usuario in self.usuarios.list(limit)]

    def buscar_por_id(self, usuario_id: int, usuario_atual: Usuario) -> UsuarioResponse:
        self._validar_dono(usuario_id, usuario_atual)
        usuario = self.usuarios.find_by_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")
        return usuario_to_response(usuario)

    def criar(self, payload: UsuarioCreate) -> UsuarioResponse:
        try:
            usuario = self.usuarios.create(payload.nome, str(payload.email), hash_password(payload.senha))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        return usuario_to_response(usuario)

    def registrar(self, payload: UsuarioCreate) -> AuthResponse:
        usuario = self.criar(payload)
        token = create_access_token(str(usuario.id))
        return AuthResponse(token=token, nome=usuario.nome, usuario=usuario)

    def login(self, payload: LoginRequest) -> AuthResponse:
        usuario = self.usuarios.find_by_email(str(payload.email))
        if not usuario or not verify_password(payload.senha, usuario.senha):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha invalidos.")

        self.usuarios.mark_login(usuario.id)
        usuario_atualizado = self.usuarios.find_by_id(usuario.id) or usuario
        token = create_access_token(str(usuario.id))
        return AuthResponse(token=token, nome=usuario.nome, usuario=usuario_to_response(usuario_atualizado))

    def atualizar(self, usuario_id: int, payload: UsuarioUpdate, usuario_atual: Usuario) -> UsuarioResponse:
        self._validar_dono(usuario_id, usuario_atual)
        senha_hash = hash_password(payload.senha) if payload.senha else None
        usuario = self.usuarios.update(usuario_id, payload.nome, senha_hash)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")
        return usuario_to_response(usuario)

    def deletar(self, usuario_id: int, usuario_atual: Usuario) -> None:
        self._validar_dono(usuario_id, usuario_atual)
        if not self.usuarios.delete(usuario_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")

    def _validar_dono(self, usuario_id: int, usuario_atual: Usuario) -> None:
        if usuario_atual.id != usuario_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
