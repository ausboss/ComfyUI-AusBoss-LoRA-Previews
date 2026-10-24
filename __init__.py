"""LoRA Previews for the AusBoss LoRA Loader.

Adds no nodes. When you click Fetch Civitai info in LoRA Loader, the browser
part of this add-on downloads the LoRA's preview picture from Civitai and the
route below saves it next to the LoRA file.
"""

import asyncio
import logging

from . import previews

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

_log = logging.getLogger("AusBoss LoRA Previews")


def _register_routes():
    try:
        from aiohttp import web
        from server import PromptServer
    except ImportError:
        return
    prompt_server = getattr(PromptServer, "instance", None)
    if prompt_server is None:
        return

    async def run(function, *args):
        return await asyncio.get_running_loop().run_in_executor(None, function, *args)

    @prompt_server.routes.get("/ausboss_previews/has")
    async def has_preview(request):
        try:
            has = await run(previews.has_preview, request.query.get("name", ""))
            return web.json_response({"ok": True, "has": has})
        except Exception as error:
            return web.json_response({"ok": False, "error": previews.safe_message(error)}, status=400)

    @prompt_server.routes.post("/ausboss_previews/save")
    async def save_preview(request):
        try:
            if (request.content_length or 0) > previews.MAX_BYTES:
                raise previews.PreviewError("The picture is too large.")
            data = await request.read()
            await run(previews.save_preview, request.query.get("name", ""), data)
            return web.json_response({"ok": True})
        except Exception as error:
            return web.json_response({"ok": False, "error": previews.safe_message(error)}, status=400)


try:
    _register_routes()
except Exception:  # pragma: no cover - never stop ComfyUI from starting
    _log.exception("LoRA Previews: could not add its routes")
