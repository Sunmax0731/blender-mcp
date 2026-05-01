from __future__ import annotations

from pathlib import Path
from urllib import parse
from urllib import request


SUPPORTED_IMPORT_EXTENSIONS = {".glb", ".gltf"}


def sanitize_collection_component(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "generated"


def infer_filename_from_url(url: str, default_stem: str = "generated-model", default_ext: str = ".glb") -> str:
    parsed = parse.urlparse(url)
    candidate = Path(parse.unquote(parsed.path)).name
    if not candidate:
        return f"{default_stem}{default_ext}"

    suffix = Path(candidate).suffix.lower()
    if suffix in SUPPORTED_IMPORT_EXTENSIONS:
        return candidate
    if suffix:
        raise ValueError(f"Unsupported import extension: {suffix}")
    return f"{Path(candidate).stem or default_stem}{default_ext}"


def download_asset(
    url: str,
    *,
    destination_dir: Path,
    filename: str | None = None,
    headers: dict[str, str] | None = None,
    timeout_seconds: float = 60.0,
) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    resolved_name = filename or infer_filename_from_url(url)
    target_path = destination_dir / resolved_name
    req = request.Request(url, headers=headers or {}, method="GET")
    with request.urlopen(req, timeout=timeout_seconds) as response:
        target_path.write_bytes(response.read())
    return target_path


def import_asset_from_url(
    *,
    bpy_module,
    asset_url: str,
    service_key: str,
    collection_name: str,
    download_root: str,
) -> dict[str, object]:
    filename = infer_filename_from_url(asset_url)
    service_dir = Path(download_root) / sanitize_collection_component(service_key)
    downloaded_path = download_asset(asset_url, destination_dir=service_dir, filename=filename)
    return import_local_asset(
        bpy_module=bpy_module,
        file_path=downloaded_path,
        collection_name=collection_name,
    )


def import_local_asset(*, bpy_module, file_path: Path, collection_name: str) -> dict[str, object]:
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_IMPORT_EXTENSIONS:
        raise ValueError(f"Unsupported import extension: {suffix}")

    existing_ids = {obj.as_pointer() for obj in bpy_module.data.objects}
    if suffix in {".glb", ".gltf"}:
        bpy_module.ops.import_scene.gltf(filepath=str(file_path))

    imported_objects = [obj for obj in bpy_module.data.objects if obj.as_pointer() not in existing_ids]
    target_collection = _ensure_collection(bpy_module, collection_name)
    for obj in imported_objects:
        if target_collection not in obj.users_collection:
            target_collection.objects.link(obj)

    return {
        "file_path": str(file_path),
        "collection_name": target_collection.name,
        "object_names": [obj.name for obj in imported_objects],
        "object_count": len(imported_objects),
    }


def _ensure_collection(bpy_module, collection_name: str):
    collections = bpy_module.data.collections
    target = collections.get(collection_name)
    if target is None:
        target = collections.new(collection_name)
        bpy_module.context.scene.collection.children.link(target)
    return target
