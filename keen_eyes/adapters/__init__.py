from .base import AdapterRegistry, EvidenceAdapter
from .cyclonedx import CycloneDxAdapter
from .junit import JUnitAdapter
from .k6 import K6Adapter
from .osv import OsvAdapter
from .sarif import SarifAdapter


def default_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(JUnitAdapter())
    registry.register(SarifAdapter())
    registry.register(K6Adapter())
    registry.register(OsvAdapter())
    registry.register(CycloneDxAdapter())
    return registry


__all__ = [
    "AdapterRegistry",
    "EvidenceAdapter",
    "CycloneDxAdapter",
    "JUnitAdapter",
    "K6Adapter",
    "OsvAdapter",
    "SarifAdapter",
    "default_registry",
]

