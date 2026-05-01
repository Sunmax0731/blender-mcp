from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExternalServiceDefinition:
    key: str
    label: str
    default_endpoint: str
    default_mode: str
    requires_api_key: bool
    notes: str
    visible_in_ui: bool = True


SERVICE_DEFINITIONS: tuple[ExternalServiceDefinition, ...] = (
    ExternalServiceDefinition(
        key="meshy",
        label="Meshy",
        default_endpoint="https://api.meshy.ai",
        default_mode="cloud_api",
        requires_api_key=True,
        notes="生成系サービスです。将来は generate / poll / import の共通操作にそろえます。",
    ),
    ExternalServiceDefinition(
        key="tripo",
        label="Tripo AI",
        default_endpoint="https://api.tripo3d.ai/v2/openapi",
        default_mode="cloud_api",
        requires_api_key=True,
        notes="生成系サービスです。将来は generate / poll / import の共通操作にそろえます。",
    ),
    ExternalServiceDefinition(
        key="rodin",
        label="Hyper3D Rodin",
        default_endpoint="https://api.hyper3d.com",
        default_mode="cloud_api",
        requires_api_key=True,
        notes="生成系サービスです。将来は generate / poll / import の共通操作にそろえます。",
    ),
    ExternalServiceDefinition(
        key="spar3d",
        label="Stability API SPAR3D",
        default_endpoint="https://platform.stability.ai/v1/3d/stable-point-aware-3d",
        default_mode="cloud_api",
        requires_api_key=True,
        notes="生成系サービスです。endpoint 差異を吸収できるように明示設定を許容します。",
    ),
    ExternalServiceDefinition(
        key="polyhaven",
        label="Poly Haven",
        default_endpoint="https://api.polyhaven.com",
        default_mode="direct_api",
        requires_api_key=False,
        notes="公開参照系サービスです。search / download / apply の共通操作で扱う想定です。",
        visible_in_ui=False,
    ),
)


VISIBLE_SERVICE_DEFINITIONS: tuple[ExternalServiceDefinition, ...] = tuple(
    definition for definition in SERVICE_DEFINITIONS if definition.visible_in_ui
)


def get_service_definition(service_key: str) -> ExternalServiceDefinition:
    for definition in SERVICE_DEFINITIONS:
        if definition.key == service_key:
            return definition
    raise KeyError(f"Unknown external service key: {service_key}")
