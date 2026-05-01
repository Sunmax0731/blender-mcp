"""One-click installer app for official Blender MCP integration."""

from .plugins import ThirdPartyPlugin, load_third_party_plugins
from .runner import InstallerRunner, InstallerStep, default_steps

__all__ = [
    "InstallerRunner",
    "InstallerStep",
    "ThirdPartyPlugin",
    "default_steps",
    "load_third_party_plugins",
]
