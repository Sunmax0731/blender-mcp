from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping


ALLOWED_PRIMITIVES = {
    "CUBE": "primitive_cube_add",
    "UV_SPHERE": "primitive_uv_sphere_add",
    "ICO_SPHERE": "primitive_ico_sphere_add",
    "CYLINDER": "primitive_cylinder_add",
    "CONE": "primitive_cone_add",
    "PLANE": "primitive_plane_add",
}


def execute_command(command: Mapping[str, object], bpy_module) -> dict[str, object]:
    request_id = str(command.get("requestId", ""))
    action = str(command.get("action", ""))
    params = dict(command.get("params", {}) or {})
    requires_confirmation = bool(command.get("requiresConfirmation", False))

    if action == "create_primitive":
        return _create_primitive(request_id=request_id, params=params, bpy_module=bpy_module)
    if action == "list_objects":
        return _list_objects(request_id=request_id, params=params, bpy_module=bpy_module)
    if action == "delete_object":
        if requires_confirmation and not params.get("_approved", False):
            return {
                "success": False,
                "requestId": request_id,
                "executionMode": "confirm_required",
                "error": {
                    "code": "CONFIRMATION_REQUIRED",
                    "message": "Object deletion requires explicit approval.",
                },
                "data": {
                    "targetObjectName": params.get("targetObjectName"),
                },
            }
        return _delete_object(request_id=request_id, params=params, bpy_module=bpy_module)

    return {
        "success": False,
        "requestId": request_id,
        "error": {
            "code": "ACTION_NOT_ALLOWED",
            "message": f"Unsupported action: {action}",
        },
    }


def _create_primitive(*, request_id: str, params: Mapping[str, object], bpy_module) -> dict[str, object]:
    primitive_type = str(params.get("type", "")).upper()
    op_name = ALLOWED_PRIMITIVES.get(primitive_type)
    if op_name is None:
        return _invalid_argument(
            request_id=request_id,
            message=f"Unsupported primitive type: {primitive_type}",
        )

    location = _vector3(params.get("location"), default=(0.0, 0.0, 0.0))
    rotation = _vector3(params.get("rotationEuler"), default=(0.0, 0.0, 0.0))
    scale = _vector3(params.get("scale"), default=(1.0, 1.0, 1.0))

    try:
        getattr(bpy_module.ops.mesh, op_name)(
            location=location,
            rotation=rotation,
            scale=scale,
        )
        active_object = bpy_module.context.active_object
        if active_object is None:
            return _internal_error(request_id=request_id, message="No active object was created.")

        requested_name = params.get("name")
        if isinstance(requested_name, str) and requested_name.strip():
            active_object.name = requested_name.strip()

        return {
            "success": True,
            "requestId": request_id,
            "message": f"{primitive_type} created.",
            "data": {
                "objectName": active_object.name,
                "objectType": getattr(active_object, "type", "UNKNOWN"),
                "createdPrimitiveType": primitive_type,
            },
        }
    except Exception as exc:  # noqa: BLE001
        return _internal_error(request_id=request_id, message=str(exc))


def _list_objects(*, request_id: str, params: Mapping[str, object], bpy_module) -> dict[str, object]:
    name_prefix = params.get("namePrefix")
    selected_only = bool(params.get("selectedOnly", False))
    type_filter = {
        str(item).upper()
        for item in (params.get("typeFilter") or [])
        if isinstance(item, str) and item
    }

    objects = []
    for obj in bpy_module.data.objects:
        if isinstance(name_prefix, str) and name_prefix and not obj.name.startswith(name_prefix):
            continue
        if type_filter and str(getattr(obj, "type", "")).upper() not in type_filter:
            continue
        selected = bool(obj.select_get()) if hasattr(obj, "select_get") else False
        if selected_only and not selected:
            continue
        visible = _object_visible(obj)
        objects.append(
            {
                "name": obj.name,
                "type": getattr(obj, "type", "UNKNOWN"),
                "selected": selected,
                "visible": visible,
            }
        )

    return {
        "success": True,
        "requestId": request_id,
        "data": {
            "objects": objects,
        },
    }


def _delete_object(*, request_id: str, params: Mapping[str, object], bpy_module) -> dict[str, object]:
    target_name = params.get("targetObjectName")
    if not isinstance(target_name, str) or not target_name.strip():
        return _invalid_argument(request_id=request_id, message="targetObjectName is required.")

    obj = _find_object_by_name(bpy_module.data.objects, target_name.strip())
    if obj is None:
        return {
            "success": False,
            "requestId": request_id,
            "error": {
                "code": "INVALID_ARGUMENT",
                "message": f"Object not found: {target_name}",
            },
        }

    try:
        if hasattr(bpy_module.ops.object, "select_all"):
            bpy_module.ops.object.select_all(action="DESELECT")
        if hasattr(obj, "select_set"):
            obj.select_set(True)
        if hasattr(bpy_module.context.view_layer.objects, "active"):
            bpy_module.context.view_layer.objects.active = obj
        bpy_module.ops.object.delete()
        return {
            "success": True,
            "requestId": request_id,
            "message": "Object deleted.",
            "data": {
                "targetObjectName": target_name,
            },
        }
    except Exception as exc:  # noqa: BLE001
        return _internal_error(request_id=request_id, message=str(exc))


def _vector3(value: object, *, default: tuple[float, float, float]) -> tuple[float, float, float]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        return default
    items = list(value)
    if len(items) != 3:
        return default
    try:
        return (float(items[0]), float(items[1]), float(items[2]))
    except (TypeError, ValueError):
        return default


def _object_visible(obj) -> bool:
    if hasattr(obj, "visible_get"):
        try:
            return bool(obj.visible_get())
        except TypeError:
            pass
    if hasattr(obj, "hide_get"):
        return not bool(obj.hide_get())
    return True


def _find_object_by_name(objects, target_name: str):
    getter = getattr(objects, "get", None)
    if callable(getter):
        found = getter(target_name)
        if found is not None:
            return found
    for obj in objects:
        if getattr(obj, "name", None) == target_name:
            return obj
    return None


def _invalid_argument(*, request_id: str, message: str) -> dict[str, object]:
    return {
        "success": False,
        "requestId": request_id,
        "error": {
            "code": "INVALID_ARGUMENT",
            "message": message,
        },
    }


def _internal_error(*, request_id: str, message: str) -> dict[str, object]:
    return {
        "success": False,
        "requestId": request_id,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": message,
        },
    }
