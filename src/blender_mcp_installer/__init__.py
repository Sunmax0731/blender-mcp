"""One-click installer app for official Blender MCP integration."""

from .runner import InstallerRunner, InstallerStep, default_steps

__all__ = ["InstallerRunner", "InstallerStep", "default_steps"]
