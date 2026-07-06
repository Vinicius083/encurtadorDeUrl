from fastapi import APIRouter, status

from app.controllers import urls_controller
from app.schemas.urls import AcessoResponse, UrlResponse

router = APIRouter(tags=["urls"])

router.add_api_route(
    "/url-encurtadas",
    urls_controller.cadastrar_url,
    methods=["POST"],
    response_model=UrlResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/url",
    urls_controller.cadastrar_url,
    methods=["POST"],
    response_model=UrlResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route("/url", urls_controller.listar_urls, methods=["GET"], response_model=list[UrlResponse])
router.add_api_route("/url/{codigo}", urls_controller.buscar_url, methods=["GET"], response_model=UrlResponse)
router.add_api_route("/url/{codigo}", urls_controller.editar_url, methods=["PUT"], response_model=UrlResponse)
router.add_api_route("/url/batch", urls_controller.deletar_urls_em_lote, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
router.add_api_route("/url/{codigo}", urls_controller.deletar_url, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
router.add_api_route("/u/{codigo}", urls_controller.acessar_url, methods=["GET"])
router.add_api_route("/acessos/{codigo}", urls_controller.listar_acessos, methods=["GET"], response_model=list[AcessoResponse])
