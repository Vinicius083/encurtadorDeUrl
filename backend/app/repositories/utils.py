import secrets

from cassandra.cluster import Session


def generate_int_id() -> int:
    return secrets.randbelow(2_000_000_000) + 1


def insert_with_random_id(
    session: Session,
    query: str,
    params_factory,
    max_attempts: int = 8,
) -> int:
    for _ in range(max_attempts):
        entity_id = generate_int_id()
        result = session.execute(query, params_factory(entity_id))
        if result.one().applied:
            return entity_id

    raise RuntimeError("Nao foi possivel gerar um id unico.")
