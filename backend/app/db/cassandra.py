from cassandra.cluster import Cluster, Session
from cassandra.policies import DCAwareRoundRobinPolicy

from app.core.config import get_settings

_cluster: Cluster | None = None
_session: Session | None = None


def get_session() -> Session:
    global _cluster, _session

    if _session is not None:
        return _session

    settings = get_settings()
    _cluster = Cluster(
        contact_points=settings.cassandra_contact_points,
        port=settings.cassandra_port,
        load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=settings.cassandra_datacenter),
    )
    _session = _cluster.connect()
    _session.default_timeout = 10
    return _session


def close_session() -> None:
    global _cluster, _session

    if _session is not None:
        _session.shutdown()
        _session = None

    if _cluster is not None:
        _cluster.shutdown()
        _cluster = None
