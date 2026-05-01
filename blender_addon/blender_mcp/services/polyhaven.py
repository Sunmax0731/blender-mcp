from __future__ import annotations

import json
from urllib import parse
from urllib import request


POLYHAVEN_USER_AGENT = "blender-mcp-polyhaven/1.1.0"
POLYHAVEN_TYPES = {"all", "hdris", "textures", "models"}
POLYHAVEN_TYPE_LABELS = {0: "hdris", 1: "textures", 2: "models"}


def _build_url(base_url: str, path: str, params: dict[str, str] | None = None) -> str:
    query = f"?{parse.urlencode(params)}" if params else ""
    return f"{base_url.rstrip('/')}{path}{query}"


def _fetch_json(base_url: str, path: str, params: dict[str, str] | None = None) -> dict[str, object]:
    req = request.Request(
        _build_url(base_url, path, params),
        headers={"User-Agent": POLYHAVEN_USER_AGENT},
        method="GET",
    )
    with request.urlopen(req, timeout=15.0) as response:
        return json.loads(response.read().decode("utf-8"))


def search_assets(
    *,
    base_url: str,
    asset_type: str,
    query_text: str = "",
    category_text: str = "",
    limit: int = 20,
) -> dict[str, object]:
    normalized_type = asset_type if asset_type in POLYHAVEN_TYPES else "all"
    params: dict[str, str] = {}
    if normalized_type != "all":
        params["type"] = normalized_type
    if category_text.strip():
        params["categories"] = category_text.strip()

    assets_payload = _fetch_json(base_url, "/assets", params)
    query = query_text.strip().lower()

    filtered_assets: list[dict[str, object]] = []
    for asset_id, raw_asset in assets_payload.items():
        name = str(raw_asset.get("name", asset_id))
        categories = [str(item) for item in raw_asset.get("categories", [])]
        tags = [str(item) for item in raw_asset.get("tags", [])]
        raw_type = raw_asset.get("type", normalized_type)
        asset_type_label = POLYHAVEN_TYPE_LABELS.get(raw_type, str(raw_type))
        haystacks = [asset_id.lower(), name.lower(), " ".join(categories).lower(), " ".join(tags).lower()]
        if query and not any(query in item for item in haystacks):
            continue
        filtered_assets.append(
            {
                "id": asset_id,
                "name": name,
                "type": asset_type_label,
                "categories": categories,
                "downloads": int(raw_asset.get("download_count", 0) or 0),
                "url": f"https://polyhaven.com/a/{asset_id}",
            }
        )

    filtered_assets.sort(key=lambda item: (-int(item["downloads"]), str(item["name"])))
    return {
        "asset_type": normalized_type,
        "query": query_text.strip(),
        "category": category_text.strip(),
        "total_count": len(filtered_assets),
        "returned_count": min(len(filtered_assets), limit),
        "assets": filtered_assets[:limit],
    }


def format_search_results(payload: dict[str, object]) -> str:
    lines = [
        f"Poly Haven search: type={payload['asset_type']} query={payload['query'] or '-'} category={payload['category'] or '-'}",
        f"Found {payload['total_count']} assets, showing {payload['returned_count']}.",
    ]
    assets = payload.get("assets", [])
    if not assets:
        lines.append("No assets matched the current filters.")
        return "\n".join(lines)

    for asset in assets:
        categories = ", ".join(asset["categories"]) if asset["categories"] else "-"
        lines.append(
            f"- {asset['name']} ({asset['id']}) [{asset['type']}] downloads={asset['downloads']} categories={categories}"
        )
    return "\n".join(lines)
