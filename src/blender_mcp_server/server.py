from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.routing import Route

from .transport.http_app import addon_command_poll_endpoint
from .transport.http_app import addon_command_result_endpoint
from .transport.http_app import addon_approval_result_endpoint
from .transport.http_app import addon_status_endpoint
from .transport.http_app import ai_suggestion_endpoint
from .transport.http_app import health_endpoint
from .transport.http_app import request_status_endpoint
from .transport.http_app import status_endpoint
from .transport.http_app import tools_endpoint


@dataclass(slots=True)
class ServerApp:
    name: str
    host: str
    port: int
    app: Starlette
    mcp_server: object


def create_server() -> ServerApp:
    host = "127.0.0.1"
    port = 8765
    mcp_server = create_mcp_server()
    app = create_starlette_app(mcp_server)
    return ServerApp(
        name="blender-mcp-server",
        host=host,
        port=port,
        app=app,
        mcp_server=mcp_server,
    )


def create_mcp_server():
    from mcp.server.fastmcp import FastMCP

    from .tools.registry import build_tool_registry

    mcp_server = FastMCP(
        name="Blender MCP",
        stateless_http=True,
        json_response=True,
        streamable_http_path="/",
    )
    tool_registry = build_tool_registry()

    @mcp_server.tool(name="blender_status")
    def blender_status() -> dict[str, object]:
        return tool_registry["blender_status"]()

    @mcp_server.tool(name="blender_get_request_status")
    def blender_get_request_status(request_id: str) -> dict[str, object]:
        return tool_registry["blender_get_request_status"](
            request_id=request_id,
        )

    @mcp_server.tool(name="blender_request_ai_suggestion")
    async def blender_request_ai_suggestion(
        prompt: str,
        selected_objects: list[dict[str, object]] | None = None,
        scene_summary: dict[str, object] | None = None,
        constraints: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return await asyncio.to_thread(
            tool_registry["blender_request_ai_suggestion"],
            prompt=prompt,
            selected_objects=selected_objects,
            scene_summary=scene_summary,
            constraints=constraints,
        )

    @mcp_server.tool(name="blender_create_primitive")
    async def blender_create_primitive(
        primitive_type: str,
        name: str | None = None,
        location: list[float] | None = None,
        rotation_euler: list[float] | None = None,
        scale: list[float] | None = None,
    ) -> dict[str, object]:
        return await asyncio.to_thread(
            tool_registry["blender_create_primitive"],
            primitive_type=primitive_type,
            name=name,
            location=location,
            rotation_euler=rotation_euler,
            scale=scale,
        )

    @mcp_server.tool(name="blender_list_objects")
    async def blender_list_objects(
        name_prefix: str | None = None,
        selected_only: bool = False,
        type_filter: list[str] | None = None,
    ) -> dict[str, object]:
        return await asyncio.to_thread(
            tool_registry["blender_list_objects"],
            name_prefix=name_prefix,
            selected_only=selected_only,
            type_filter=type_filter,
        )

    @mcp_server.tool(name="blender_transform_object")
    async def blender_transform_object(
        target_object_name: str,
        location: list[float] | None = None,
        rotation_euler: list[float] | None = None,
        scale: list[float] | None = None,
        mode: str = "absolute",
    ) -> dict[str, object]:
        return await asyncio.to_thread(
            tool_registry["blender_transform_object"],
            target_object_name=target_object_name,
            location=location,
            rotation_euler=rotation_euler,
            scale=scale,
            mode=mode,
        )

    @mcp_server.tool(name="blender_delete_object")
    async def blender_delete_object(target_object_name: str) -> dict[str, object]:
        return await asyncio.to_thread(
            tool_registry["blender_delete_object"],
            target_object_name=target_object_name,
        )

    return mcp_server


def create_starlette_app(mcp_server) -> Starlette:
    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        async with mcp_server.session_manager.run():
            yield

    return Starlette(
        routes=[
            Route("/health", endpoint=health_endpoint, methods=["GET"]),
            Route("/api/ai/suggest", endpoint=ai_suggestion_endpoint, methods=["POST"]),
            Route("/api/status", endpoint=status_endpoint, methods=["GET"]),
            Route("/api/requests/{request_id:str}", endpoint=request_status_endpoint, methods=["GET"]),
            Route("/api/tools", endpoint=tools_endpoint, methods=["GET"]),
            Route("/api/addon/status", endpoint=addon_status_endpoint, methods=["POST"]),
            Route("/api/addon/command/poll", endpoint=addon_command_poll_endpoint, methods=["POST"]),
            Route(
                "/api/addon/command-result",
                endpoint=addon_command_result_endpoint,
                methods=["POST"],
            ),
            Route(
                "/api/addon/approval-result",
                endpoint=addon_approval_result_endpoint,
                methods=["POST"],
            ),
            Mount("/mcp", app=mcp_server.streamable_http_app()),
        ],
        lifespan=lifespan,
    )
