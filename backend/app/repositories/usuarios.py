from datetime import datetime, timezone

from cassandra.cluster import Session
from nanoid import generate

from app.models.domain import Usuario
from app.repositories.utils import insert_with_random_id


class UsuarioRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, limit: int = 50) -> list[Usuario]:
        rows = self.session.execute("SELECT * FROM usuarios_by_id LIMIT %s", (limit,))
        return [self._row_to_usuario(row) for row in rows]

    def find_by_id(self, user_id: int) -> Usuario | None:
        row = self.session.execute("SELECT * FROM usuarios_by_id WHERE id = %s", (user_id,)).one()
        return self._row_to_usuario(row) if row else None

    def find_by_email(self, email: str) -> Usuario | None:
        row = self.session.execute(
            "SELECT * FROM usuarios_by_email WHERE email = %s",
            (email.lower(),),
        ).one()
        return self._row_to_usuario(row) if row else None

    def create(self, nome: str, email: str, senha_hash: str) -> Usuario:
        email = email.lower()
        if self.find_by_email(email):
            raise ValueError("Email ja cadastrado.")

        codigo = generate(size=10)
        criado_em = datetime.now(timezone.utc)

        query = """
            INSERT INTO usuarios_by_id
            (id, codigo, nome, email, senha, criado_em, ultimo_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            IF NOT EXISTS
        """
        user_id = insert_with_random_id(
            self.session,
            query,
            lambda entity_id: (entity_id, codigo, nome, email, senha_hash, criado_em, None),
        )

        self.session.execute(
            """
            INSERT INTO usuarios_by_email
            (email, id, codigo, nome, senha, criado_em, ultimo_login)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (email, user_id, codigo, nome, senha_hash, criado_em, None),
        )

        return Usuario(user_id, codigo, nome, email, senha_hash, criado_em, None)

    def update(self, user_id: int, nome: str | None, senha_hash: str | None) -> Usuario | None:
        usuario = self.find_by_id(user_id)
        if not usuario:
            return None

        novo_nome = nome or usuario.nome
        nova_senha = senha_hash or usuario.senha

        self.session.execute(
            "UPDATE usuarios_by_id SET nome = %s, senha = %s WHERE id = %s",
            (novo_nome, nova_senha, user_id),
        )
        self.session.execute(
            "UPDATE usuarios_by_email SET nome = %s, senha = %s WHERE email = %s",
            (novo_nome, nova_senha, usuario.email),
        )
        return self.find_by_id(user_id)

    def delete(self, user_id: int) -> bool:
        usuario = self.find_by_id(user_id)
        if not usuario:
            return False

        self.session.execute("DELETE FROM usuarios_by_id WHERE id = %s", (user_id,))
        self.session.execute("DELETE FROM usuarios_by_email WHERE email = %s", (usuario.email,))
        return True

    def mark_login(self, user_id: int) -> None:
        usuario = self.find_by_id(user_id)
        if not usuario:
            return

        ultimo_login = datetime.now(timezone.utc)
        self.session.execute(
            "UPDATE usuarios_by_id SET ultimo_login = %s WHERE id = %s",
            (ultimo_login, user_id),
        )
        self.session.execute(
            "UPDATE usuarios_by_email SET ultimo_login = %s WHERE email = %s",
            (ultimo_login, usuario.email),
        )

    def _row_to_usuario(self, row) -> Usuario:
        return Usuario(
            id=row.id,
            codigo=row.codigo,
            nome=row.nome,
            email=row.email,
            senha=row.senha,
            criado_em=row.criado_em,
            ultimo_login=row.ultimo_login,
        )
