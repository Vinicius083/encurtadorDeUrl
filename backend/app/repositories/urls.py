from datetime import date, datetime, timezone

from cassandra.cluster import Session
from nanoid import generate

from app.core.config import get_settings
from app.models.domain import AcessoUrlEncurtada, UrlEncurtada
from app.repositories.utils import insert_with_random_id


class UrlRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_by_user(self, usuario_id: int, limit: int = 50) -> list[UrlEncurtada]:
        rows = self.session.execute(
            "SELECT * FROM urls_by_usuario WHERE usuario_id = %s LIMIT %s",
            (usuario_id, limit),
        )
        return [self._row_to_url(row) for row in rows]

    def find_by_codigo(self, codigo: str) -> UrlEncurtada | None:
        row = self.session.execute(
            "SELECT * FROM urls_by_codigo WHERE codigo = %s",
            (codigo,),
        ).one()
        return self._row_to_url(row) if row else None

    def create(
        self,
        usuario_id: int,
        url_original: str,
        alias: str | None,
        data_expiracao: datetime | None,
    ) -> UrlEncurtada:
        codigo = alias or generate(size=8)
        if self.find_by_codigo(codigo):
            raise ValueError("Alias/codigo ja cadastrado.")

        now = datetime.now(timezone.utc)
        qr_code = f"{get_settings().api_base_url}/u/{codigo}"
        url = UrlEncurtada(codigo, url_original, usuario_id, now, now, False, data_expiracao, qr_code)
        self._insert_url(url)
        return url

    def update_redirect(
        self,
        codigo: str,
        usuario_id: int,
        url_original: str,
        data_expiracao: datetime | None,
        desabilitado: bool | None,
        manter_expiracao: bool,
    ) -> UrlEncurtada | None:
        atual = self.find_by_codigo(codigo)
        if not atual or atual.usuario_id != usuario_id:
            return None

        nova = UrlEncurtada(
            codigo=atual.codigo,
            url_original=url_original,
            usuario_id=atual.usuario_id,
            criado_em=atual.criado_em,
            atualizado_em=datetime.now(timezone.utc),
            desabilitado=atual.desabilitado if desabilitado is None else desabilitado,
            data_expiracao=atual.data_expiracao if manter_expiracao else data_expiracao,
            qr_code=atual.qr_code,
        )

        self._delete_from_user_index(atual)
        self._insert_url(nova)
        return nova

    def delete(self, codigo: str, usuario_id: int) -> bool:
        atual = self.find_by_codigo(codigo)
        if not atual or atual.usuario_id != usuario_id:
            return False

        self.session.execute("DELETE FROM urls_by_codigo WHERE codigo = %s", (codigo,))
        self._delete_from_user_index(atual)
        return True

    def register_access(self, codigo: str) -> AcessoUrlEncurtada:
        accessed_at = datetime.now(timezone.utc)
        access_day = accessed_at.date()
        query = """
            INSERT INTO acessos_url_encurtada (codigo, dia, id, acessado_em)
            VALUES (%s, %s, %s, %s)
            IF NOT EXISTS
        """
        access_id = insert_with_random_id(
            self.session,
            query,
            lambda entity_id: (codigo, access_day, entity_id, accessed_at),
        )
        return AcessoUrlEncurtada(codigo, access_day, access_id, accessed_at)

    def list_accesses(self, codigo: str, access_day: date | None = None, limit: int = 100) -> list[AcessoUrlEncurtada]:
        if access_day:
            rows = self.session.execute(
                "SELECT * FROM acessos_url_encurtada WHERE codigo = %s AND dia = %s LIMIT %s",
                (codigo, access_day, limit),
            )
        else:
            today = datetime.now(timezone.utc).date()
            rows = self.session.execute(
                "SELECT * FROM acessos_url_encurtada WHERE codigo = %s AND dia = %s LIMIT %s",
                (codigo, today, limit),
            )
        return [
            AcessoUrlEncurtada(row.codigo, self._to_python_date(row.dia), row.id, row.acessado_em)
            for row in rows
        ]

    def increment_access_counter(self, codigo: str) -> None:
        self.session.execute(
            "UPDATE url_access_counters SET access_count = access_count + 1 WHERE codigo = %s",
            (codigo,),
        )

    def get_access_count(self, codigo: str) -> int:
        row = self.session.execute(
            "SELECT access_count FROM url_access_counters WHERE codigo = %s",
            (codigo,),
        ).one()
        return row.access_count if row else 0

    def _to_python_date(self, value) -> date:
        if isinstance(value, date):
            return value
        if hasattr(value, "date"):
            return value.date()
        raise ValueError("Data de acesso invalida retornada pelo Cassandra.")

    def _insert_url(self, url: UrlEncurtada) -> None:
        self.session.execute(
            """
            INSERT INTO urls_by_codigo
            (codigo, url_original, usuario_id, criado_em, atualizado_em, desabilitado, data_expiracao, qr_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                url.codigo,
                url.url_original,
                url.usuario_id,
                url.criado_em,
                url.atualizado_em,
                url.desabilitado,
                url.data_expiracao,
                url.qr_code,
            ),
        )
        self.session.execute(
            """
            INSERT INTO urls_by_usuario
            (usuario_id, criado_em, codigo, url_original, atualizado_em, desabilitado, data_expiracao, qr_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                url.usuario_id,
                url.criado_em,
                url.codigo,
                url.url_original,
                url.atualizado_em,
                url.desabilitado,
                url.data_expiracao,
                url.qr_code,
            ),
        )

    def _delete_from_user_index(self, url: UrlEncurtada) -> None:
        self.session.execute(
            "DELETE FROM urls_by_usuario WHERE usuario_id = %s AND criado_em = %s AND codigo = %s",
            (url.usuario_id, url.criado_em, url.codigo),
        )

    def _row_to_url(self, row) -> UrlEncurtada:
        return UrlEncurtada(
            codigo=row.codigo,
            url_original=row.url_original,
            usuario_id=row.usuario_id,
            criado_em=row.criado_em,
            atualizado_em=row.atualizado_em,
            desabilitado=row.desabilitado,
            data_expiracao=row.data_expiracao,
            qr_code=row.qr_code,
        )
