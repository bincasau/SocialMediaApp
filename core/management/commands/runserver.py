from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand

import uvicorn


class Command(BaseCommand):
    help = "Run the ASGI app via Uvicorn (HTTP + WebSocket)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "addrport",
            nargs="?",
            default="127.0.0.1:8000",
            help="Optional host:port (default: 127.0.0.1:8000)",
        )
        parser.add_argument(
            "--noreload",
            action="store_true",
            help="Disable auto-reload.",
        )

    def handle(self, *args, **options) -> None:
        addrport = options["addrport"]
        host, port = self._parse_addrport(addrport)
        app_path = self._get_asgi_app_path()

        uvicorn.run(
            app_path,
            host=host,
            port=port,
            reload=not options["noreload"],
        )

    def _get_asgi_app_path(self) -> str:
        asgi_app = getattr(settings, "ASGI_APPLICATION", None)
        if asgi_app:
            module, app = asgi_app.rsplit(".", 1)
            return f"{module}:{app}"
        return "SocialMediaApp.asgi:application"

    def _parse_addrport(self, addrport: str) -> tuple[str, int]:
        if ":" in addrport:
            host, port_str = addrport.rsplit(":", 1)
            return host or "127.0.0.1", int(port_str)
        if addrport.isdigit():
            return "127.0.0.1", int(addrport)
        return "127.0.0.1", 8000
