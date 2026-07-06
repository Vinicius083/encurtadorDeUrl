from fastapi import APIRouter, status

from app.controllers import usuarios_controller
from app.schemas.usuarios import AuthResponse, UsuarioResponse

router = APIRouter(tags=["usuarios"])

router.add_api_route("/usuarios", usuarios_controller.listar_usuarios, methods=["GET"], response_model=list[UsuarioResponse])
router.add_api_route("/usuarios/{usuario_id}", usuarios_controller.buscar_usuario, methods=["GET"], response_model=UsuarioResponse)
router.add_api_route(
    "/usuarios",
    usuarios_controller.criar_usuario,
    methods=["POST"],
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/register",
    usuarios_controller.registrar,
    methods=["POST"],
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route("/login", usuarios_controller.login, methods=["POST"], response_model=AuthResponse)
router.add_api_route("/usuarios/{usuario_id}", usuarios_controller.atualizar_usuario, methods=["PUT"], response_model=UsuarioResponse)
router.add_api_route(
    "/usuarios/{usuario_id}",
    usuarios_controller.deletar_usuario,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
)
