import os
from mcp.server import Server, stdio_server
from .browser import BrowserManager
from .tools import BASE_TOOLS
from .tools.captcha import captcha_solve_tool, captcha_report_tool, handle_solve, handle_report, init_solver


class SessionContext:
    def __init__(self, context):
        self.context = context
        self._current_page = None

    async def get_page(self):
        if self._current_page is None or self._current_page.is_closed():
            pages = self.context.pages
            if pages:
                self._current_page = pages[0]
            else:
                self._current_page = await self.context.new_page()
        return self._current_page


def create_server(args):
    server = Server("browser-mcp")

    registry = dict(BASE_TOOLS)

    if args.captcha_api_key:
        init_solver(args.captcha_api_key)
        registry["captcha_solve"] = (captcha_solve_tool, handle_solve)
        registry["captcha_report"] = (captcha_report_tool, handle_report)

    @server.list_tools()
    async def list_tools():
        return [info for info, _ in registry.values()]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name not in registry:
            raise ValueError(f"Unknown tool: {name}")

        bm = await BrowserManager.get_instance(args)
        session_id = server.request_context.session_id
        ctx = await bm.get_context(session_id)
        session_ctx = SessionContext(ctx)

        _, handler = registry[name]
        result = await handler(session_ctx, **arguments)
        return result

    return server
