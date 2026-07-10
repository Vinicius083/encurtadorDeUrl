from cassandra.cluster import Session

from app.core.config import get_settings


def init_schema(session: Session) -> None:
    settings = get_settings()

    session.execute(
        f"""
        CREATE KEYSPACE IF NOT EXISTS {settings.cassandra_keyspace}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
        """
    )
    session.set_keyspace(settings.cassandra_keyspace)

    session.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios_by_id (
          id int PRIMARY KEY,
          codigo text,
          nome text,
          email text,
          senha text,
          criado_em timestamp,
          ultimo_login timestamp
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios_by_email (
          email text PRIMARY KEY,
          id int,
          codigo text,
          nome text,
          senha text,
          criado_em timestamp,
          ultimo_login timestamp
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS urls_by_codigo (
          codigo text PRIMARY KEY,
          url_original text,
          usuario_id int,
          criado_em timestamp,
          atualizado_em timestamp,
          desabilitado boolean,
          data_expiracao timestamp,
          qr_code text
        )
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS urls_by_usuario (
          usuario_id int,
          criado_em timestamp,
          codigo text,
          url_original text,
          atualizado_em timestamp,
          desabilitado boolean,
          data_expiracao timestamp,
          qr_code text,
          PRIMARY KEY ((usuario_id), criado_em, codigo)
        ) WITH CLUSTERING ORDER BY (criado_em DESC)
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS acessos_url_encurtada (
          codigo text,
          dia date,
          id int,
          acessado_em timestamp,
          PRIMARY KEY ((codigo), dia, id)
        ) WITH CLUSTERING ORDER BY (dia DESC, id DESC)
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS url_access_counters (
          codigo text PRIMARY KEY,
          access_count counter
        )
        """
    )
