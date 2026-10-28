"""Construct entity identifiers within a caller-owned export namespace."""

import hashlib
import json
import re
from urllib.parse import quote

from rdflib import URIRef


def entity_iri(namespace: str, kind: str, *keys: str) -> URIRef:
    """Separate entity kinds and hash ordered keys without joining collisions.

    The caller supplies a producer namespace or a persisted, randomly allocated
    export namespace. Content fingerprints alone do not identify the producer.
    """
    namespace = str(namespace)
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", namespace) or re.search(r'[\s<>"{}|\\^`]', namespace):
        raise ValueError("namespace must be an absolute IRI without whitespace or forbidden characters")
    if not isinstance(kind, str) or not kind or not keys or any(not isinstance(key, str) or not key for key in keys):
        raise ValueError("kind and identity keys must be non-empty strings")
    payload = json.dumps(list(keys), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    checksum = hashlib.sha256(payload).hexdigest()
    separator = "" if namespace.endswith(("/", "#", ":")) else "/"
    return URIRef(f"{namespace}{separator}{quote(kind, safe='')}/{checksum}")
